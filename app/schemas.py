from pydantic import BaseModel, EmailStr
from typing import Optional, List, Literal
from datetime import date, time, datetime
from decimal import Decimal


# ------------------------ Direccion ------------------------
class DireccionBase(BaseModel):
    latitud: Decimal
    longitud: Decimal

class DireccionCreate(DireccionBase):
    pass

class DireccionResponse(BaseModel):
    id_direccion: int
    latitud: float
    longitud: float

    model_config = {
        "from_attributes": True
    }

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

class ConductorInfo(BaseModel):
    id_conductor: int
    patente: Optional[str]
    modelo_vehiculo: Optional[str]
    codigo_vinculacion: Optional[str]
    direcciones: List[DireccionResponse] = []

    model_config = {
        "from_attributes": True
    }
    
class ConductorUpdate(BaseModel):
    patente: Optional[str] = None
    modelo_vehiculo: Optional[str] = None
    codigo_vinculacion: Optional[str] = None
    
class ConductorVinculado(BaseModel):
    id_conductor: int
    nombre: str
    telefono: Optional[str]
    patente: Optional[str]
    modelo_vehiculo: Optional[str]
    codigo_vinculacion: Optional[str]

    model_config = {
        "from_attributes": True
    }


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
    
class ApoderadoVinculado(BaseModel):
    id_apoderado: int
    nombre: str
    telefono: Optional[str]
    email: str

    model_config = {
        "from_attributes": True
    }


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

class EstudianteCreate(EstudianteBase):
    id_conductor: Optional[int] = None
    
class EstudianteUpdate(BaseModel):
    nombre: Optional[str] = None
    edad: Optional[int] = None
    direccion: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    id_conductor: Optional[int] = None

    
class EstudianteResponse(EstudianteBase):
    id_estudiante: int

    model_config = {
        "from_attributes": True
    }



# ------------------------ Ruta ------------------------
class RutaCreate(BaseModel):
    fecha: date
    hora_inicio: time
    id_acompanante: Optional[int] = None

class ParadaResponse(BaseModel):
    id_parada: int
    latitud: float
    longitud: float
    orden: int
    recogido: bool
    entregado: bool
    id_estudiante: int

    model_config = {
        "from_attributes": True
    }

class RutaResponse(BaseModel):
    id_ruta: int
    fecha: date
    hora_inicio: time
    id_conductor: int
    id_acompanante: Optional[int]
    paradas: List[ParadaResponse]

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
    
class MarcarAsistenciaRequest(BaseModel):
    id_ruta: int
    id_estudiante: int
    accion: Literal["recogido", "entregado"]

class AsistenciaResponse(AsistenciaBase):
    id_asistencia: int
    registrada: datetime

    model_config = {
        "from_attributes": True
    }

# ------------------------ Vinculo  ------------------------
class VinculoCreate(BaseModel):
    id_apoderado: int
    id_conductor: int

class VinculacionRequest(BaseModel):
    codigo_vinculacion: str

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
