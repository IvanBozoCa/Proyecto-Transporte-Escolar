from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Date, Time,
    ForeignKey, DateTime, UniqueConstraint, DECIMAL, Float
)
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
from pydantic import BaseModel
# ================= USUARIO =================
class Usuario(Base):
    __tablename__ = "usuarios"
    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True)
    contrasena = Column(Text, nullable=False)
    tipo_usuario = Column(String, nullable=False)
    telefono = Column(Text)

    apoderado = relationship("Apoderado", back_populates="usuario", uselist=False,cascade="all, delete")
    conductor = relationship("Conductor", back_populates="usuario", uselist=False,cascade="all, delete")
    notificaciones = relationship("Notificacion", back_populates="usuario")


# ================= CONDUCTOR =================
class Conductor(Base):
    __tablename__ = "conductores"
    id_conductor = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), unique=True, nullable=False)
    patente = Column(Text)
    modelo_vehiculo = Column(Text)
    id_acompanante = Column(Integer, ForeignKey("acompanantes.id_acompanante"), nullable=True)

    estudiantes = relationship("Estudiante", back_populates="conductor")
    direcciones = relationship("Direccion", back_populates="conductor", cascade="all, delete-orphan")
    usuario = relationship("Usuario", back_populates="conductor")
    rutas = relationship("Ruta", back_populates="conductor")
    vinculaciones = relationship("Vinculo", back_populates="conductor")
    acompanante = relationship("Acompanante", back_populates="conductores")
    ubicaciones = relationship("UbicacionConductor", back_populates="conductor")
    rutas_fijas = relationship("RutaFija", back_populates="conductor", cascade="all, delete-orphan")

# ================= UBICACIÓN CONDUCTOR =================
class UbicacionConductor(Base):
    __tablename__ = "ubicaciones_conductor"

    id_ubicacion = Column(Integer, primary_key=True, index=True)
    id_conductor = Column(Integer, ForeignKey("conductores.id_conductor"))
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    conductor = relationship("Conductor", back_populates="ubicaciones")


# ================= APODERADO =================
class Apoderado(Base):
    __tablename__ = "apoderados"
    id_apoderado = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario",ondelete="CASCADE"), unique=True, nullable=False)
    direccion = Column(Text)

    direcciones = relationship("Direccion", back_populates="apoderado",cascade="all, delete")
    usuario = relationship("Usuario", back_populates="apoderado")
    estudiantes = relationship("Estudiante", back_populates="apoderado")
    vinculaciones = relationship("Vinculo", back_populates="apoderado")


# ================= ESTUDIANTE =================
class Estudiante(Base):
    __tablename__ = "estudiantes"

    id_estudiante = Column(Integer, primary_key=True)
    nombre = Column(Text, nullable=False)
    edad = Column(Integer)
    direccion = Column(Text)
    latitud = Column(DECIMAL(9, 6))
    longitud = Column(DECIMAL(9, 6))
    colegio = Column(Text, nullable=True)
    curso=Column(Text, nullable=True)
    #hora_entrada = Column(Time, nullable=True)  
    activo = Column(Boolean, default=True)
    nombre_apoderado_secundario = Column(String, nullable=True)
    telefono_apoderado_secundario = Column(String, nullable=True)

    id_apoderado = Column(Integer, ForeignKey("apoderados.id_apoderado"))
    id_conductor = Column(Integer, ForeignKey("conductores.id_conductor"), nullable=True)

    conductor = relationship("Conductor", back_populates="estudiantes")
    apoderado = relationship("Apoderado", back_populates="estudiantes")
    paradas = relationship("Parada", back_populates="estudiante")
    asistencias = relationship("Asistencia", back_populates="estudiante")
    rutas_estudiantes = relationship("RutaEstudiante", back_populates="estudiante")
    paradas = relationship("Parada", back_populates="estudiante")
    paradas_fijas = relationship("ParadaRutaFija", back_populates="estudiante", cascade="all, delete-orphan")

# ================= ACOMPAÑANTE =================
class Acompanante(Base):
    __tablename__ = "acompanantes"
    id_acompanante = Column(Integer, primary_key=True)
    nombre = Column(Text, nullable=False)
    telefono = Column(Text)

    rutas = relationship("Ruta", back_populates="acompanante")
    conductores = relationship("Conductor", back_populates="acompanante")


# ================= RUTA =================
class Ruta(Base):
    __tablename__ = "rutas"
    id_ruta = Column(Integer, primary_key=True)
    id_conductor = Column(Integer, ForeignKey("conductores.id_conductor"))
    id_acompanante = Column(Integer, ForeignKey("acompanantes.id_acompanante"))
    fecha = Column(Date, nullable=False)
    #hora_inicio = Column(Time)
    estado = Column(String, default="activa")

    conductor = relationship("Conductor", back_populates="rutas")
    acompanante = relationship("Acompanante", back_populates="rutas")
    paradas = relationship("Parada", back_populates="ruta")
    paradas_estudiantes = relationship("RutaEstudiante", back_populates="ruta")

