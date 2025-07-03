from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Usuario, Conductor
from app.auth import get_current_user, verificar_admin, verificar_tipo_usuario
from app import models, schemas
from typing import List
from datetime import date, datetime
router = APIRouter(
    prefix="/firebase",
    tags=["Firebase"]
)


@router.post("/RegistrarToken")
def registrar_token_firebase(
    token_data: schemas.TokenFirebaseCreate,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    existente = db.query(models.TokenFirebase).filter_by(id_usuario=usuario_actual.id_usuario).first()

    if existente:
        existente.token = token_data.token
    else:
        nuevo_token = models.TokenFirebase(id_usuario=usuario_actual.id_usuario, token=token_data.token)
        db.add(nuevo_token)

    db.commit()
    return {"mensaje": "Token Firebase registrado correctamente"}
