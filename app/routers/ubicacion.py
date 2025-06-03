from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app import models, schemas
from app.database import get_db
from app.auth import get_current_user

router = APIRouter(prefix="/ubicacion", tags=["Ubicación"])

@router.post("/", response_model=schemas.UbicacionConductorResponse)
def registrar_ubicacion(
    datos: schemas.UbicacionConductorCreate,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    if usuario_actual.tipo_usuario_token != "conductor":
        raise HTTPException(status_code=403, detail="Solo conductores pueden registrar su ubicación")

    conductor = db.query(models.Conductor).filter_by(id_usuario=usuario_actual.id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    nueva = models.UbicacionConductor(
        id_conductor=conductor.id_conductor,
        latitud=datos.latitud,
        longitud=datos.longitud,
        timestamp=datetime.utcnow()
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    return nueva


@router.get("/conductor/{id_usuario}", response_model=schemas.UbicacionConductorResponse)
def obtener_ultima_ubicacion(
    id_usuario: int,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    conductor = db.query(models.Conductor).filter_by(id_usuario=id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    ultima = (
        db.query(models.UbicacionConductor)
        .filter_by(id_conductor=conductor.id_conductor)
        .order_by(models.UbicacionConductor.timestamp.desc())
        .first()
    )
    if not ultima:
        raise HTTPException(status_code=404, detail="Ubicación no disponible")

    return ultima
