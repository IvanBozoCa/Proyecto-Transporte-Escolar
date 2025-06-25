import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db

# Cargar variables del .env
load_dotenv()

def initialize_firebase():
    if not firebase_admin._apps:
        entorno = os.getenv("render", "local")

        # Trabajamos SOLO en entorno local
        if entorno != "local":
            raise ValueError("Este archivo solo debe usarse en entorno local")

        cred_path = os.getenv("FIREBASE_KEY_PATH")
        db_url = os.getenv("FIREBASE_DATABASE_URL")

        if not cred_path or not os.path.isfile(cred_path):
            raise ValueError(f"No se encontró el archivo de clave de Firebase en la ruta: {cred_path}")

        if not db_url:
            raise ValueError("Falta la URL de la base de datos de Firebase")

        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {
            'databaseURL': db_url
        })
