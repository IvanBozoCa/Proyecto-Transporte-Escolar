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
        modelo_vehiculo=conductor.modelo_vehiculo
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
            id_estudiante=est.id_estudiante,
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


@router.get("/asistencias-hoy", response_model=List[schemas.EstudianteConAsistencias])
def obtener_estudiantes_presentes_hoy(
    usuario_actual: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if usuario_actual.tipo_usuario != "conductor" :
        raise HTTPException(status_code=403, detail="Acceso restringido a conductores")

    conductor = db.query(models.Conductor).filter_by(id_usuario=usuario_actual.id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    estudiantes = db.query(models.Estudiante).filter_by(id_conductor=conductor.id_conductor).all()

    estudiantes_presentes = []
    hoy = date.today()

    for est in estudiantes:
        asistencia = db.query(models.Asistencia).filter_by(
            id_estudiante=est.id_estudiante,
            fecha=hoy,
            asiste=True
        ).first()

        if asistencia:
            estudiantes_presentes.append(schemas.EstudianteConAsistencias(
                id_estudiante=est.id_estudiante,
                nombre=est.nombre,
                curso=est.curso,
                colegio=est.colegio,
                asistencias=[schemas.AsistenciaResponse.from_orm(asistencia)]
            ))

    return estudiantes_presentes

@router.post("/ruta-dia/generar", response_model=schemas.RutaResponse)
def generar_ruta_dia_conductor(
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    if usuario_actual.tipo_usuario != "conductor" :
        raise HTTPException(status_code=403, detail="Acceso restringido a conductores")

    hoy = date.today()

    # Obtener el conductor asociado al usuario actual
    conductor = db.query(models.Conductor).filter_by(id_usuario=usuario_actual.id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    # Verificar si ya existe una ruta para hoy
    ruta_existente = db.query(models.Ruta).filter_by(id_conductor=conductor.id_conductor, fecha=hoy).first()
    if ruta_existente:
        raise HTTPException(status_code=400, detail="Ya existe una ruta del día para este conductor.")

    # Buscar ruta fija del conductor
    ruta_fija = db.query(models.RutaFija).filter_by(id_conductor=conductor.id_conductor).first()
    if not ruta_fija:
        raise HTTPException(status_code=404, detail="No hay una ruta fija asignada a este conductor.")

    # Obtener IDs de estudiantes con asistencia positiva hoy
    asistencias_hoy = db.query(models.Asistencia).filter_by(fecha=hoy, asiste=True).all()
    ids_presentes = {asistencia.id_estudiante for asistencia in asistencias_hoy}

    # Filtrar paradas de la ruta fija cuyos estudiantes están presentes
    paradas_presentes = [
        parada for parada in ruta_fija.paradas if parada.id_estudiante in ids_presentes
    ]

    if not paradas_presentes:
        raise HTTPException(status_code=400, detail="No hay estudiantes presentes para hoy.")

    # Crear la ruta del día
    nueva_ruta = models.Ruta(
        id_conductor=conductor.id_conductor,
        fecha=hoy,
        estado="activa",
        hora_inicio=datetime.now().time()
    )
    db.add(nueva_ruta)
    db.commit()
    db.refresh(nueva_ruta)

    # Agregar paradas a la nueva ruta
    for parada_fija in paradas_presentes:
        estudiante = parada_fija.estudiante
        nueva_parada = models.Parada(
            id_ruta=nueva_ruta.id_ruta,
            id_estudiante=estudiante.id_estudiante,
            orden=parada_fija.orden,
            latitud=estudiante.latitud,
            longitud=estudiante.longitud
        )
        db.add(nueva_parada)

    db.commit()
    db.refresh(nueva_ruta)

    return nueva_ruta


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
