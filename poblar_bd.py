from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app import models
from faker import Faker
from dotenv import load_dotenv
import os
import random
from datetime import time
from app.auth import hash_contrasena

# Cargar variables de entorno
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Configurar SQLAlchemy
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Instancia de Faker
faker = Faker("es_CL")

# === Crear 2 CONDUCTORES ===
conductores = []
for _ in range(2):
    user = models.Usuario(
        nombre=faker.name(),
        email=faker.unique.email(),
        contrasena=hash_contrasena("conductor123"),
        tipo_usuario="conductor",
        telefono=faker.phone_number()
    )
    session.add(user)
    session.commit()
    conductor = models.Conductor(
        id_usuario=user.id_usuario,
        patente=faker.license_plate(),
        modelo_vehiculo=f"{faker.word().capitalize()} 2024"
    )
    session.add(conductor)
    session.commit()
    conductores.append(conductor)

# === Crear 20 APODERADOS y 20 ESTUDIANTES ===
for i in range(20):
    user = models.Usuario(
        nombre=faker.name(),
        email=faker.unique.email(),
        contrasena=hash_contrasena("apoderado123"),
        tipo_usuario="apoderado",
        telefono=faker.phone_number()
    )
    session.add(user)
    session.commit()

    apoderado = models.Apoderado(
        id_usuario=user.id_usuario,
        direccion=faker.street_address()
    )
    session.add(apoderado)
    session.commit()

    direccion = models.Direccion(
        latitud=float(faker.latitude()),
        longitud=float(faker.longitude()),
        id_apoderado=apoderado.id_apoderado
    )
    session.add(direccion)
    session.commit()

    estudiante = models.Estudiante(
        nombre=faker.first_name(),
        edad=random.randint(6, 12),
        direccion=apoderado.direccion,
        latitud=direccion.latitud,
        longitud=direccion.longitud,
        hora_entrada=time(hour=random.randint(7, 8), minute=random.choice([0, 15, 30, 45])),
        id_apoderado=apoderado.id_apoderado,
        id_conductor=conductores[0].id_conductor if i < 10 else conductores[1].id_conductor,
        nombre_apoderado_secundario=faker.name(),
        telefono_apoderado_secundario=faker.phone_number()
    )
    session.add(estudiante)

session.commit()
print("Base de datos poblada exitosamente sin borrar datos anteriores.")
session.close()