class RutaEstudiante(Base):
    __tablename__ = "rutas_estudiantes"

    id = Column(Integer, primary_key=True, index=True)
    id_ruta = Column(Integer, ForeignKey("rutas.id_ruta"), nullable=False)
    id_estudiante = Column(Integer, ForeignKey("estudiantes.id_estudiante"), nullable=False)
    orden = Column(Integer, nullable=True)  # Orden opcional de recogida

    ruta = relationship("Ruta", back_populates="paradas_estudiantes")
    estudiante = relationship("Estudiante", back_populates="rutas_estudiantes")

# ================= PARADA =================
class Parada(Base):
    __tablename__ = "paradas"
    id_parada = Column(Integer, primary_key=True)
    id_estudiante = Column(Integer, ForeignKey("estudiantes.id_estudiante"))
    id_ruta = Column(Integer, ForeignKey("rutas.id_ruta"))
    orden = Column(Integer, nullable=False)
    latitud = Column(DECIMAL(9, 6))
    longitud = Column(DECIMAL(9, 6))
    recogido = Column(Boolean, default=False)
    entregado = Column(Boolean, default=False)

    estudiante = relationship("Estudiante", back_populates="paradas")
    ruta = relationship("Ruta", back_populates="paradas")

    __table_args__ = (
        UniqueConstraint("id_estudiante", "id_ruta", "orden", name="uq_estudiante_ruta_orden"),
    )


# ================= ASISTENCIA =================
class Asistencia(Base):
    __tablename__ = "asistencias"

    id_asistencia = Column(Integer, primary_key=True, index=True)
    id_estudiante = Column(Integer, ForeignKey("estudiantes.id_estudiante"))
    fecha = Column(Date, nullable=False)
    asiste = Column(Boolean, nullable=False)

    estudiante = relationship("Estudiante", back_populates="asistencias")


# ================= NOTIFICACIÓN =================
class Notificacion(Base):
    __tablename__ = "notificaciones"
    id_notificacion = Column(Integer, primary_key=True)
    mensaje = Column(Text, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    tipo_envio = Column(Text)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))

    usuario = relationship("Usuario", back_populates="notificaciones")


# ================= VÍNCULO =================
class Vinculo(Base):
    __tablename__ = "vinculos_apoderado_conductor"
    id_vinculo = Column(Integer, primary_key=True)
    id_apoderado = Column(Integer, ForeignKey("apoderados.id_apoderado"))
    id_conductor = Column(Integer, ForeignKey("conductores.id_conductor"))
    fecha_vinculacion = Column(DateTime, default=datetime.utcnow)

    apoderado = relationship("Apoderado", back_populates="vinculaciones")
    conductor = relationship("Conductor", back_populates="vinculaciones")


# ================= DIRECCIÓN =================
class Direccion(Base):
    __tablename__ = "direcciones"
    id_direccion = Column(Integer, primary_key=True, index=True)
    latitud = Column(DECIMAL(9, 6), nullable=False)
    longitud = Column(DECIMAL(9, 6), nullable=False)

    id_apoderado = Column(Integer, ForeignKey("apoderados.id_apoderado"), nullable=True)
    id_conductor = Column(Integer, ForeignKey("conductores.id_conductor"), nullable=True)

    apoderado = relationship("Apoderado", back_populates="direcciones")
    conductor = relationship("Conductor", back_populates="direcciones")
    
    
    
# ================== MODELO: Ruta Fija ==================
class RutaFija(Base):
    __tablename__ = "rutas_fijas"
    id_ruta_fija = Column(Integer, primary_key=True)
    id_conductor = Column(Integer, ForeignKey("conductores.id_conductor"))
    nombre = Column(String, nullable=False)

    conductor = relationship("Conductor", back_populates="rutas_fijas")
    paradas = relationship("ParadaRutaFija", back_populates="ruta", cascade="all, delete-orphan")

class ParadaRutaFija(Base):
    __tablename__ = "paradas_ruta_fija"
    id_parada_ruta_fija = Column(Integer, primary_key=True)
    id_ruta_fija = Column(Integer, ForeignKey("rutas_fijas.id_ruta_fija"))
    id_estudiante = Column(Integer, ForeignKey("estudiantes.id_estudiante"))
    orden = Column(Integer)

    ruta = relationship("RutaFija", back_populates="paradas")
    estudiante = relationship("Estudiante")
