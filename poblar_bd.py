from sqlalchemy.orm import Session
from faker import Faker
from app.database import SessionLocal, engine
from app import models
import random
from datetime import date
from passlib.context import CryptContext
from sqlalchemy import text

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
    models.Estudiante,
    models.Apoderado,
    models.Conductor,
    models.Usuario,
]

print("Eliminando datos existentes...")
for tabla in tablas:
    db.query(tabla).delete()
db.commit()

# Reiniciar secuencias
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
admin3 = models.Usuario(
    nombre="Ivan Bozo",
    email="ivan.bozo@example.com",
    telefono="222222222",
    tipo_usuario="administrador",
    contrasena=hash_contrasena("admin123")
)
db.add_all([admin1, admin2,admin3])
db.commit()

