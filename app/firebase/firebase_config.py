import os
import json
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db

load_dotenv()

def initialize_firebase():
    if not firebase_admin._apps:
        cred_json = os.getenv("FIREBASE_KEY_JSON")
        database_url = os.getenv("FIREBASE_DATABASE_URL")

        if not cred_json or not database_url:
            raise ValueError("Faltan variables de entorno")

        try:
            cred_dict = json.loads(cred_json)
        except json.JSONDecodeError:
            raise ValueError("El contenido de FIREBASE_KEY_JSON no es un JSON válido")

        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred, {
            'databaseURL': database_url
        })