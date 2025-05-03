from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, time, datetime

# ------------------------ Usuario ------------------------
class UsuarioBase(BaseModel):
    nombre: str
    email: EmailStr
    telefono: Optional[str] = None

class UsuarioCreate(UsuarioBase):
    contrasena: str
    tipo_usuario: str

class UsuarioResponse(UsuarioBase):
    id_usuario: int
    tipo_usuario: str

    model_config = {
        "from_attributes": True
    }

# ------------------------ Conductor ------------------------
class ConductorBase(BaseModel):
    patente: Optional[str] = None
    modelo_vehiculo: Optional[str] = None
    codigo_vinculacion: Optional[str] = None

class ConductorCreate(ConductorBase):
    id_usuario: int

class ConductorResponse(ConductorBase):
    id_conductor: int

    model_config = {
        "from_attributes": True
    }

# ------------------------ Apoderado ------------------------
class ApoderadoBase(BaseModel):
    direccion: Optional[str] = None

class ApoderadoCreate(ApoderadoBase):
    id_usuario: int

class ApoderadoResponse(ApoderadoBase):
    id_apoderado: int

    model_config = {
        "from_attributes": True
    }

# ------------------------ Estudiante ------------------------
class EstudianteBase(BaseModel):
    nombre: str
    edad: Optional[int] = None
    direccion: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None

class EstudianteCreate(EstudianteBase):
    id_apoderado: int

class EstudianteResponse(EstudianteBase):
    id_estudiante: int

    model_config = {
        "from_attributes": True
    }

# ------------------------ Ruta ------------------------
class RutaBase(BaseModel):
    fecha: date
    hora_inicio: Optional[time] = None
    estado: Optional[str] = "activa"

class RutaCreate(RutaBase):
    id_conductor: int
    id_acompanante: Optional[int] = None

class RutaResponse(RutaBase):
    id_ruta: int

    model_config = {
        "from_attributes": True
    }

# ------------------------ Parada ------------------------
class ParadaBase(BaseModel):
    orden: int
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    recogido: Optional[bool] = False
    entregado: Optional[bool] = False

class ParadaCreate(ParadaBase):
    id_estudiante: int
    id_ruta: int

class ParadaResponse(ParadaBase):
    id_parada: int

    model_config = {
        "from_attributes": True
    }

# ------------------------ Acompañante ------------------------
class AcompananteBase(BaseModel):
    nombre: str
    telefono: Optional[str] = None

class AcompananteCreate(AcompananteBase):
    pass

class AcompananteResponse(AcompananteBase):
    id_acompanante: int

    model_config = {
        "from_attributes": True
    }

# ------------------------ Notificación ------------------------
class NotificacionBase(BaseModel):
    mensaje: str
    tipo_envio: Optional[str] = None

class NotificacionCreate(NotificacionBase):
    id_usuario: int

class NotificacionResponse(NotificacionBase):
    id_notificacion: int
    fecha: datetime

    model_config = {
        "from_attributes": True
    }

# ------------------------ Asistencia ------------------------
class AsistenciaBase(BaseModel):
    fecha: date
    asistencia: Optional[bool] = True

class AsistenciaCreate(AsistenciaBase):
    id_estudiante: int

class AsistenciaResponse(AsistenciaBase):
    id_asistencia: int
    registrada: datetime

    model_config = {
        "from_attributes": True
    }

# ------------------------ Vinculo Apoderado-Conductor ------------------------
class VinculoCreate(BaseModel):
    id_apoderado: int
    id_conductor: int

class VinculoResponse(VinculoCreate):
    id_vinculo: int
    fecha_vinculacion: datetime

    model_config = {
        "from_attributes": True
    }
# ------------------------ Login Request ------------------------
class LoginRequest(BaseModel):
    email: EmailStr
    contrasena: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
