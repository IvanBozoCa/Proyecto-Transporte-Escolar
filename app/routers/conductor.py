from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, auth
from app.database import get_db
from sqlalchemy.orm import joinedload
from fastapi import Query
from datetime import date
router = APIRouter(prefix="/conductor", tags=["Conductor"])

@router.get("/me", response_model=schemas.ConductorInfo)
def obtener_conductor_actual(
    usuario_actual: models.Usuario = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    auth.verificar_tipo_usuario(usuario_actual, "conductor")

    conductor = db.query(models.Conductor).filter(
        models.Conductor.id_usuario == usuario_actual.id_usuario
    ).first()

    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    return conductor

@router.put("/", response_model=schemas.ConductorInfo)
def actualizar_conductor(
    datos: schemas.ConductorUpdate,
    usuario_actual: models.Usuario = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    auth.verificar_tipo_usuario(usuario_actual, "conductor")

    conductor = db.query(models.Conductor).filter(
        models.Conductor.id_usuario == usuario_actual.id_usuario
    ).first()

    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    for campo, valor in datos.dict(exclude_unset=True).items():
        setattr(conductor, campo, valor)

    db.commit()
    db.refresh(conductor)
    return conductor

@router.get("/vinculados", response_model=list[schemas.ApoderadoVinculado])
def obtener_apoderados_vinculados(
    usuario_actual: models.Usuario = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    auth.verificar_tipo_usuario(usuario_actual, "conductor")

    conductor = db.query(models.Conductor).filter(
        models.Conductor.id_usuario == usuario_actual.id_usuario
    ).first()

    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    apoderados_vinculados = []
    for vinculo in conductor.vinculaciones:
        apoderado = vinculo.apoderado
        usuario_apoderado = apoderado.usuario
        apoderados_vinculados.append(schemas.ApoderadoVinculado(
            id_apoderado=apoderado.id_apoderado,
            nombre=usuario_apoderado.nombre,
            telefono=usuario_apoderado.telefono,
            email=usuario_apoderado.email
        ))

    return apoderados_vinculados

@router.get("/estudiantes", response_model=list[schemas.EstudianteResponse])
def obtener_estudiantes_asignados(
    usuario_actual: models.Usuario = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    auth.verificar_tipo_usuario(usuario_actual, "conductor")

    conductor = db.query(models.Conductor).filter(
        models.Conductor.id_usuario == usuario_actual.id_usuario
    ).first()

    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    return conductor.estudiantes

#===RUTA===
@router.post("/rutas", response_model=schemas.RutaResponse)
def crear_ruta_con_paradas(
    datos: schemas.RutaCreate,
    usuario_actual: models.Usuario = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    auth.verificar_tipo_usuario(usuario_actual, "conductor")

    conductor = db.query(models.Conductor).filter(
        models.Conductor.id_usuario == usuario_actual.id_usuario
    ).first()

    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    # Crear la ruta
    nueva_ruta = models.Ruta(
        fecha=datos.fecha,
        hora_inicio=datos.hora_inicio,
        id_conductor=conductor.id_conductor,
        id_acompanante=datos.id_acompanante
    )
    db.add(nueva_ruta)
    db.commit()
    db.refresh(nueva_ruta)

    # Obtener estudiantes asignados al conductor
    estudiantes = db.query(models.Estudiante).filter(
        models.Estudiante.id_conductor == conductor.id_conductor
    ).all()

    # (Futuro) excluir estudiantes ausentes en datos.fecha

    # Crear una parada por estudiante
    for orden, estudiante in enumerate(estudiantes, start=1):
        parada = models.Parada(
            latitud=estudiante.latitud,
            longitud=estudiante.longitud,
            orden=orden,
            recogido=False,
            entregado=False,
            id_ruta=nueva_ruta.id_ruta,
            id_estudiante=estudiante.id_estudiante
        )
        db.add(parada)

    db.commit()
    db.refresh(nueva_ruta)
    return nueva_ruta

@router.get("/rutas/porfechas", response_model=list[schemas.RutaResponse])
def obtener_rutas_por_fecha(
    fecha: date = Query(..., description="Fecha de las rutas (YYYY-MM-DD)"),
    usuario_actual: models.Usuario = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    auth.verificar_tipo_usuario(usuario_actual, "conductor")

    conductor = db.query(models.Conductor).filter(
        models.Conductor.id_usuario == usuario_actual.id_usuario
    ).first()

    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    rutas = db.query(models.Ruta).options(joinedload(models.Ruta.paradas)).filter(
        models.Ruta.id_conductor == conductor.id_conductor,
        models.Ruta.fecha == fecha
    ).all()

    return rutas

@router.get("/rutas/porsemana", response_model=list[schemas.RutaResponse])
def obtener_rutas_por_semana(
    inicio: date = Query(..., description="Fecha inicio del rango (YYYY-MM-DD)"),
    fin: date = Query(..., description="Fecha fin del rango (YYYY-MM-DD)"),
    usuario_actual: models.Usuario = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    auth.verificar_tipo_usuario(usuario_actual, "conductor")

    if fin < inicio:
        raise HTTPException(status_code=400, detail="La fecha de fin no puede ser menor que la de inicio")

    conductor = db.query(models.Conductor).filter(
        models.Conductor.id_usuario == usuario_actual.id_usuario
    ).first()

    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    rutas = db.query(models.Ruta).options(joinedload(models.Ruta.paradas)).filter(
        models.Ruta.id_conductor == conductor.id_conductor,
        models.Ruta.fecha >= inicio,
        models.Ruta.fecha <= fin
    ).order_by(models.Ruta.fecha).all()

    return rutas

@router.get("/rutas/{id_ruta}", response_model=schemas.RutaResponse)
def obtener_ruta_por_id(
    id_ruta: int,
    usuario_actual: models.Usuario = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    auth.verificar_tipo_usuario(usuario_actual, "conductor")

    ruta = db.query(models.Ruta).options(joinedload(models.Ruta.paradas)).filter(
        models.Ruta.id_ruta == id_ruta
    ).first()

    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")

    # Validación de seguridad: solo el conductor dueño puede ver
    if ruta.id_conductor != usuario_actual.conductor.id_conductor:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta ruta")

    return ruta

@router.post("/paradas/marcar", response_model=schemas.ParadaResponse)
def marcar_asistencia(
    datos: schemas.MarcarAsistenciaRequest,
    usuario_actual: models.Usuario = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    auth.verificar_tipo_usuario(usuario_actual, "conductor")

    # Validar que la ruta es del conductor autenticado
    ruta = db.query(models.Ruta).filter(
        models.Ruta.id_ruta == datos.id_ruta,
        models.Ruta.id_conductor == usuario_actual.conductor.id_conductor
    ).first()

    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada o no autorizada")

    # Buscar la parada del estudiante en esa ruta
    parada = db.query(models.Parada).filter(
        models.Parada.id_ruta == ruta.id_ruta,
        models.Parada.id_estudiante == datos.id_estudiante
    ).first()

    if not parada:
        raise HTTPException(status_code=404, detail="Parada no encontrada para este estudiante en la ruta")

    if datos.accion == "recogido":
        if parada.recogido:
            raise HTTPException(status_code=409, detail="El estudiante ya fue marcado como recogido")
        parada.recogido = True

    elif datos.accion == "entregado":
        if parada.entregado:
            raise HTTPException(status_code=409, detail="El estudiante ya fue marcado como entregado")
        parada.entregado = True

    db.commit()
    db.refresh(parada)
    return parada

@router.post("/paradas/desmarcar", response_model=schemas.ParadaResponse)
def desmarcar_asistencia(
    datos: schemas.MarcarAsistenciaRequest,
    usuario_actual: models.Usuario = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    auth.verificar_tipo_usuario(usuario_actual, "conductor")

    ruta = db.query(models.Ruta).filter(
        models.Ruta.id_ruta == datos.id_ruta,
        models.Ruta.id_conductor == usuario_actual.conductor.id_conductor
    ).first()

    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada o no autorizada")

    parada = db.query(models.Parada).filter(
        models.Parada.id_ruta == ruta.id_ruta,
        models.Parada.id_estudiante == datos.id_estudiante
    ).first()

    if not parada:
        raise HTTPException(status_code=404, detail="Parada no encontrada para este estudiante en la ruta")

    if datos.accion == "recogido":
        parada.recogido = False
    elif datos.accion == "entregado":
        parada.entregado = False

    db.commit()
    db.refresh(parada)
    return parada