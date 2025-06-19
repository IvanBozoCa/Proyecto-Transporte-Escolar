from faker import Faker
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
import app.models as models
#from app.utils import hash_contrasena
import random

faker = Faker('es_ES')
session: Session = SessionLocal()

# Eliminar datos previos
session.query(models.ParadaRuta).delete()
session.query(models.Ruta).delete()
session.query(models.Asistencia).delete()
session.query(models.Estudiante).delete()
session.query(models.Apoderado).delete()
session.query(models.Conductor).delete()
session.query(models.Usuario).delete()
session.query(models.Acompanante).delete()
session.commit()

# Crear acompañantes
acompanantes = []
for _ in range(2):
    usuario = models.Usuario(
        nombre=faker.name(),
        email=faker.unique.email(),
  #      contrasena=hash_contrasena("123"),
        tipo_usuario="acompanante",
        telefono=faker.phone_number()
    )
    session.add(usuario)
    session.commit()

    acompanante = models.Acompanante(id_usuario=usuario.id_usuario)
    session.add(acompanante)
    acompanantes.append(acompanante)

session.commit()

# Crear conductores
conductores = []
for i in range(2):
    usuario = models.Usuario(
        nombre=f"Conductor Demo {i+1}",
        email=f"conductor{i+1}@demo.com",
        contrasena=hash_contrasena("123"),
        tipo_usuario="conductor",
        telefono=faker.phone_number()
    )
    session.add(usuario)
    session.commit()

    conductor = models.Conductor(
        id_usuario=usuario.id_usuario,
        patente=f"ABC{i+1}23",
        modelo_vehiculo="Furgón escolar",
        id_acompanante=acompanantes[i].id_acompanante
    )
    session.add(conductor)
    conductores.append(conductor)

session.commit()

# Crear apoderados y estudiantes
for i in range(20):
    usuario = models.Usuario(
        nombre=f"Apoderado Demo {i+1}",
        email=f"apoderado{i+1}@demo.com",
        contrasena=hash_contrasena("123"),
        tipo_usuario="apoderado",
        telefono=faker.phone_number()
    )
    session.add(usuario)
    session.commit()

    apoderado = models.Apoderado(
        id_usuario=usuario.id_usuario,
        rut_apoderado=faker.unique.ssn(),
        nombre_apoderado=usuario.nombre,
        telefono=usuario.telefono,
        correo=usuario.email,
        direccion=faker.address(),
        nombre_apoderado_secundario=faker.name(),
        telefono_secundario=faker.phone_number(),
        correo_secundario=faker.email()
    )
    session.add(apoderado)
    session.commit()

    direccion = models.Direccion(
        id_apoderado=apoderado.id_apoderado,
        calle=faker.street_name(),
        numero=faker.building_number(),
        comuna=faker.city(),
        latitud=float(faker.latitude()),
        longitud=float(faker.longitude())
    )
    session.add(direccion)
    session.commit()

    estudiante = models.Estudiante(
        nombre=f"Estudiante {i+1}",
        edad=random.randint(6, 12),
        direccion=direccion.calle + " " + direccion.numero,
        curso=random.choice(["1° Básico", "2° Básico", "3° Básico"]),
        colegio=faker.company(),
        hora_entrada="08:00",
        id_apoderado=apoderado.id_apoderado,
        id_conductor=random.choice(conductores).id_conductor
    )
    session.add(estudiante)
    session.commit()

    # Asistencias para hoy y mañana
    session.add_all([
        models.Asistencia(id_estudiante=estudiante.id_estudiante, fecha=date.today(), asiste=random.choice([True, False])),
        models.Asistencia(id_estudiante=estudiante.id_estudiante, fecha=date.today() + timedelta(days=1), asiste=True)
    ])

session.commit()

# Crear rutas base con paradas
for conductor in conductores:
    ruta = models.Ruta(nombre=f"Ruta asignada {conductor.id_conductor}", id_conductor=conductor.id_conductor)
    session.add(ruta)
    session.commit()

    estudiantes = session.query(models.Estudiante).filter_by(id_conductor=conductor.id_conductor).all()
    for idx, estudiante in enumerate(estudiantes):
        parada = models.ParadaRuta(
            id_ruta=ruta.id_ruta,
            id_estudiante=estudiante.id_estudiante,
            orden=idx + 1
        )
        session.add(parada)

session.commit()

# Crear 2 administradores de forma manual
admin1 = models.Usuario(
    nombre="Ivan Bozo",
    email="ivan@example.com",
    contrasena=hash_contrasena("admin123"),
    tipo_usuario="administrador",
    telefono="+56911111111"
)

admin2 = models.Usuario(
    nombre="Lukas Flores",
    email="lukas@example.com",
    contrasena=hash_contrasena("admin123"),
    tipo_usuario="administrador",
    telefono="+56922222222"
)

session.add_all([admin1, admin2])
session.commit()
