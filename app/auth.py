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
import re

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


def verificar_admin(usuario: Usuario = Depends(get_current_user)):
    if usuario.tipo_usuario != "administrador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    return usuario

def verificar_tipo_usuario(usuario: Usuario = Depends(get_current_user)):
    if usuario.tipo_usuario not in ["conductor", "apoderado"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    return usuario


def validar_contrasena(password: str):
    if len(password) < 10:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 10 caracteres.")
    if not any(c.isupper() for c in password):
        raise HTTPException(status_code=400, detail="Debe tener al menos una letra mayúscula.")
    if not any(c.islower() for c in password):
        raise HTTPException(status_code=400, detail="Debe tener al menos una letra minúscula.")
    if not any(c.isdigit() for c in password):
        raise HTTPException(status_code=400, detail="Debe tener al menos un número.")
    if not any(c in "!@#$%^&*()_+-=[]{};:,.<>?" for c in password):
        raise HTTPException(status_code=400, detail="Debe tener al menos un símbolo especial.")


def validar_patente_chilena(patente: str): 
    patente = patente.strip().upper()
    
    formato_nuevo = re.match(r'^[A-Z]{2}[0-9]{2}[A-Z]{2}$', patente)
    formato_antiguo = re.match(r'^[A-Z]{3}[0-9]{3}$', patente)
    
    if not (formato_nuevo or formato_antiguo):
        raise HTTPException(
            status_code=400,
            detail="La patente no tiene un formato válido. Ejemplos válidos: AB12CD o ABC123"
        )
        
RESET_PASSWORD_SECRET = "OTRA_LLAVE_SECRETA" 
def generar_token_restablecer_contrasena(email: str) -> str:
    datos = {"sub": email, "exp": datetime.utcnow() + timedelta(minutes=15)}
    return jwt.encode(datos, RESET_PASSWORD_SECRET, algorithm=ALGORITHM)

def verificar_token_restablecer_contrasena(token: str) -> str:
    try:
        payload = jwt.decode(token, RESET_PASSWORD_SECRET, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="El enlace ha expirado")
    except jwt.JWTError:
        raise HTTPException(status_code=400, detail="Token inválido")
    
    
def validar_email(email: str):

    patron = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(patron, email):
        raise HTTPException(
            status_code=400,
            detail="El correo electrónico no tiene un formato válido. Ejemplo: usuario@dominio.com"
        )


def validar_telefono(telefono: str):

    patron = r"^\+56\d{9}$"
    if not re.match(patron, telefono):
        raise HTTPException(
            status_code=400,
            detail="El número debe comenzar con +56 seguido de 9 dígitos. Ejemplo: +56912345678"
        )
