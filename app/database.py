from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Datos de conexión
DB_USER = "transporte_escolar_db_c85j_user"
DB_PASSWORD = "tim8btq8OGz8uydUnEcinFWElGM2Wm0g"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "transporte_escolar_db_c85j"

DATABASE_URL = f"postgresql://transporte_escolar_db_c85j_user:tim8btq8OGz8uydUnEcinFWElGM2Wm0g@dpg-d0v6u795pdvs7385thd0-a.oregon-postgres.render.com/transporte_escolar_db_c85j"
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
