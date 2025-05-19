from fastapi import FastAPI
from app import models, database
from app.routers import login, usuarios,direcciones,estudiantes,conductor

# http://127.0.0.1:8000/docs#/

app = FastAPI()

# Crea todas las tablas de la base de datos al iniciar la app
models.Base.metadata.create_all(bind=database.engine)

# Montar los routers
app.include_router(login.router)
app.include_router(usuarios.router)
app.include_router(estudiantes.router)
app.include_router(direcciones.router)
app.include_router(conductor.router)
@app.get("/")
def root():
    return {"mensaje": "API de Transporte Escolar"}
