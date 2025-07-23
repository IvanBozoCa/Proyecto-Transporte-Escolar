from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, models, database, auth,email_envio
from app.auth import get_current_user
from app.database import get_db
from pydantic import EmailStr
router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("/CrearAdministrador", response_model=schemas.UsuarioResponse)
def crear_administrador(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    # Validar si ya existe el correo
    if db.query(models.Usuario).filter_by(email=usuario.email).first():
        raise HTTPException(status_code=400, detail="Correo ya registrado")

    # Validar contraseña
    auth.validar_contrasena(usuario.contrasena)

    # Crear usuario con tipo administrador
    nuevo_usuario = models.Usuario(
        nombre=usuario.nombre,
        email=usuario.email,
        telefono=usuario.telefono,
        tipo_usuario="administrador",
        contrasena=auth.hash_contrasena(usuario.contrasena)
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return schemas.UsuarioResponse(
        nombre=nuevo_usuario.nombre,
        email=nuevo_usuario.email,
        telefono=nuevo_usuario.telefono,
        tipo_usuario=nuevo_usuario.tipo_usuario
    )

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


@router.post("/OlvideContrasena")
def solicitar_reinicio_contrasena(email: EmailStr, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter_by(email=email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    token = auth.generar_token_restablecer_contrasena(usuario.email)

    email_envio.enviar_correo_restablecer_contrasena(email, token)
    return {"mensaje": "Revisa tu correo para restablecer la contraseña", "token": token}


@router.post("/ReiniciarContrasena")
def reiniciar_contrasena(datos: schemas.ReiniciarContrasenaInput, db: Session = Depends(get_db)):
    email = auth.verificar_token_restablecer_contrasena(datos.token)
    usuario = db.query(models.Usuario).filter_by(email=email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Validar nueva contraseña
    auth.validar_contrasena(datos.nueva_contrasena)

    # Actualizar
    usuario.contrasena = auth.hash_contrasena(datos.nueva_contrasena)
    db.commit()

    return {"mensaje": "Contraseña actualizada correctamente"}