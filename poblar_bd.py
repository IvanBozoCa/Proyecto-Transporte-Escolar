from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app import models
from faker import Faker
from dotenv import load_dotenv
import os
import random
from datetime import date, time

# Cargar variables de entorno
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Configurar SQLAlchemy
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Crear las tablas si no existen
Base.metadata.create_all(bind=engine)

# Instancia de Faker
faker = Faker()

# 🔄 Limpiar base (orden correcto)
try:
    session.query(models.Parada).delete()
    session.query(models.Ruta).delete()
    session.query(models.Vinculo).delete()
    session.query(models.Estudiante).delete()
    session.query(models.Direccion).delete()
    session.query(models.Apoderado).delete()
    session.query(models.Conductor).delete()
    session.query(models.Usuario).delete()
    session.commit()
    print("Base limpiada correctamente.")
except Exception as e:
    session.rollback()
    print("Error al limpiar la base:", e)

# === Crear usuarios ===
usuarios = []
for _ in range(2):  # Conductores
    usuarios.append(models.Usuario(
        nombre=faker.name(),
        email=faker.unique.email(),
        contrasena="1234",
        tipo_usuario="conductor",
        telefono=faker.phone_number()
    ))

for _ in range(2):  # Apoderados
    usuarios.append(models.Usuario(
        nombre=faker.name(),
        email=faker.unique.email(),
        contrasena="1234",
        tipo_usuario="apoderado",
        telefono=faker.phone_number()
    ))

session.add_all(usuarios)
session.commit()

# === Crear conductores ===
conductores = []
for u in usuarios:
    if u.tipo_usuario == "conductor":
        c = models.Conductor(
            id_usuario=u.id_usuario,
            patente=faker.license_plate(),
            modelo_vehiculo=faker.word().capitalize() + " 2024",
            codigo_vinculacion=faker.unique.uuid4()[:8]
        )
        conductores.append(c)

session.add_all(conductores)
session.commit()

# === Crear apoderados y direcciones ===
apoderados = []
for u in usuarios:
    if u.tipo_usuario == "apoderado":
        a = models.Apoderado(
            id_usuario=u.id_usuario,
            direccion=faker.street_address()
        )
        session.add(a)
        session.commit()
        apoderados.append(a)

        # Dirección geográfica
        direccion = models.Direccion(
            latitud=float(faker.latitude()),
            longitud=float(faker.longitude()),
            id_apoderado=a.id_apoderado
        )
        session.add(direccion)

session.commit()

# === Vincular apoderados al primer conductor ===
for a in apoderados:
    v = models.Vinculo(
        id_apoderado=a.id_apoderado,
        id_conductor=conductores[0].id_conductor
    )
    session.add(v)

session.commit()

# === Crear estudiantes ===
estudiantes = []
for a in apoderados:
    for _ in range(2):  # 2 por apoderado
        e = models.Estudiante(
            nombre=faker.first_name(),
            edad=random.randint(6, 12),
            direccion=faker.street_address(),
            latitud=float(faker.latitude()),
            longitud=float(faker.longitude()),
            id_apoderado=a.id_apoderado,
            id_conductor=conductores[0].id_conductor
        )
        estudiantes.append(e)

session.add_all(estudiantes)
session.commit()

# === Crear una ruta y paradas ===
ruta = models.Ruta(
    id_conductor=conductores[0].id_conductor,
    id_acompanante=None,
    fecha=date.today(),
    hora_inicio=time(7, 30),
    estado="activa"
)
session.add(ruta)
session.commit()

# Paradas según estudiantes
for orden, e in enumerate(estudiantes, start=1):
    p = models.Parada(
        id_estudiante=e.id_estudiante,
        id_ruta=ruta.id_ruta,
        orden=orden,
        latitud=e.latitud,
        longitud=e.longitud,
        recogido=False,
        entregado=False
    )
    session.add(p)

session.commit()
print("Base de datos poblada exitosamente.")
session.close()
