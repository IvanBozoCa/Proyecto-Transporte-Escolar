from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime,time
from datetime import date
# ---------- USUARIO ----------

class UsuarioBase(BaseModel):
    nombre: str
    email: EmailStr
    telefono: Optional[str]

    class Config:
        from_attributes = True

class UsuarioCreate(UsuarioBase):
    contrasena: str

class UsuarioResponse(BaseModel):
    nombre: str
    email: EmailStr
    telefono: str
    tipo_usuario: str

    class Config:
        from_attributes = True
        
class UsuarioUpdate(BaseModel):
    nombre: Optional[str] 
    email: Optional[EmailStr] 
    telefono: Optional[str] 
    contrasena: Optional[str] 
    
    class Config:
        from_attributes = True

# ---------- ESTUDIANTE ----------

class EstudianteCreate(BaseModel):
    nombre: str
    edad: int
    curso:str
    colegio:str
    direccion: str
    latitud: float
    longitud: float
    #hora_entrada: time
    nombre_apoderado_secundario: Optional[str] = None
    telefono_apoderado_secundario: Optional[str] = None

class EstudianteResponse(BaseModel):
    id_estudiante: int
    nombre: str
    edad: int
    curso:Optional[str] = None
    colegio:Optional[str] = None
    direccion: str
    latitud: float
    longitud: float
    #hora_entrada: time
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
    #hora_entrada: Optional[time]
    nombre_apoderado_secundario: Optional[str]
    telefono_apoderado_secundario: Optional[str]

class EstudianteSimple(BaseModel):
    id_estudiante: int
    nombre: str
    edad: int
    curso:str
    colegio:str
    direccion: str
    #hora_entrada: time
    nombre_apoderado_secundario: Optional[str] = None
    telefono_apoderado_secundario: Optional[str] = None

    class Config:
        from_attributes = True
        
class EstudianteConConductor(BaseModel):
    id_estudiante: int
    nombre: str
    edad: Optional[int]
    direccion: Optional[str]
    curso: Optional[str]
    colegio: Optional[str]
    nombre_conductor: Optional[str]

    class Config:
        from_attributes = True
        
class EstudianteEnConductor(BaseModel):
    id_estudiante: int
    nombre: str
    edad: int
    curso:Optional[str]
    colegio:Optional[str]
    direccion: str
    latitud: float
    longitud: float
    #hora_entrada: Optional[time]

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
        
class ApoderadoResponse(BaseModel):
    id_apoderado: int
    usuario: UsuarioBase

    class Config:
        from_attributes = True
        
class ApoderadoUpdate(BaseModel):
    usuario: UsuarioUpdate 

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
    class Config:
        from_attributes = True 
        
class DatosConductorSchema(BaseModel):
    patente: str
    modelo_vehiculo: str

class ConductorInfoResponse(BaseModel):
    usuario: UsuarioResponse
    datos_conductor: DatosConductorSchema

    class Config:
        from_attributes = True

class ConductorCompleto(BaseModel):
    usuario: UsuarioResponse
    datos_conductor: ConductorCreateDatos
    
    class Config:
        from_attributes = True

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
    nombre: Optional[str]
    email: Optional[EmailStr]
    telefono: Optional[str]
    patente: Optional[str]
    modelo_vehiculo: Optional[str]

class ConductorDetalle(BaseModel):
    usuario: UsuarioBase
    datos_conductor: ConductorUpdateDatos

    class Config:
        from_attributes = True
class ConductorCompletoCreate(BaseModel):
    usuario: UsuarioCreate
    datos_conductor: ConductorCreateDatos

class ConductorCompletoResponse(BaseModel):
    usuario: UsuarioResponse
    datos_conductor: DatosConductorSchema

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

# ========== RUTA ==========

class RutaEstudianteCreate(BaseModel):
    id_estudiante: int
    orden: Optional[int] = None  # orden de recogida opcional

class RutaCreate(BaseModel):
    id_conductor: int
    id_acompanante: Optional[int] = None
    fecha: date
    hora_inicio: Optional[time] = None
    estudiantes: List[RutaEstudianteCreate]

