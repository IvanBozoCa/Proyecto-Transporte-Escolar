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

class UsuarioResponse(BaseModel):
    nombre: str
    email: EmailStr
    telefono: str
    tipo_usuario: str
    
    class Config:
        from_attributes = True
        
class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    telefono: str
    contrasena: str 
    

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] 
    email: Optional[EmailStr] 
    telefono: Optional[str] 
    
    class Config:
        from_attributes = True

class UsuarioUpdateconductor(BaseModel):
    nombre: Optional[str] 
    email: Optional[EmailStr] 
    telefono: Optional[str] 
    casa: Optional[str]
    lat_casa: Optional[float]
    long_casa: Optional[float]
    
    class Config:
        from_attributes = True

# ---------- ESTUDIANTE ----------

class Coordenadas(BaseModel):
    lat: float
    long: float

class EstudianteCreate(BaseModel):
    nombre: str
    edad: int
    colegio: Optional[str] = None
    casa: Optional[str]
    lat_casa: Optional[float]
    long_casa: Optional[float]
    lat_colegio: Optional[float]
    long_colegio: Optional[float]
    curso: Optional[str] = None
    nombre_apoderado_secundario: Optional[str] = None
    telefono_apoderado_secundario: Optional[str] = None
    id_usuario_conductor: Optional[int]

class EstudianteResponse(BaseModel):
    id_estudiante: int
    nombre: str
    edad: int
    curso: Optional[str] 
    colegio: Optional[str]
    casa: Optional[str]  
    lat_casa: Optional[float]
    long_casa: Optional[float]
    lat_colegio: Optional[float]
    long_colegio: Optional[float]
    nombre_apoderado_secundario: Optional[str] = None
    telefono_apoderado_secundario: Optional[str] = None
    id_usuario_conductor: Optional[int]
    class Config:
        from_attributes = True

class EstudianteUpdate(BaseModel):
    nombre: Optional[str]
    edad: Optional[int]
    curso: Optional[str] = None
    colegio: Optional[str] = None
    casa: Optional[str]  # texto
    lat_casa: Optional[float]
    long_casa: Optional[float]
    lat_colegio: Optional[float]
    long_colegio: Optional[float]
    nombre_apoderado_secundario: Optional[str]
    telefono_apoderado_secundario: Optional[str]
    id_usuario_conductor: Optional[int]
    
class EstudianteSimple(BaseModel):
    id_estudiante: int
    nombre: str
    edad: int
    colegio: Optional[str] = None
    curso: Optional[str] = None
    colegio: Optional[str] = None
    casa: Optional[str] = None
    lat_casa: Optional[float] = None
    long_casa: Optional[float] = None
    lat_colegio: Optional[float]= None
    long_colegio: Optional[float]= None
    nombre_apoderado_secundario: Optional[str] = None
    telefono_apoderado_secundario: Optional[str] = None
    id_usuario_conductor: Optional[int]
    class Config:
        from_attributes = True

        
class EstudianteConConductor(BaseModel):
    id_estudiante: int
    nombre: str
    edad: Optional[int]
    casa: Optional[str]
    lat_casa: Optional[float]
    long_casa: Optional[float]
    curso: Optional[str]
    colegio: Optional[str]
    nombre_conductor: Optional[str]

    class Config:
        from_attributes = True
        
class EstudianteEnConductor(BaseModel):
    id_estudiante: int
    nombre: str
    edad: int
    curso: Optional[str]
    colegio: Optional[str]
    casa: Optional[str]
    lat_casa: Optional[float]
    long_casa: Optional[float]

    class Config:
        from_attributes = True

# ---------- APODERADO Y ESTUDIANTE COMBINADO ----------

class ApoderadoYEstudiantecreate(BaseModel):
    apoderado: UsuarioCreate
    estudiante: EstudianteCreate
    
class ApoderadoYEstudiante(BaseModel):
    apoderado: UsuarioUpdate
    estudiante: EstudianteUpdate

