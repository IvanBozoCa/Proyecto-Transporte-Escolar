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
        # Si ya existe y es False, lo eliminamos para asumir asistencia por defecto
        if registro_existente:
            db.delete(registro_existente)
            db.commit()
        # Devolvemos asistencia simulada en True
        return schemas.AsistenciaResponse(
            id_asistencia=0,
            id_estudiante=asistencia.id_estudiante,
            fecha=hoy,
            asiste=True
        )

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




@router.get("/apoderado/mis-estudiantes-hoy", response_model=List[schemas.EstudianteConAsistenciaHoy])
def listar_estudiantes_apoderado_con_asistencia_hoy(
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
        asistencia_hoy = db.query(models.Asistencia).filter_by(
            id_estudiante=est.id_estudiante,
            fecha=date.today()
        ).first()

        asistencia_schema = schemas.AsistenciaHoyResponse.from_orm(asistencia_hoy) if asistencia_hoy else None

        ruta_resumen = None
        if est.conductor:
            ruta_fija = db.query(models.RutaFija).filter_by(id_conductor=est.conductor.id_conductor).first()
            if ruta_fija:
                ruta_resumen = schemas.RutaResumen(
                    id=ruta_fija.id_ruta_fija,
                    nombre=ruta_fija.nombre
                )

        resultado.append(schemas.EstudianteConAsistenciaHoy(
            id_estudiante=est.id_estudiante,
            nombre=est.nombre,
            curso=est.curso,
            colegio=est.colegio,
            asistencia=asistencia_schema,
            ruta=ruta_resumen
        ))

    return resultado
