from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Usuario, Conductor
from app.auth import get_current_user, verificar_admin
from app.schemas import ConductorCompleto

router = APIRouter(
    prefix="/conductor",
    tags=["Conductor"]
)

@router.get("/me", response_model=ConductorCompleto)
def obtener_datos_conductor(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user)
):
    verificar_admin(usuario_actual, "conductor")

    conductor = db.query(Conductor).filter_by(id_usuario=usuario_actual.id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    return conductor
