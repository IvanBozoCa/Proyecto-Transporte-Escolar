import psycopg2

# Conexión directa
conn = psycopg2.connect(
    host="localhost",
    port="5432",
    dbname="transporte_escolar",
    user="postgres",
    password="Simon"
)
cursor = conn.cursor()

# Borra todas las tablas con CASCADE
print("Eliminando todas las tablas con CASCADE...")
cursor.execute("""
    DROP TABLE IF EXISTS 
        direcciones,
        estudiantes,
        apoderados,
        conductores,
        usuarios,
        acompanantes,
        rutas,
        paradas,
        asistencias,
        notificaciones,
        vinculos_apoderado_conductor
    CASCADE;
""")
conn.commit()
print("Tablas eliminadas correctamente.")

cursor.close()
conn.close()

from app.database import engine
from app.models import Base

Base.metadata.create_all(bind=engine)