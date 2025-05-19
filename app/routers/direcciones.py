from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, auth
from app.database import get_db

router = APIRouter(prefix="/direcciones", tags=["Direcciones"])

@router.post("/", response_model=schemas.DireccionResponse)
def agregar_direccion(
    direccion: schemas.DireccionCreate,
    usuario_actual: models.Usuario = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if usuario_actual.tipo_usuario_token == "apoderado":
        apoderado = db.query(models.Apoderado).filter(models.Apoderado.id_usuario == usuario_actual.id_usuario).first()
        if not apoderado:
            raise HTTPException(status_code=404, detail="Apoderado no encontrado")
        nueva = models.Direccion(
            latitud=direccion.latitud,
            longitud=direccion.longitud,
            id_apoderado=apoderado.id_apoderado
        )

    elif usuario_actual.tipo_usuario_token == "conductor":
        conductor = db.query(models.Conductor).filter(models.Conductor.id_usuario == usuario_actual.id_usuario).first()
        if not conductor:
            raise HTTPException(status_code=404, detail="Conductor no encontrado")
        nueva = models.Direccion(
            latitud=direccion.latitud,
            longitud=direccion.longitud,
            id_conductor=conductor.id_conductor
        )
    else:
        raise HTTPException(status_code=403, detail="Este tipo de usuario no puede registrar direcciones.")

    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

# GET para obtener direcciones del usuario autenticado
@router.get("/", response_model=list[schemas.DireccionResponse])
def obtener_mis_direcciones(
    usuario_actual: models.Usuario = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if usuario_actual.tipo_usuario_token == "apoderado":
        apoderado = db.query(models.Apoderado).filter(models.Apoderado.id_usuario == usuario_actual.id_usuario).first()
        if not apoderado:
            raise HTTPException(status_code=404, detail="Apoderado no encontrado")
        return apoderado.direcciones

    elif usuario_actual.tipo_usuario_token == "conductor":
        conductor = db.query(models.Conductor).filter(models.Conductor.id_usuario == usuario_actual.id_usuario).first()
        if not conductor:
            raise HTTPException(status_code=404, detail="Conductor no encontrado")
        return conductor.direcciones

    else:
        raise HTTPException(status_code=403, detail="Este tipo de usuario no puede tener direcciones.")