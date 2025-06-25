import firebase_admin
from firebase_admin import credentials, messaging
import os

# Ruta relativa al archivo JSON
ruta_credenciales = "C:/Users/Ivan/Desktop/universidad/año 2025/curso proyecto de tesis/Proyecto/transporte_backend/app/firebase/firebase_key.json"
def initialize_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(ruta_credenciales)
        firebase_admin.initialize_app(cred, {
            "databaseURL": "https://transporte-escolar-543e8-default-rtdb.firebaseio.com/"
        })