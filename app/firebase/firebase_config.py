from dotenv import load_dotenv
import os
import json
import firebase_admin
from firebase_admin import credentials, db

# Cargar variables de entorno
load_dotenv()

def initialize_firebase():
    if not firebase_admin._apps:
        cred_json = os.getenv("FIREBASE_KEY_JSON")
        database_url = os.getenv("FIREBASE_DATABASE_URL")

        if not cred_json:
            raise ValueError("La variable de entorno FIREBASE_KEY_JSON no está configurada")

        if not database_url:
            raise ValueError("La variable de entorno FIREBASE_DATABASE_URL no está configurada")

        cred_dict = json.loads(cred_json)
        cred = credentials.Certificate(cred_dict)

        firebase_admin.initialize_app(cred, {
            'databaseURL': database_url
        })
