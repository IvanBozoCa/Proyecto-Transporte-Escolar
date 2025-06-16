from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app import models
from app.routers import login, usuarios, gestion_admin, conductor, rutas

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas
app.include_router(login.router, prefix="/auth", tags=["Autenticación"])
app.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"])
app.include_router(gestion_admin.router, prefix="/admin", tags=["Administrador"])
app.include_router(conductor.router, prefix="/conductor", tags=["Conductor"])
app.include_router(rutas.router, prefix="/rutas", tags=["Rutas"])

@app.get("/")
def root():
    return {"mensaje": "API para gestión de transporte escolar"}