class ApoderadoYEstudianteResponse(BaseModel):
    apoderado: UsuarioResponse
    estudiante: EstudianteResponse

class ApoderadoConEstudiantes(BaseModel):
    id_usuario: int
    nombre: str
    email: str
    telefono: str
    estudiantes: List[EstudianteSimple]

    class Config:
        from_attributes = True
        
class ApoderadoResponse(BaseModel):
    id_apoderado: int
    usuario: ApoderadoConEstudiantes

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
    casa: str
    lat_casa: Optional[float]
    long_casa: Optional[float]
    
    class Config:
        from_attributes = True 
        
class DatosConductorSchema(BaseModel):
    patente: str
    modelo_vehiculo: str
    casa: Optional[str]
    lat_casa: Optional[float]
    long_casa: Optional[float]
    
    class Config:
        from_attributes = True
        
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
    patente: Optional[str]
    modelo_vehiculo: Optional[str]
    casa: Optional[str]
    lat_casa: Optional[float]
    long_casa: Optional[float]

class ConductorDetalle(BaseModel):
    usuario: UsuarioBase
    datos_conductor: ConductorUpdateDatos

    class Config:
        from_attributes = True
class ConductorCompletoCreate(BaseModel):
    usuario: UsuarioCreate
    datos_conductor: DatosConductorSchema

class ConductorCompletoupdate(BaseModel):
    usuario: UsuarioUpdate
    datos_conductor: ConductorUpdateDatos

class ConductorCompletoResponse(BaseModel):
    usuario: UsuarioResponse
    datos_conductor: DatosConductorSchema

class UbicacionConductorCreate(BaseModel):
    latitud: float
    longitud: float

class UbicacionConductorResponse(BaseModel):
    latitud: float
    longitud: float
    timestamp: datetime

    class Config:
        from_attributes = True
        
class NombreAcompanante(BaseModel):
    nombre_completo: str

    class Config:
        from_attributes = True
class ConductorConAcompanante(BaseModel):
    id_usuario: int
    nombre: str
    email: str
    telefono: str
    patente: str
    modelo_vehiculo: str
    acompanante: Optional[NombreAcompanante] = None


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

    model_config = {
        "from_attributes": True
    }


class ParadaResponse(BaseModel):
    id_parada: int
    orden: int
    latitud: float
    longitud: float
    recogido: bool
    entregado: bool
    estudiante: Optional[EstudianteSimple] = None

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
    id_estudiante: int
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
        
class RutaResumen(BaseModel):
    id: int
    nombre: str

    class Config:
        from_attributes = True
        
class EstudianteConAsistenciaHoy(BaseModel):
    id_estudiante: int
    nombre: str
    curso: str
    colegio: str
    asistencia: Optional[AsistenciaHoyResponse] = None
    ruta: Optional[RutaResumen] = None 

    class Config:
        from_attributes = True
        
    
class EstudianteHoyConParada(BaseModel):
    id_estudiante: int
    nombre: str
    curso: str
    colegio: str
    asistencia: Optional[AsistenciaHoyResponse] = None
    recogido: Optional[bool] = None
    entregado: Optional[bool] = None
    orden: Optional[int] = None

    class Config:
        from_attributes = True
# ------------------------ Login Request ------------------------
class LoginRequest(BaseModel):
    email: EmailStr
    contrasena: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenFirebaseCreate(BaseModel):
    token: str

 
class FilaListadoGeneral(BaseModel):
    nombre_apoderado: str
    nombre_estudiante: str
    edad: Optional[int] 
    casa: Optional[str]
    lat_casa: Optional[float]
    long_casa: Optional[float]
    curso: Optional[str] 
    nombre_conductor: str

    class Config:
        from_attributes = True



#===== Todos los usuarios existentes=====

