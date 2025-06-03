import psycopg2

from app.database import engine
from app.models import Base

# Conexión directa
conn = psycopg2.connect(f"postgresql://transporte_escolar_db_user:tA9Nx575L4SBJnDaQ8B7XBBeV5p1U3uK@dpg-d0qjue15pdvs73alno20-a.oregon-postgres.render.com/transporte_escolar_db"
)
cursor = conn.cursor()
#f"postgresql://transporte_escolar_db_user:tA9Nx575L4SBJnDaQ8B7XBBeV5p1U3uK@dpg-d0qjue15pdvs73alno20-a.oregon-postgres.render.com/transporte_escolar_db"
# Borra todas las tablas con CASCADEpostgresql://transporte_escolar_db_user:tA9Nx575L4SBJnDaQ8B7XBBeV5p1U3uK@dpg-d0qjue15pdvs73alno20-a.oregon-postgres.render.com/transporte_escolar_db
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

Base.metadata.create_all(bind=engine)