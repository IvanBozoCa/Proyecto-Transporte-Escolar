from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import schemas, models, database, auth
from app.auth import get_current_user

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

# Dependencia para obtener la sesión de base de datos
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/me", response_model=schemas.UsuarioResponse)
def obtener_mi_usuario(usuario_actual: models.Usuario = Depends(get_current_user)):
    return {
        "id_usuario": usuario_actual.id_usuario,
        "nombre": usuario_actual.nombre,
        "tipo_usuario": usuario_actual.tipo_usuario
    }

@router.put("/me", response_model=schemas.UsuarioResponse)
def actualizar_mi_usuario(
    cambios: schemas.UsuarioUpdate,
    usuario_actual: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    for campo, valor in cambios.dict(exclude_unset=True).items():
        if campo == "contrasena":
            valor = auth.hash_contrasena(valor)
        setattr(usuario_actual, campo, valor)

    db.commit()
    db.refresh(usuario_actual)
    return usuario_actual