class DatosConductor(BaseModel):
    patente: str
    modelo_vehiculo: str
    casa: Optional[str] = None
    lat_casa: Optional[float] = None
    long_casa: Optional[float] = None
    class Config:
        from_attributes = True

class EstudianteResumen(BaseModel):
    id_estudiante: int
    nombre: str
    edad: Optional[int]
    curso: Optional[str]
    casa: Optional[str]
    lat_casa: Optional[float]
    long_casa: Optional[float]
    colegio: Optional[str]
    lat_colegio: Optional[float]
    long_colegio: Optional[float]
    id_conductor: Optional[int]

class DatosApoderado(BaseModel):
    id_apoderado: int
    estudiante: EstudianteResumen
    class Config:
        from_attributes = True
    
class DatosAcompanante(BaseModel):
    nombre_completo: str  # puedes personalizar

    class Config:
        from_attributes = True
        
class DireccionEstudiante(BaseModel):
    casa: Optional[str]
    latitud: Optional[float]
    longitud: Optional[float]

class UsuarioConDatos(BaseModel):
    id_usuario: int
    nombre: str
    email: EmailStr
    telefono: str
    tipo_usuario: str
    datos_conductor: Optional[DatosConductor] = None
    datos_apoderado: Optional[DatosApoderado] = None
    datos_acompanante: Optional[DatosAcompanante] = None
    direccion_estudiante: Optional[DireccionEstudiante] = None
    
    class Config:
        from_attributes = True


# ======= Ruta Fija =======

class ParadaRutaFijaCreate(BaseModel):
    id_estudiante: Optional[int] = None  
    orden: int
    es_destino_final: Optional[bool] = False

class ParadaRutaFijaResponse(BaseModel):
    id_parada_ruta_fija: int
    orden: int
    estudiante: Optional[EstudianteBasico] = None
    es_destino_final: Optional[bool] = False
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    
    model_config = {
        "from_attributes": True
    }


class ParadaEstudianteRutaFijaCreate(BaseModel):
    id_estudiante: int
    orden: int

class ParadaFinalRutaFijaCreate(BaseModel):
    latitud: float
    longitud: float
    orden: Optional[int] = None
    
class RutaFijaCreate(BaseModel):
    id_conductor: int
    nombre: str
    descripcion: str
    paradas_estudiantes: List[ParadaEstudianteRutaFijaCreate]
    parada_final: Optional[ParadaFinalRutaFijaCreate] = None




class ParadaRutaDiaResponse(BaseModel):
    id_parada: int
    orden: int
    recogido: bool
    entregado: bool
    estudiante: EstudianteSimple  

    class Config:
        from_attributes = True

class RutaDiaActivaResponse(BaseModel):
    id_ruta: int
    fecha: date
    estado: str
    paradas: List[ParadaRutaDiaResponse]
    
class RutaFijaUpdate(BaseModel):
    nombre: Optional[str]
    descripcion: Optional[str]
    id_conductor: Optional[int] 
    paradas_estudiantes: Optional[List[ParadaEstudianteRutaFijaCreate]]
    parada_final: Optional[ParadaFinalRutaFijaCreate]

class ParadaEstudianteRutaFijaResponse(BaseModel):
    id_parada_ruta_fija: int
    orden: int
    estudiante: Optional[EstudianteBasico]

    class Config:
        from_attributes = True


class ParadaFinalRutaFijaResponse(BaseModel):
    id_parada_ruta_fija: int
    orden: int
    latitud: float
    longitud: float

    class Config:
        from_attributes = True
        
        
class RutaFijaResponse(BaseModel):
    id_ruta_fija: int
    nombre: str
    descripcion: str
    id_conductor: int
    paradas: List[ParadaEstudianteRutaFijaResponse]
    parada_final: Optional[ParadaFinalRutaFijaResponse] = None

    class Config:
        from_attributes = True
        
class EstudianteAConductor(BaseModel):
    id_estudiante: int
    id_usuario_conductor: int  