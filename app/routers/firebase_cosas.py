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


@router.post("/firebase/token")
def registrar_token_firebase(
    token: str,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    token_existente = db.query(models.TokenFirebase).filter_by(id_usuario=usuario_actual.id_usuario).first()

    if token_existente:
        token_existente.token = token
    else:
        nuevo_token = models.TokenFirebase(
            token=token,
            id_usuario=usuario_actual.id_usuario
        )
        db.add(nuevo_token)

    db.commit()
    return {"mensaje": "Token registrado correctamente"}




from app.firebase.notificaciones import enviar_notificacion
from sqlalchemy.orm import joinedload

@router.put("/parada/{id_parada}/recoger", response_model=schemas.ParadaResponse)
def marcar_parada_como_recogida(
    id_parada: int,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    if usuario_actual.tipo_usuario != "conductor":
        raise HTTPException(status_code=403, detail="No autorizado")

    conductor = db.query(models.Conductor).filter_by(id_usuario=usuario_actual.id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    parada = db.query(models.Parada).options(joinedload(models.Parada.estudiante)).filter_by(id_parada=id_parada).first()
    if not parada:
        raise HTTPException(status_code=404, detail="Parada no encontrada")

    if parada.ruta.id_conductor != conductor.id_conductor:
        raise HTTPException(status_code=403, detail="Esta parada no pertenece a tu ruta")

    if parada.ruta.estado != "activa":
        raise HTTPException(status_code=400, detail="La ruta no está activa")

    parada.recogido = True
    db.commit()
    db.refresh(parada)

    estudiante = parada.estudiante
    if estudiante:
        apoderado = estudiante.apoderado
        if apoderado:
            token_obj = db.query(models.TokenFirebase).filter_by(id_usuario=apoderado.id_usuario).first()
            if token_obj:
                enviar_notificacion(
                    titulo="Estudiante recogido",
                    cuerpo=f"El estudiante {estudiante.nombre} fue recogido.",
                    token=token_obj.token
                )

    return parada

