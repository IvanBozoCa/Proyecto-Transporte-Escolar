import os
import firebase_admin
from firebase_admin import credentials

def initialize_firebase():
    if not firebase_admin._apps:
        ruta_credenciales = os.path.join(os.path.dirname(__file__), 'firebase_key.json')

        cred = credentials.Certificate(ruta_credenciales)
        firebase_admin.initialize_app(cred, {
            'databaseURL': os.getenv("FIREBASE_DATABASE_URL", "https://transporte-escolar-543e8-default-rtdb.firebaseio.com/")  # <-- reemplaza esto
        })
