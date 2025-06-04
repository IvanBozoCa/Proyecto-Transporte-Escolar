from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import database, models, auth, schemas
from app.database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(prefix="/login", tags=["Autenticación"])

@router.post("/", response_model=schemas.TokenResponse)
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.email == data.email).first()

    if not usuario:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    if not auth.verificar_contrasena(data.contrasena, usuario.contrasena):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    token = auth.crear_token({
        "sub": usuario.email,
        "tipo_usuario": usuario.tipo_usuario,
        "id_usuario": usuario.id_usuario,
        "nombre": usuario.nombre
    })

    return {"access_token": token, "token_type": "bearer"}
