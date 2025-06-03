from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from app import models, schemas
from app.database import get_db
from app.auth import obtener_usuario_actual

router = APIRouter(prefix="/asistencia", tags=["Asistencia"])

@router.post("/", response_model=schemas.AsistenciaResponse)
def registrar_asistencia(
    datos: schemas.AsistenciaCreate,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(obtener_usuario_actual)
):
    # Solo apoderado puede marcar asistencia
    if usuario_actual.tipo_usuario != "apoderado":
        raise HTTPException(status_code=403, detail="Solo apoderados pueden registrar asistencia")

    estudiante = db.query(models.Estudiante).filter_by(id_estudiante=datos.id_estudiante).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    if estudiante.id_apoderado != usuario_actual.id_usuario:
        raise HTTPException(status_code=403, detail="No puedes marcar asistencia para este estudiante")

    # Verificamos si ya existe un registro para ese día
    asistencia_existente = db.query(models.Asistencia).filter_by(
        id_estudiante=datos.id_estudiante,
        fecha=datos.fecha
    ).first()

    if asistencia_existente:
        asistencia_existente.asiste = datos.asiste
        db.commit()
        db.refresh(asistencia_existente)
        return asistencia_existente

    nueva = models.Asistencia(**datos.dict())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva
