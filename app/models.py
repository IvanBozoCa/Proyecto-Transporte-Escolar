from sqlalchemy import Column, Integer, String, Text, Boolean, Date, Time, ForeignKey, DateTime, UniqueConstraint, DECIMAL,Float, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class Usuario(Base):
    __tablename__ = "usuarios"
    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True)
    contrasena = Column(Text, nullable=False)
    tipo_usuario = Column(String, nullable=False)
    telefono = Column(Text)

    apoderado = relationship("Apoderado", back_populates="usuario", uselist=False)
    conductor = relationship("Conductor", back_populates="usuario", uselist=False)
    notificaciones = relationship("Notificacion", back_populates="usuario")


class Conductor(Base):
    __tablename__ = "conductores"
    id_conductor = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), unique=True, nullable=False)
    patente = Column(Text)
    modelo_vehiculo = Column(Text)
    codigo_vinculacion = Column(String, unique=True)
    id_acompanante = Column(Integer, ForeignKey("acompanantes.id_acompanante"), nullable=True)

    estudiantes = relationship("Estudiante", back_populates="conductor")
    direcciones = relationship("Direccion", back_populates="conductor", cascade="all, delete-orphan")
    usuario = relationship("Usuario", back_populates="conductor")
    rutas = relationship("Ruta", back_populates="conductor")
    vinculaciones = relationship("Vinculo", back_populates="conductor")
    acompanante = relationship("Acompanante", back_populates="conductores")

class UbicacionConductor(Base):
    __tablename__ = "ubicaciones_conductor"

    id_ubicacion = Column(Integer, primary_key=True, index=True)
    id_conductor = Column(Integer, ForeignKey("conductores.id_conductor"))
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    conductor = relationship("Conductor", backref="ubicaciones")


class Apoderado(Base):
    __tablename__ = "apoderados"
    id_apoderado = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), unique=True, nullable=False)
    direccion = Column(Text)
    
    direcciones = relationship("Direccion", back_populates="apoderado", cascade="all, delete-orphan")
    usuario = relationship("Usuario", back_populates="apoderado")
    estudiantes = relationship("Estudiante", back_populates="apoderado")
    vinculaciones = relationship("Vinculo", back_populates="apoderado")

class Estudiante(Base):
    __tablename__ = "estudiantes"
    
    id_estudiante = Column(Integer, primary_key=True)
    nombre = Column(Text, nullable=False)
    edad = Column(Integer)

    # Datos de localización
    direccion = Column(Text)  # Texto libre (puede mantenerse si deseas mostrar algo legible)
    latitud = Column(DECIMAL(9,6))
    longitud = Column(DECIMAL(9,6))

    # Nueva información solicitada
    colegio = Column(Text, nullable=True)
    hora_ingreso = Column(Time, nullable=True)
    activo = Column(Boolean, default=True)
    nombre_apoderado_secundario = Column(String, nullable=True)
    telefono_apoderado_secundario = Column(String, nullable=True)
    # Relaciones
    id_apoderado = Column(Integer, ForeignKey("apoderados.id_apoderado"))
    id_conductor = Column(Integer, ForeignKey("conductores.id_conductor"), nullable=True)


    conductor = relationship("Conductor", back_populates="estudiantes")
    apoderado = relationship("Apoderado", back_populates="estudiantes")
    paradas = relationship("Parada", back_populates="estudiante")
    asistencias = relationship("Asistencia", back_populates="estudiante")



class Acompanante(Base):
    __tablename__ = "acompanantes"
    id_acompanante = Column(Integer, primary_key=True)
    nombre = Column(Text, nullable=False)
    telefono = Column(Text)

    rutas = relationship("Ruta", back_populates="acompanante")
    conductores = relationship("Conductor", back_populates="acompanante")

class Ruta(Base):
    __tablename__ = "rutas"
    id_ruta = Column(Integer, primary_key=True)
    id_conductor = Column(Integer, ForeignKey("conductores.id_conductor"))
    id_acompanante = Column(Integer, ForeignKey("acompanantes.id_acompanante"))
    fecha = Column(Date, nullable=False)
    hora_inicio = Column(Time)
    estado = Column(String, default="activa")

    conductor = relationship("Conductor", back_populates="rutas")
    acompanante = relationship("Acompanante", back_populates="rutas")
    paradas = relationship("Parada", back_populates="ruta")

class Parada(Base):
    __tablename__ = "paradas"
    id_parada = Column(Integer, primary_key=True)
    id_estudiante = Column(Integer, ForeignKey("estudiantes.id_estudiante"))
    id_ruta = Column(Integer, ForeignKey("rutas.id_ruta"))
    orden = Column(Integer, nullable=False)
    latitud = Column(DECIMAL(9,6))
    longitud = Column(DECIMAL(9,6))
    recogido = Column(Boolean, default=False)
    entregado = Column(Boolean, default=False)

    estudiante = relationship("Estudiante", back_populates="paradas")
    ruta = relationship("Ruta", back_populates="paradas")

class Asistencia(Base):
    __tablename__ = "asistencias"

    id_asistencia = Column(Integer, primary_key=True, index=True)
    id_estudiante = Column(Integer, ForeignKey("estudiantes.id_estudiante"))
    fecha = Column(Date, nullable=False)
    asiste = Column(Boolean, nullable=False)

    estudiante = relationship("Estudiante", backref="asistencias")


class Notificacion(Base):
    __tablename__ = "notificaciones"
    id_notificacion = Column(Integer, primary_key=True)
    mensaje = Column(Text, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    tipo_envio = Column(Text)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))

    usuario = relationship("Usuario", back_populates="notificaciones")

class Vinculo(Base):
    __tablename__ = "vinculos_apoderado_conductor"
    id_vinculo = Column(Integer, primary_key=True)
    id_apoderado = Column(Integer, ForeignKey("apoderados.id_apoderado"))
    id_conductor = Column(Integer, ForeignKey("conductores.id_conductor"))
    fecha_vinculacion = Column(DateTime, default=datetime.utcnow)

    apoderado = relationship("Apoderado", back_populates="vinculaciones")
    conductor = relationship("Conductor", back_populates="vinculaciones")


class Direccion(Base):
    __tablename__ = "direcciones"
    id_direccion = Column(Integer, primary_key=True, index=True)
    latitud = Column(DECIMAL(9,6), nullable=False)
    longitud = Column(DECIMAL(9,6), nullable=False)

    id_apoderado = Column(Integer, ForeignKey("apoderados.id_apoderado"), nullable=True)
    id_conductor = Column(Integer, ForeignKey("conductores.id_conductor"), nullable=True)

    apoderado = relationship("Apoderado", back_populates="direcciones")
    conductor = relationship("Conductor", back_populates="direcciones")
