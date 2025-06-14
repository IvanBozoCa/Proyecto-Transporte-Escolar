from fastapi import FastAPI
from app import models, database
from app.routers import login, usuarios, gestion_admin,rutas,apoderado,conductor


# http://127.0.0.1:8000/docs#/
app = FastAPI()

# Crear todas las tablas en la base de datos
models.Base.metadata.create_all(bind=database.engine)

# Incluir routers activos
app.include_router(login.router)
app.include_router(usuarios.router)
app.include_router(gestion_admin.router) 
app.include_router(rutas.router)
app.include_router(conductor.router)
app.include_router(apoderado.router)

@app.get("/")
def root():
    return {"mensaje": "API de Transporte Escolar"}
