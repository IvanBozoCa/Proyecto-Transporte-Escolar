from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, models, database, auth

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

# Dependencia para obtener la sesión de base de datos
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=schemas.UsuarioResponse)
def crear_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    # Verificar si ya existe el correo
    usuario_existente = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    if usuario_existente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El correo ya está registrado")
    
    # Hashear la contraseña
    hashed_pass = auth.hash_contrasena(usuario.contrasena)

    # Crear objeto de usuario
    nuevo_usuario = models.Usuario(
        nombre=usuario.nombre,
        email=usuario.email,
        telefono=usuario.telefono,
        tipo_usuario=usuario.tipo_usuario,
        contrasena=hashed_pass
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return nuevo_usuario


from app.auth import get_current_user

@router.get("/me")
def obtener_mi_usuario(usuario_actual: models.Usuario = Depends(get_current_user)):
    return {
        "id_usuario": usuario_actual.id_usuario,
        "nombre": usuario_actual.nombre,
        "tipo_usuario": usuario_actual.tipo_usuario_token  # <- del token
    }
