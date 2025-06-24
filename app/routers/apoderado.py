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

@router.post("/asistencia", response_model=dict)
def registrar_asistencia(
    id_estudiante: int,
    asistencia: schemas.AsistenciaCreate,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    # Solo apoderados pueden registrar asistencia
    if usuario_actual.tipo_usuario != "apoderado":
        raise HTTPException(status_code=403, detail="No autorizado")

    estudiante = db.query(models.Estudiante).filter_by(id_estudiante=asistencia.id_estudiante).first()
    if not estudiante or estudiante.id_apoderado != usuario_actual.apoderado.id_apoderado:
        raise HTTPException(status_code=403, detail="No autorizado para este estudiante")

    registro = db.query(models.Asistencia).filter_by(
        id_estudiante=asistencia.id_estudiante,
    ).first()

    if registro:
        registro.asiste = asistencia.asiste
    else:
        nuevo = models.Asistencia(
            id_estudiante=asistencia.id_estudiante,
            asiste=asistencia.asiste
        )
        db.add(nuevo)

    db.commit()
    return {"mensaje": "Asistencia registrada correctamente"}


@router.get("/asistencia/hoy", response_model=List[schemas.EstudianteBasico])
def estudiantes_presentes_hoy(
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    hoy = date.today()

    asistencias = db.query(models.Asistencia).filter_by(fecha=hoy, asiste=True).all()
    estudiantes = [asistencia.estudiante for asistencia in asistencias]

    return estudiantes
