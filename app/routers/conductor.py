from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Usuario, Conductor
from app.auth import get_current_user, verificar_admin, verificar_tipo_usuario
from app import models, schemas
from typing import List
from datetime import date, datetime

router = APIRouter(
    prefix="/conductor",
    tags=["Conductor"]
)

@router.get("/me", response_model=schemas.ConductorCompleto)
def obtener_mi_info_conductor(
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    if usuario_actual.tipo_usuario != "conductor":
        raise HTTPException(status_code=403, detail="Solo los conductores pueden acceder a esta información.")

    conductor = db.query(models.Conductor).filter_by(id_usuario=usuario_actual.id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="No se encontró un conductor vinculado a este usuario.")

    usuario_schema = schemas.UsuarioResponse(
        id_usuario=usuario_actual.id_usuario,
        nombre=usuario_actual.nombre,
        email=usuario_actual.email,
        telefono=usuario_actual.telefono,
        tipo_usuario=usuario_actual.tipo_usuario
    )

    datos_conductor_schema = schemas.ConductorCreateDatos(
        patente=conductor.patente,
        modelo_vehiculo=conductor.modelo_vehiculo,
        casa= conductor.casa,
        lat_casa=conductor.lat_casa,
        long_casa=conductor.long_casa
    )
    
    return schemas.ConductorCompleto(
        usuario=usuario_schema,
        datos_conductor=datos_conductor_schema
    )
    
    
@router.get("/mis-estudiantes", response_model=List[schemas.EstudianteResponse])
def obtener_estudiantes_conductor(
    usuario_actual: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if usuario_actual.tipo_usuario != "conductor":
        raise HTTPException(status_code=403, detail="Solo los conductores pueden acceder a esta información.")

    conductor = db.query(models.Conductor).filter_by(id_usuario=usuario_actual.id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="No se encontró conductor para este usuario.")

    estudiantes = db.query(models.Estudiante).filter_by(id_conductor=conductor.id_conductor).all()

    return estudiantes


@router.get("/mis-estudiantes-hoy", response_model=List[schemas.EstudianteConAsistenciaHoy])
def listar_estudiantes_con_asistencia_hoy(
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    if usuario_actual.tipo_usuario != "conductor":
        raise HTTPException(status_code=403, detail="Solo los conductores pueden acceder a esta información.")

    conductor = db.query(models.Conductor).filter_by(id_usuario=usuario_actual.id_usuario).first()

    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado.")

    estudiantes = conductor.estudiantes
    resultado = []

    for est in estudiantes:
        asistencia_hoy = db.query(models.Asistencia).filter_by(
            fecha=date.today()
        ).first()

        resultado.append(schemas.EstudianteConAsistenciaHoy(
            id_estudiante=est.id_estudiante,
            nombre=est.nombre,
            curso=est.curso,
            colegio=est.colegio,
            asistencia=asistencia_hoy
        ))

    return resultado



@router.get("/ruta-dia/conductor", response_model=schemas.RutaConParadasResponse)
def ver_ultima_ruta_del_dia_del_conductor(
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)):
    
    if usuario_actual.tipo_usuario != "conductor" :
        raise HTTPException(status_code=403, detail="Acceso restringido a conductores")
    hoy = date.today()

    # Obtener el conductor asociado al usuario actual
    conductor = db.query(models.Conductor).filter_by(id_usuario=usuario_actual.id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    # Obtener la última ruta del día para ese conductor (opcionalmente podrías ordenar por hora_inicio si existiera)
    ruta = (
        db.query(models.Ruta)
        .filter_by(id_conductor=conductor.id_conductor, fecha=hoy)
        .order_by(models.Ruta.id_ruta.desc())  # última en caso de múltiples
        .first()
    )

    if not ruta:
        raise HTTPException(status_code=404, detail="No se encontró una ruta para hoy.")

    return ruta


@router.post("/generar-ruta-dia", response_model=schemas.RutaConParadasResponse)
def generar_ruta_dia(
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    if usuario_actual.tipo_usuario != "conductor":
        raise HTTPException(status_code=403, detail="No autorizado")

    conductor = db.query(models.Conductor).filter_by(id_usuario=usuario_actual.id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no registrado")

    # Verificar que no exista una ruta activa actual
    ruta_activa = db.query(models.Ruta).filter(
        models.Ruta.id_conductor == conductor.id_conductor,
        models.Ruta.estado == "activa"
    ).first()

    if ruta_activa:
        raise HTTPException(status_code=400, detail="Ya existe una ruta activa. Debe finalizarla antes de generar una nueva.")

    # Buscar la ruta fija del conductor
    ruta_fija = db.query(models.RutaFija).filter_by(id_conductor=conductor.id_conductor).first()
    if not ruta_fija:
        raise HTTPException(status_code=404, detail="Ruta fija no encontrada")

    # Obtener estudiantes con asistencia registrada para hoy
    asistencias_hoy = db.query(models.Asistencia).filter_by(
        fecha=date.today(),
        asiste=True
    ).all()

    ids_presentes = {a.id_estudiante for a in asistencias_hoy}

    # Generar paradas solo para los estudiantes que están en la ruta fija y están presentes hoy
    paradas_creadas = []
    orden = 1
    for parada_fija in sorted(ruta_fija.paradas, key=lambda x: x.orden):
        estudiante = parada_fija.estudiante
        if estudiante.id_estudiante in ids_presentes:
            parada = models.Parada(
                id_estudiante=estudiante.id_estudiante,
                orden=orden,
                latitud=estudiante.lat_casa,
                longitud=estudiante.long_casa,
                recogido=False,
                entregado=False
            )
            paradas_creadas.append(parada)
            orden += 1

    if not paradas_creadas:
        raise HTTPException(status_code=400, detail="No hay estudiantes con asistencia para hoy en la ruta fija")

    # Crear nueva ruta del día
    nueva_ruta = models.Ruta(
        id_conductor=conductor.id_conductor,
        fecha=date.today(),
        estado="activa",
        hora_inicio=datetime.now().time(),
        paradas=paradas_creadas
    )

    db.add(nueva_ruta)
    db.commit()
    db.refresh(nueva_ruta)

    return nueva_ruta


@router.put("/finalizar-ruta-dia")
def finalizar_ruta_dia(
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    if usuario_actual.tipo_usuario != "conductor":
        raise HTTPException(status_code=403, detail="No autorizado")

    # Obtener al conductor desde el usuario
    conductor = db.query(models.Conductor).filter_by(id_usuario=usuario_actual.id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    # Buscar la ruta activa actual
    ruta = db.query(models.Ruta).filter_by(
        id_conductor=conductor.id_conductor,
        estado="activa"
    ).first()

    if not ruta:
        raise HTTPException(status_code=404, detail="No hay una ruta activa para finalizar")

    ruta.estado = "finalizada"
    ruta.hora_fin = datetime.now().time()
    db.commit()

    return {"mensaje": "Ruta finalizada exitosamente"}
