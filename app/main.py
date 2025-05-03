from fastapi import FastAPI
from app import models, database
from app.routers import login, usuarios 

app = FastAPI()

# Crea todas las tablas de la base de datos al iniciar la app
models.Base.metadata.create_all(bind=database.engine)

# Montar los routers
app.include_router(login.router)
app.include_router(usuarios.router)

@app.get("/")
def root():
    return {"mensaje": "API de Transporte Escolar - Autenticación lista"}
