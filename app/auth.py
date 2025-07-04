from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status, Security
from app import schemas, models, database
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Usuario

# Dependencia para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Configuración de la clave secreta y algoritmo
SECRET_KEY = "furgonescolar"
ALGORITHM = "HS256"

# Hacemos que dure 10 años
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 365 * 10  # 10 años

# Contexto de hasheo con bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Función para hashear contraseñas
def hash_contrasena(plain_password: str) -> str:
    return pwd_context.hash(plain_password)

# Función para verificar contraseñas
def verificar_contrasena(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Función para crear un JWT token
def crear_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Función para decodificar y validar el token
def verificar_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# Bearer token
bearer_scheme = HTTPBearer()

# Función para obtener el usuario desde el token
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: Session = Depends(get_db)
) -> models.Usuario:
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar el token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        tipo_usuario: str = payload.get("tipo_usuario")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if user is None:
        raise credentials_exception
    
    return user

# Verificar tipo de usuario
def verificar_admin(usuario: Usuario = Depends(get_current_user)):
    if usuario.tipo_usuario != "administrador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    return usuario

def verificar_tipo_usuario(usuario: Usuario = Depends(get_current_user)):
    if usuario.tipo_usuario not in ["conductor", "apoderado"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    return usuario
