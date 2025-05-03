from sqlalchemy import Column, Integer, String, Text, Boolean, Date, Time, ForeignKey, DateTime, UniqueConstraint, DECIMAL
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

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

    usuario = relationship("Usuario", back_populates="conductor")
    rutas = relationship("Ruta", back_populates="conductor")
    vinculaciones = relationship("Vinculo", back_populates="conductor")

class Apoderado(Base):
    __tablename__ = "apoderados"
    id_apoderado = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), unique=True, nullable=False)
    direccion = Column(Text)

    usuario = relationship("Usuario", back_populates="apoderado")
    estudiantes = relationship("Estudiante", back_populates="apoderado")
    vinculaciones = relationship("Vinculo", back_populates="apoderado")

class Estudiante(Base):
    __tablename__ = "estudiantes"
    id_estudiante = Column(Integer, primary_key=True)
    nombre = Column(Text, nullable=False)
    edad = Column(Integer)
    direccion = Column(Text)
    latitud = Column(DECIMAL(9,6))
    longitud = Column(DECIMAL(9,6))
    id_apoderado = Column(Integer, ForeignKey("apoderados.id_apoderado"))

    apoderado = relationship("Apoderado", back_populates="estudiantes")
    paradas = relationship("Parada", back_populates="estudiante")
    asistencias = relationship("Asistencia", back_populates="estudiante")

class Acompanante(Base):
    __tablename__ = "acompanantes"
    id_acompanante = Column(Integer, primary_key=True)
    nombre = Column(Text, nullable=False)
    telefono = Column(Text)

    rutas = relationship("Ruta", back_populates="acompanante")

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
    id_asistencia = Column(Integer, primary_key=True)
    id_estudiante = Column(Integer, ForeignKey("estudiantes.id_estudiante"))
    fecha = Column(Date, nullable=False)
    asistencia = Column(Boolean, default=True)
    registrada = Column(DateTime, default=datetime.utcnow)

    estudiante = relationship("Estudiante", back_populates="asistencias")

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
