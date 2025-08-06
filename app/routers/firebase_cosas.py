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


@router.post("/registrar-token")
def registrar_token_firebase(
    datos: schemas.TokenFirebaseRequest,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    # Eliminar cualquier otro usuario que tenga este token
    db.query(models.TokenFirebase).filter(models.TokenFirebase.token == datos.token_firebase).delete()

    # Buscar si ya existe un registro de token para este usuario
    existente = db.query(models.TokenFirebase).filter_by(id_usuario=usuario_actual.id_usuario).first()

    if existente:
        existente.token = datos.token_firebase
    else:
        nuevo = models.TokenFirebase(
            id_usuario=usuario_actual.id_usuario,
            token=datos.token_firebase
        )
        db.add(nuevo)

    db.commit()
    return {"mensaje": "Token registrado correctamente"}
