from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime,time

# ---------- USUARIO ----------

class UsuarioBase(BaseModel):
    nombre: str
    email: EmailStr
    telefono: str

class UsuarioCreate(UsuarioBase):
    contrasena: str

class UsuarioResponse(BaseModel):
    id_usuario: int
    nombre: str
    email: EmailStr
    telefono: str
    tipo_usuario: str

    class Config:
        from_attributes = True
class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    contrasena: Optional[str] = None

# ---------- ESTUDIANTE ----------

class EstudianteCreate(BaseModel):
    nombre: str
    edad: int
    curso:str
    colegio:str
    direccion: str
    latitud: float
    longitud: float
    hora_entrada: time
    nombre_apoderado_secundario: Optional[str] = None
    telefono_apoderado_secundario: Optional[str] = None

class EstudianteResponse(BaseModel):
    id_estudiante: int
    nombre: str
    edad: int
    curso:str
    colegio:str
    direccion: str
    latitud: float
    longitud: float
    hora_entrada: time
    nombre_apoderado_secundario: Optional[str] = None
    telefono_apoderado_secundario: Optional[str] = None

    class Config:
        from_attributes = True

class EstudianteUpdate(BaseModel):
    nombre: Optional[str]
    edad: Optional[int]
    curso:Optional[str]
    colegio:Optional[str]
    direccion: Optional[str]
    latitud: Optional[float]
    longitud: Optional[float]
    hora_entrada: Optional[time]
    nombre_apoderado_secundario: Optional[str]
    telefono_apoderado_secundario: Optional[str]

class EstudianteSimple(BaseModel):
    id_estudiante: int
    nombre: str
    edad: int
    curso:str
    colegio:str
    direccion: str
    hora_entrada: time
    nombre_apoderado_secundario: Optional[str] = None
    telefono_apoderado_secundario: Optional[str] = None

    class Config:
        from_attributes = True
        
class EstudianteEnConductor(BaseModel):
    id_estudiante: int
    nombre: str
    edad: int
    curso:str
    colegio:str
    direccion: str
    latitud: float
    longitud: float
    hora_entrada: Optional[time]

    class Config:
        from_attributes = True

# ---------- APODERADO Y ESTUDIANTE COMBINADO ----------

class ApoderadoYEstudiante(BaseModel):
    apoderado: UsuarioCreate
    estudiante: EstudianteCreate

class ApoderadoYEstudianteResponse(BaseModel):
    apoderado: UsuarioResponse
    estudiante: EstudianteResponse

class ApoderadoConEstudiantes(BaseModel):
    id_usuario: int
    nombre: str
    email: str
    telefono: str
    estudiantes: List[EstudianteSimple] = []

    class Config:
        from_attributes = True

# ---------- ACOMPAÑANTE ----------

class AcompananteCreate(BaseModel):
    nombre: str
    telefono: str
    
class AcompananteUpdate(BaseModel):
    nombre: Optional[str]
    telefono: Optional[str]

class AcompananteResponse(BaseModel):
    id_acompanante: int
    nombre: str
    telefono: str

    class Config:
        from_attributes = True

# ---------- CONDUCTOR ----------

class ConductorCreateDatos(BaseModel):
    patente: str
    modelo_vehiculo: str


class ConductorCompleto(BaseModel):
    usuario: UsuarioCreate
    datos_conductor: ConductorCreateDatos

class ConductorConEstudiantes(BaseModel):
    id_usuario: int
    nombre: str
    email: str
    telefono: str
    patente: str
    modelo_vehiculo: str

    estudiantes: List[EstudianteEnConductor] = []

    class Config:
        from_attributes = True
        
class ConductorUpdateDatos(BaseModel):
    patente: Optional[str]
    modelo_vehiculo: Optional[str]

class UbicacionConductorCreate(BaseModel):
    latitud: float
    longitud: float

class UbicacionConductorResponse(BaseModel):
    id_ubicacion: int
    latitud: float
    longitud: float
    timestamp: datetime

    class Config:
        from_attributes = True

    
#========ASISTENCIAS===============
from datetime import date

class AsistenciaCreate(BaseModel):
    id_estudiante: int
    fecha: date
    asiste: bool

class AsistenciaResponse(BaseModel):
    id_asistencia: int
    id_estudiante: int
    fecha: date
    asiste: bool

    class Config:
        from_attributes = True
# ------------------------ Login Request ------------------------
class LoginRequest(BaseModel):
    email: EmailStr
    contrasena: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
class FilaListadoGeneral(BaseModel):
    nombre_apoderado: str
    nombre_estudiante: str
    edad: Optional[int] 
    direccion: Optional[str] 
    curso: Optional[str] 
    nombre_conductor: str

    class Config:
        from_attributes = True