class RutaResponse(BaseModel):
    id_ruta: int
    id_conductor: int
    id_acompanante: Optional[int]
    fecha: date
    hora_inicio: Optional[time]
    estado: str
    estudiantes: List[RutaEstudianteCreate]

    class Config:
        from_attributes = True

class EstudianteBasico(BaseModel):
    id_estudiante: int
    nombre: str
    direccion: str
    colegio: Optional[str] = None
    curso: Optional[str] = None

    class Config:
        from_attributes = True


class ParadaResponse(BaseModel):
    orden: int
    latitud: float
    longitud: float
    recogido: bool
    entregado: bool
    estudiante: EstudianteBasico

    class Config:
        from_attributes = True


class RutaConParadasResponse(BaseModel):
    id_ruta: int
    fecha: date
    estado: str
    hora_inicio: Optional[time]
    id_acompanante: Optional[int] = None
    paradas: List[ParadaResponse]

    class Config:
        from_attributes = True


#========ASISTENCIAS===============


class EstudianteRutaInfo(BaseModel):
    id_estudiante: int
    nombre: str
    asiste: bool

class RutaDiariaResponse(BaseModel):
    id_conductor: int
    fecha: date
    estudiantes: List[EstudianteRutaInfo]
    
class AsistenciaResponse(BaseModel):
    id_asistencia: int
    id_estudiante: int
    fecha: date
    asiste: bool

    class Config:
        from_attributes = True

class AsistenciaCreate(BaseModel):
    fecha: date
    asiste: bool

class AsistenciaHoyResponse(BaseModel):
    fecha: date
    asiste: Optional[bool]

    class Config:
        from_attributes = True        
        
class EstudianteConAsistencias(BaseModel):
    id_estudiante: int
    nombre: str
    curso: str
    colegio: str
    asistencias: List[AsistenciaResponse] = []

    class Config:
        from_attributes = True
        
class EstudianteConAsistenciaHoy(BaseModel):
    id_estudiante: int
    nombre: str
    curso: str
    colegio: str
    asistencia: Optional[AsistenciaHoyResponse] = None

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



#===== Todos los usuarios existentes=====

from typing import Optional, Union

class DireccionResponse(BaseModel):
    latitud: float
    longitud: float

    class Config:
        from_attributes = True

class DatosConductor(BaseModel):
    patente: str
    modelo_vehiculo: str

    class Config:
        from_attributes = True

class DatosApoderado(BaseModel):
    direccion: Optional[DireccionResponse]

    class Config:
        from_attributes = True

class DatosAcompanante(BaseModel):
    nombre_completo: str  # puedes personalizar

    class Config:
        from_attributes = True

class UsuarioConDatos(BaseModel):
    id_usuario: int
    nombre: str
    email: EmailStr
    telefono: str
    tipo_usuario: str
    datos_conductor: Optional[DatosConductor] = None
    datos_apoderado: Optional[DatosApoderado] = None
    datos_acompanante: Optional[DatosAcompanante] = None

    class Config:
        from_attributes = True


# ======= Ruta Fija =======
class EstudianteBasico(BaseModel):
    id_estudiante: int
    nombre: str

    model_config = {
        "from_attributes": True
    }

class ParadaRutaFijaCreate(BaseModel):
    id_estudiante: int
    orden: int

class ParadaRutaFijaResponse(BaseModel):
    id_parada_ruta_fija: int
    orden: int
    estudiante: EstudianteBasico

    model_config = {
        "from_attributes": True
    }


class RutaFijaCreate(BaseModel):
    id_conductor: int
    nombre: str
    descripcion: Optional[str] = None
    paradas: List[ParadaRutaFijaCreate]

class RutaFijaResponse(BaseModel):
    id_ruta_fija: int
    nombre: str
    id_conductor: int
    paradas: List[ParadaRutaFijaResponse]

    class Config:
        from_attributes = True
        
class ParadaRutaFijaCreate(BaseModel):
    id_estudiante: int
    orden: int
    

class RutaFijaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    paradas: Optional[List[ParadaRutaFijaCreate]] = None  
    

