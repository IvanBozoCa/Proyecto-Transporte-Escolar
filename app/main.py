import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app import models
from app.routers import login, usuarios, gestion_admin, conductor, rutas, apoderado,firebase_cosas
from dotenv import load_dotenv

# Cargar variables de entorno desde un archivo .env (opcional)
load_dotenv()

# Crear tablas
models.Base.metadata.create_all(bind=engine)

# Crear app
app = FastAPI()

# Detectar entorno
ENV = os.getenv("ENV", "development")  # valor por defecto: development

# Configurar CORS dinámico
if ENV == "production":
    allowed_origins = [
        os.getenv("FRONTEND_URL", "https://frontend-escolar.vercel.app")  # puedes setear esta variable en Render
    ]
else:
    allowed_origins = ["*"]  # modo desarrollo local, más permisivo

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(login.router, prefix="/auth", tags=["Autenticación"])
app.include_router(firebase_cosas.router, prefix="/firebase", tags=["Firebase"])
app.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"])
app.include_router(gestion_admin.router, prefix="/admin", tags=["Administrador"])
app.include_router(conductor.router, prefix="/conductor", tags=["Conductor"])
app.include_router(apoderado.router, prefix="/apoderado", tags=["Apoderado"])
app.include_router(rutas.router, prefix="/rutas-fijas", tags=["Rutas Fijas"])
@app.get("/")
def root():
    return {"mensaje": "API para gestión de transporte escolar"}
