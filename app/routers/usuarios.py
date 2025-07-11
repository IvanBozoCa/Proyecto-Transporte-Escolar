from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, models, database, auth
from app.auth import get_current_user
from app.database import get_db
router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.get("/me", response_model=schemas.UsuarioResponse)
def obtener_mi_usuario(usuario_actual: models.Usuario = Depends(get_current_user)):
    return usuario_actual

@router.put("/me", response_model=schemas.UsuarioResponse)
def actualizar_mi_usuario(
    cambios: schemas.UsuarioUpdate,
    usuario_token: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)):
    
    usuario_actual = db.query(models.Usuario).filter_by(id_usuario=usuario_token.id_usuario).first()
    if not usuario_actual:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    datos = cambios.dict(exclude_unset=True)

    # Validación: email en uso
    if "email" in datos:
        email_existente = db.query(models.Usuario).filter(
            models.Usuario.email == datos["email"],
            models.Usuario.id_usuario != usuario_actual.id_usuario
        ).first()
        if email_existente:
            raise HTTPException(status_code=400, detail="Este correo ya está en uso.")

    # Aplicar cambios
    for campo, valor in datos.items():
        if campo == "contrasena":
            valor = auth.hash_contrasena(valor)
        if hasattr(usuario_actual, campo):
            setattr(usuario_actual, campo, valor)

    db.commit()
    db.refresh(usuario_actual)
    return usuario_actual
