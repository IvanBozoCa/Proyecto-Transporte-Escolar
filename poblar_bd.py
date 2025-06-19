from sqlalchemy.orm import Session
from faker import Faker
from app.database import SessionLocal, engine
from app import models
import random
from datetime import date
from passlib.context import CryptContext

fake = Faker()
db: Session = SessionLocal()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_contrasena(contrasena: str) -> str:
    return pwd_context.hash(contrasena)

# Borrar datos existentes
tablas = [
    models.Notificacion,
    models.Asistencia,
    models.Parada,
    models.RutaEstudiante,
    models.Ruta,
    models.ParadaRutaFija,
    models.RutaFija,
    models.Vinculo,
    models.Direccion,
    models.Estudiante,
    models.Apoderado,
    models.Conductor,
    models.Usuario,
]
colegios_falsos = [
    "Colegio Bicentenario Santa María",
    "Liceo Técnico Profesional Andes",
    "Escuela República de Chile",
    "Colegio San Martín",
    "Instituto La Esperanza"
]

# Lista de cursos posibles
cursos_falsos = [
    "1° Básico", "2° Básico", "3° Básico", "4° Básico",
    "5° Básico", "6° Básico", "7° Básico", "8° Básico",
    "1° Medio", "2° Medio", "3° Medio", "4° Medio"
]

print("Eliminando datos existentes...")
for tabla in tablas:
    db.query(tabla).delete()
db.commit()

# Crear administradores manualmente
admin1 = models.Usuario(
    nombre="ivan",
    email="ivan@example.com",
    telefono="111111111",
    tipo_usuario="administrador",
    contrasena=hash_contrasena("admin123")
)

admin2 = models.Usuario(
    nombre="lukas",
    email="lukas@example.com",
    telefono="222222222",
    tipo_usuario="administrador",
    contrasena=hash_contrasena("admin123")
)

db.add_all([admin1, admin2])
db.commit()

# Crear conductores
conductores = []
for i in range(2):
    usuario = models.Usuario(
        nombre=fake.name(),
        email=fake.unique.email(),
        telefono=fake.phone_number(),
        tipo_usuario="conductor",
        contrasena=hash_contrasena("conductor123")
    )
    db.add(usuario)
    db.flush()

    conductor = models.Conductor(
        id_usuario=usuario.id_usuario,
        patente=fake.license_plate(),
        modelo_vehiculo=fake.word().capitalize()
    )
    db.add(conductor)
    db.flush()

    direccion = models.Direccion(
        id_conductor=conductor.id_conductor,
        latitud=float(fake.latitude()),
        longitud=float(fake.longitude())
    )
    db.add(direccion)
    conductores.append(conductor)

db.commit()

# Crear apoderados y estudiantes
for i in range(10):
    usuario = models.Usuario(
        nombre=fake.name(),
        email=fake.unique.email(),
        telefono=fake.phone_number(),
        tipo_usuario="apoderado",
        contrasena=hash_contrasena("apoderado123")
    )
    db.add(usuario)
    db.flush()

    apoderado = models.Apoderado(
        id_usuario=usuario.id_usuario
    )
    db.add(apoderado)
    db.flush()

    direccion = models.Direccion(
        id_apoderado=apoderado.id_apoderado,
        latitud=float(fake.latitude()),
        longitud=float(fake.longitude())
    )
    db.add(direccion)
    db.flush()

    # Crear estudiante asociado
    estudiante = models.Estudiante(
        nombre=fake.first_name(),
        direccion=fake.street_address(),
        latitud=direccion.latitud,
        longitud=direccion.longitud,
        colegio=random.choice(colegios_falsos),
        curso=random.choice(cursos_falsos),
        id_apoderado=apoderado.id_apoderado,
        edad= random.randint(6, 17)
    )
    db.add(estudiante)
    db.flush()

    # Registrar asistencia positiva para hoy
    asistencia = models.Asistencia(
        id_estudiante=estudiante.id_estudiante,
        fecha=date.today(),
        asiste=True
    )
    db.add(asistencia)
db.commit()
from sqlalchemy import text

print("Base de datos poblada exitosamente.")

from sqlalchemy import text

secuencias = [
    "usuarios_id_usuario_seq",
    "acompanantes_id_acompanante_seq",
    "apoderados_id_apoderado_seq",
    "conductores_id_conductor_seq",
    "notificaciones_id_notificacion_seq",
    "ubicaciones_conductor_id_ubicacion_seq",
    "estudiantes_id_estudiante_seq",
    "rutas_id_ruta_seq",
    "vinculos_apoderado_conductor_id_vinculo_seq",
    "direcciones_id_direccion_seq",
    "asistencias_id_asistencia_seq",
    "paradas_ruta_fija_id_parada_ruta_fija_seq",
    "paradas_id_parada_seq",
    "rutas_estudiantes_id_seq",
    "rutas_fijas_id_ruta_fija_seq"
]

print("Reiniciando secuencias de IDs...")
for secuencia in secuencias:
    try:
        db.execute(text(f"ALTER SEQUENCE {secuencia} RESTART WITH 1"))
        print(f"Secuencia reiniciada: {secuencia}")
    except Exception as e:
        print(f"Error al reiniciar {secuencia}: {e}")

db.commit()
from sqlalchemy import text

# === Ajustar secuencias de IDs para evitar conflictos con claves duplicadas ===
secuencias = [
    ('usuarios_id_usuario_seq', 'usuarios', 'id_usuario'),
    ('apoderados_id_apoderado_seq', 'apoderados', 'id_apoderado'),
    ('conductores_id_conductor_seq', 'conductores', 'id_conductor'),
    ('estudiantes_id_estudiante_seq', 'estudiantes', 'id_estudiante'),
    ('direcciones_id_direccion_seq', 'direcciones', 'id_direccion'),
    ('asistencias_id_asistencia_seq', 'asistencias', 'id_asistencia'),
    ('rutas_fijas_id_ruta_fija_seq', 'rutas_fijas', 'id_ruta_fija'),
    ('paradas_ruta_fija_id_parada_ruta_fija_seq', 'paradas_ruta_fija', 'id_parada_ruta_fija'),
    ('rutas_id_ruta_seq', 'rutas', 'id_ruta'),
    ('paradas_id_parada_seq', 'paradas', 'id_parada'),
    ('notificaciones_id_notificacion_seq', 'notificaciones', 'id_notificacion'),
    # Agrega más si tienes nuevas tablas con claves autoincrementales
]

print("Ajustando secuencias de ID...")
for secuencia, tabla, campo in secuencias:
    db.execute(text(f"""
        SELECT setval('{secuencia}', COALESCE((SELECT MAX({campo}) FROM {tabla}), 1));
    """))
db.commit()
print("Secuencias ajustadas correctamente.")
