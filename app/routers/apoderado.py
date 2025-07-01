from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Usuario, Conductor, Asistencia
from app.auth import get_current_user, verificar_admin, verificar_tipo_usuario
from app import models, schemas
from typing import List
from datetime import date
from fastapi.responses import JSONResponse
from typing import Union

router = APIRouter(
    prefix="/apoderado",
    tags=["Apoderado"]
)
@router.get("/perfil", response_model=schemas.ApoderadoResponse)
def obtener_mi_perfil_completo(
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    if usuario_actual.tipo_usuario != "apoderado":
        raise HTTPException(status_code=403, detail="Solo los apoderados pueden acceder a este perfil")

    apoderado = db.query(models.Apoderado).filter_by(id_usuario=usuario_actual.id_usuario).first()
    if not apoderado:
        raise HTTPException(status_code=404, detail="Apoderado no encontrado")

    estudiantes = db.query(models.Estudiante).filter_by(id_apoderado=apoderado.id_apoderado).all()

    return schemas.ApoderadoResponse(
        id_apoderado=apoderado.id_apoderado,
        usuario=schemas.ApoderadoConEstudiantes(
            id_usuario=usuario_actual.id_usuario,
            nombre=usuario_actual.nombre,
            email=usuario_actual.email,
            telefono=usuario_actual.telefono,
            estudiantes=[
                schemas.EstudianteSimple.from_orm(est) for est in estudiantes
            ]
        )
    )

@router.post("/asistencia", response_model=schemas.AsistenciaResponse)
def registrar_asistencia(
    asistencia: schemas.AsistenciaCreate,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    if usuario_actual.tipo_usuario != "apoderado":
        raise HTTPException(status_code=403, detail="No autorizado")

    estudiante = db.query(models.Estudiante).filter_by(id_estudiante=asistencia.id_estudiante).first()
    if not estudiante or estudiante.id_apoderado != usuario_actual.apoderado.id_apoderado:
        raise HTTPException(status_code=403, detail="No autorizado para este estudiante")

    hoy = date.today()

    registro_existente = db.query(models.Asistencia).filter_by(
        id_estudiante=asistencia.id_estudiante,
        fecha=hoy
    ).first()

    if asistencia.asiste:
        if registro_existente:
            registro_existente.asiste = True
            db.commit()
            db.refresh(registro_existente)
            return registro_existente
        else:
            nuevo = models.Asistencia(
                id_estudiante=asistencia.id_estudiante,
                fecha=hoy,
                asiste=True
            )
            db.add(nuevo)
            db.commit()
            db.refresh(nuevo)
            return nuevo
    else:
        if registro_existente:
            registro_existente.asiste = False
            db.commit()
            db.refresh(registro_existente)
            return registro_existente
        nuevo = models.Asistencia(
            id_estudiante=asistencia.id_estudiante,
            fecha=hoy,
            asiste=False
        )
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        return nuevo





@router.get("/mis-hijos-hoy", response_model=List[schemas.EstudianteConAsistenciaHoy])
def listar_hijos_con_asistencia(
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    if usuario_actual.tipo_usuario != "apoderado":
        raise HTTPException(status_code=403, detail="Solo los apoderados pueden acceder a esta información.")

    apoderado = db.query(models.Apoderado).filter_by(id_usuario=usuario_actual.id_usuario).first()
    if not apoderado:
        raise HTTPException(status_code=404, detail="Apoderado no encontrado.")

    estudiantes = apoderado.estudiantes
    resultado = []

    for est in estudiantes:
        # Buscar la asistencia más reciente (aunque no sea de hoy)
        asistencia = (
            db.query(models.Asistencia)
            .filter(models.Asistencia.id_estudiante == est.id_estudiante)
            .order_by(models.Asistencia.fecha.desc())
            .first()
        )

        if asistencia:
            asistencia_schema = schemas.AsistenciaHoyResponse.from_orm(asistencia)
        else:
            # Si no hay registros, se asume presente por defecto
            asistencia_schema = schemas.AsistenciaHoyResponse(
                fecha=date.today(),
                asiste=True
            )

        # Obtener nombre de la ruta si el estudiante tiene un conductor con ruta fija
        ruta_fija = (
            db.query(models.RutaFija)
            .join(models.Conductor)
            .filter(models.Conductor.id_conductor == est.id_conductor)
            .first()
        )

        ruta_schema = schemas.RutaResumen(
            id=ruta_fija.id_ruta_fija,
            nombre=ruta_fija.nombre
        ) if ruta_fija else None

        resultado.append(schemas.EstudianteConAsistenciaHoy(
            id_estudiante=est.id_estudiante,
            nombre=est.nombre,
            curso=est.curso,
            colegio=est.colegio,
            asistencia=asistencia_schema,
            ruta=ruta_schema
        ))

    return resultado


@router.get("/ubicacion-conductor/{id_usuario}", response_model=schemas.UbicacionConductorResponse)
def obtener_ubicacion_conductor(
    id_usuario: int,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    # Solo usuarios autenticados pueden acceder
    if usuario_actual.tipo_usuario not in ["apoderado", "conductor", "administrador"]:
        raise HTTPException(status_code=403, detail="No autorizado")

    # Buscar al conductor a partir del id_usuario
    conductor = db.query(models.Conductor).filter_by(id_usuario=id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    ubicacion = db.query(models.UbicacionConductor).filter_by(id_conductor=conductor.id_conductor).first()
    if not ubicacion:
        raise HTTPException(status_code=404, detail="Ubicación no encontrada para el conductor")

    return schemas.UbicacionConductorResponse(
        latitud=ubicacion.latitud,
        longitud=ubicacion.longitud,
        timestamp=ubicacion.timestamp
    )

@router.get("/mi-conductor", response_model=schemas.ConductorConAcompanante)
def obtener_conductor_asignado(
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    if usuario_actual.tipo_usuario != "apoderado":
        raise HTTPException(status_code=403, detail="No autorizado")

    apoderado = db.query(models.Apoderado).filter_by(id_usuario=usuario_actual.id_usuario).first()
    if not apoderado:
        raise HTTPException(status_code=404, detail="Apoderado no encontrado")

    estudiante = db.query(models.Estudiante).filter_by(id_apoderado=apoderado.id_apoderado).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="No se encontró estudiante asociado al apoderado")

    parada = (
        db.query(models.Parada)
        .filter_by(id_estudiante=estudiante.id_estudiante)
        .join(models.Ruta)
        .first()
    )
    if not parada or not parada.ruta:
        raise HTTPException(status_code=404, detail="No se encontró una ruta asignada al estudiante")

    conductor = parada.ruta.conductor
    if not conductor or not conductor.usuario:
        raise HTTPException(status_code=404, detail="Conductor no asignado correctamente")

    return schemas.ConductorConAcompanante(
    id_usuario=conductor.usuario.id_usuario,
    nombre=conductor.usuario.nombre,
    email=conductor.usuario.email,
    telefono=conductor.usuario.telefono,
    patente=conductor.patente,
    modelo_vehiculo=conductor.modelo_vehiculo,
    acompanante=schemas.NombreAcompanante(
        nombre_completo=conductor.acompanante.nombre
    ) if conductor.acompanante else None
)

