import os
import firebase_admin
from firebase_admin import credentials, db

def initialize_firebase():
    if not firebase_admin._apps:
        entorno = os.getenv("ENV", "local")

        if entorno == "render":
            cred_path = "/etc/secrets/firebase_key_render.json"
        else:
            cred_path = os.getenv("FIREBASE_KEY_PATH")

        db_url = os.getenv("FIREBASE_DATABASE_URL")

        if not cred_path or not os.path.isfile(cred_path):
            raise ValueError("No se encontró el archivo de clave de Firebase")

        if not db_url:
            raise ValueError("Falta la URL de la base de datos de Firebase")

        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {
            'databaseURL': db_url
        })
