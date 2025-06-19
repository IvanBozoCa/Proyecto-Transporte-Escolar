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
from sqlalchemy import text

print("Sincronizando secuencias con las tablas...")

tablas_y_secuencias = {
    "usuarios": "usuarios_id_usuario_seq",
    "acompanantes": "acompanantes_id_acompanante_seq",
    "apoderados": "apoderados_id_apoderado_seq",
    "conductores": "conductores_id_conductor_seq",
    "notificaciones": "notificaciones_id_notificacion_seq",
    "ubicaciones_conductor": "ubicaciones_conductor_id_ubicacion_seq",
    "estudiantes": "estudiantes_id_estudiante_seq",
    "rutas": "rutas_id_ruta_seq",
    "vinculos_apoderado_conductor": "vinculos_apoderado_conductor_id_vinculo_seq",
    "direcciones": "direcciones_id_direccion_seq",
    "asistencias": "asistencias_id_asistencia_seq",
    "paradas_ruta_fija": "paradas_ruta_fija_id_parada_ruta_fija_seq",
    "paradas": "paradas_id_parada_seq",
    "rutas_estudiantes": "rutas_estudiantes_id_seq",
    "rutas_fijas": "rutas_fijas_id_ruta_fija_seq"
}

for tabla, secuencia in tablas_y_secuencias.items():
    try:
        db.execute(text(f"""
            SELECT setval('{secuencia}', COALESCE((SELECT MAX(id) FROM {tabla}), 1), true)
        """.replace("id", f"id_{tabla[:-1]}")))  # Ajuste automático de nombre de columna
        print(f" Secuencia {secuencia} sincronizada con {tabla}")
    except Exception as e:
        print(f" Error al sincronizar {secuencia}: {e}")

db.commit()
