from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Datos de conexión
DB_USER = "postgres"
DB_PASSWORD = "Simon"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "transporte_escolar"

DATABASE_URL = f"postgresql://transporte_escolar_db_user:tA9Nx575L4SBJnDaQ8B7XBBeV5p1U3uK@dpg-d0qjue15pdvs73alno20-a.oregon-postgres.render.com/transporte_escolar_db"
#f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Conexión a la base de datos
engine = create_engine(DATABASE_URL)

# Sesiones de trabajo
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa (para ORM)
Base = declarative_base()

# Dependencia para usar en los endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
