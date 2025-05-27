from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, models, auth
from app.database import SessionLocal

router = APIRouter(prefix="/apoderado", tags=["Apoderado"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/estudiantes", response_model=schemas.EstudianteResponse)
def registrar_estudiante(
    estudiante: schemas.EstudianteBase,
    usuario_actual: models.Usuario = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    # Validar tipo de usuario
    auth.verificar_tipo_usuario(usuario_actual, "apoderado")

    # Obtener id_apoderado desde relación
    apoderado = db.query(models.Apoderado).filter(models.Apoderado.id_usuario == usuario_actual.id_usuario).first()

    if not apoderado:
        raise HTTPException(status_code=404, detail="Apoderado no encontrado")

    nuevo_estudiante = models.Estudiante(
        nombre=estudiante.nombre,
        edad=estudiante.edad,
        direccion=estudiante.direccion,
        latitud=estudiante.latitud,
        longitud=estudiante.longitud,
        id_apoderado=apoderado.id_apoderado
    )

    db.add(nuevo_estudiante)
    db.commit()
    db.refresh(nuevo_estudiante)

    return nuevo_estudiante
@router.get("/estudiantes", response_model=list[schemas.EstudianteResponse])
def obtener_estudiantes(
    usuario_actual: models.Usuario = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    auth.verificar_tipo_usuario(usuario_actual, "apoderado")

    apoderado = db.query(models.Apoderado).filter(models.Apoderado.id_usuario == usuario_actual.id_usuario).first()
    if not apoderado:
        raise HTTPException(status_code=404, detail="Apoderado no encontrado")

    return apoderado.estudiantes

@router.delete("/estudiantes/{id_estudiante}", status_code=204)
def eliminar_estudiante(
    id_estudiante: int,
    usuario_actual: models.Usuario = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    auth.verificar_tipo_usuario(usuario_actual, "apoderado")

    estudiante = db.query(models.Estudiante).join(models.Apoderado).filter(
        models.Estudiante.id_estudiante == id_estudiante,
        models.Apoderado.id_usuario == usuario_actual.id_usuario
    ).first()

    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado o no autorizado")

    db.delete(estudiante)
    db.commit()
    return


@router.put("/estudiantes/{id_estudiante}", response_model=schemas.EstudianteResponse)
def actualizar_estudiante(
    id_estudiante: int,
    datos_actualizados: schemas.EstudianteUpdate,
    usuario_actual: models.Usuario = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    auth.verificar_tipo_usuario(usuario_actual, "apoderado")

    estudiante = db.query(models.Estudiante).join(models.Apoderado).filter(
        models.Estudiante.id_estudiante == id_estudiante,
        models.Apoderado.id_usuario == usuario_actual.id_usuario
    ).first()

    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado o no autorizado")

    for campo, valor in datos_actualizados.dict(exclude_unset=True).items():
        setattr(estudiante, campo, valor)

    db.commit()
    db.refresh(estudiante)
    return estudiante


@router.get("/vinculaciones", response_model=list[schemas.ConductorVinculado])
def obtener_conductores_vinculados(
    usuario_actual: models.Usuario = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    auth.verificar_tipo_usuario(usuario_actual, "apoderado")

    apoderado = db.query(models.Apoderado).filter(
        models.Apoderado.id_usuario == usuario_actual.id_usuario
    ).first()

    if not apoderado:
        raise HTTPException(status_code=404, detail="Apoderado no encontrado")

    conductores_vinculados = []
    for vinculo in apoderado.vinculaciones:
        conductor = vinculo.conductor
        usuario_conductor = conductor.usuario
        conductores_vinculados.append(schemas.ConductorVinculado(
            id_conductor=conductor.id_conductor,
            nombre=usuario_conductor.nombre,
            telefono=usuario_conductor.telefono,
            patente=conductor.patente,
            modelo_vehiculo=conductor.modelo_vehiculo,
            codigo_vinculacion=conductor.codigo_vinculacion
        ))

    return conductores_vinculados


@router.post("/vincular", status_code=201)
def vincular_conductor(
    datos: schemas.VinculacionRequest,
    usuario_actual: models.Usuario = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    auth.verificar_tipo_usuario(usuario_actual, "apoderado")

    apoderado = db.query(models.Apoderado).filter(
        models.Apoderado.id_usuario == usuario_actual.id_usuario
    ).first()

    if not apoderado:
        raise HTTPException(status_code=404, detail="Apoderado no encontrado")

    conductor = db.query(models.Conductor).filter(
        models.Conductor.codigo_vinculacion == datos.codigo_vinculacion
    ).first()

    if not conductor:
        raise HTTPException(status_code=404, detail="Código de vinculación inválido")

    # Verificar si ya está vinculado
    ya_vinculado = db.query(models.Vinculo).filter_by(
        id_apoderado=apoderado.id_apoderado,
        id_conductor=conductor.id_conductor
    ).first()

    if ya_vinculado:
        raise HTTPException(status_code=409, detail="Ya estás vinculado con este conductor")

    nuevo_vinculo = models.Vinculo(
        id_apoderado=apoderado.id_apoderado,
        id_conductor=conductor.id_conductor
    )
    db.add(nuevo_vinculo)
    db.commit()
    return {"mensaje": "Vinculación exitosa con el conductor"}

@router.put("/estudiantes/{id_estudiante}/asignar-conductor", response_model=schemas.EstudianteResponse)
def asignar_conductor_a_estudiante(
    id_estudiante: int,
    conductor_id: int,
    usuario_actual: models.Usuario = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    auth.verificar_tipo_usuario(usuario_actual, "apoderado")

    estudiante = db.query(models.Estudiante).join(models.Apoderado).filter(
        models.Estudiante.id_estudiante == id_estudiante,
        models.Apoderado.id_usuario == usuario_actual.id_usuario
    ).first()

    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado o no autorizado")

    conductor = db.query(models.Conductor).filter(models.Conductor.id_conductor == conductor_id).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    estudiante.id_conductor = conductor.id_conductor
    db.commit()
    db.refresh(estudiante)
    return estudiante
