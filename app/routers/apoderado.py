from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Usuario, Conductor, Asistencia
from app.auth import get_current_user, verificar_admin, verificar_tipo_usuario
from app import models, schemas
from typing import List
from datetime import date

router = APIRouter(
    prefix="/apoderado",
    tags=["Apoderado"]
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

    # Buscar si ya existe un registro de asistencia para hoy
    registro_existente = db.query(models.Asistencia).filter_by(
        id_estudiante=asistencia.id_estudiante,
        fecha=hoy
    ).first()

    if registro_existente:
        registro_existente.asiste = asistencia.asiste
        db.commit()
        db.refresh(registro_existente)
        return registro_existente

    # Si no existe, crearlo
    nuevo = models.Asistencia(
        id_estudiante=asistencia.id_estudiante,
        fecha=hoy,
        asiste=asistencia.asiste
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo




@router.get("/asistencia/hoy", response_model=List[schemas.EstudianteBasico])
def estudiantes_presentes_hoy(
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    hoy = date.today()

    asistencias = db.query(models.Asistencia).filter_by(fecha=hoy, asiste=True).all()
    estudiantes = [asistencia.estudiante for asistencia in asistencias]

    return estudiantes
