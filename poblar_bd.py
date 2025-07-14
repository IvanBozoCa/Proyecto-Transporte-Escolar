from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models
from sqlalchemy import text
from passlib.context import CryptContext

db: Session = SessionLocal()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_contrasena(contrasena: str) -> str:
    return pwd_context.hash(contrasena)

# 1. Borrado de datos en orden seguro
tablas = [
    models.TokenFirebase,
    models.ParadaRutaFija,
    models.RutaFija,
    models.Vinculo,
    models.Notificacion,
    models.Asistencia,
    models.Parada,
    models.RutaEstudiante,
    models.Ruta,
    models.UbicacionConductor,
    models.Estudiante,
    models.Apoderado,
    models.Conductor,
    models.Usuario,
]

print("Eliminando datos existentes...")
for tabla in tablas:
    db.query(tabla).delete()
db.commit()

# 2. Reiniciar secuencias
secuencias = [
    "usuarios_id_usuario_seq",
    "conductores_id_conductor_seq",
    "ubicaciones_conductor_id_ubicacion_seq",
    "apoderados_id_apoderado_seq",
    "estudiantes_id_estudiante_seq",
    "acompanantes_id_acompanante_seq",
    "rutas_id_ruta_seq",
    "rutas_estudiantes_id_seq",
    "paradas_id_parada_seq",
    "asistencias_id_asistencia_seq",
    "notificaciones_id_notificacion_seq",
    "vinculos_apoderado_conductor_id_vinculo_seq",
    "rutas_fijas_id_ruta_fija_seq",
    "paradas_ruta_fija_id_parada_ruta_fija_seq",
    "token_firebase_id_token_seq"
]

print("Reiniciando secuencias...")
for secuencia in secuencias:
    try:
        db.execute(text(f"ALTER SEQUENCE {secuencia} RESTART WITH 1"))
        print(f"Secuencia reiniciada: {secuencia}")
    except Exception as e:
        print(f"Error al reiniciar {secuencia}: {e}")
db.commit()

# 3. Crear administradores SIN ID manual
print("Creando administradores...")
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
    email="ivan@gmail.com",
    telefono="333333333",
    tipo_usuario="administrador",
    contrasena=hash_contrasena("admin123")
)

db.add_all([admin1, admin2, admin3])
db.commit()

print("Todo listo: base de datos limpia y administradores creados.")
