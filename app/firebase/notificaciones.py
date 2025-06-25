from firebase_admin import messaging, db
from app.firebase.firebase_config import initialize_firebase
from datetime import datetime
# Asegura inicialización de Firebase al importar este archivo
initialize_firebase()

def enviar_notificacion(titulo: str, cuerpo: str, token: str):
    mensaje = messaging.Message(
        notification=messaging.Notification(
            title=titulo,
            body=cuerpo
        ),
        token=token
    )
    try:
        respuesta = messaging.send(mensaje)
        print(f"Notificación enviada con éxito: {respuesta}")
    except Exception as e:
        print(f"Error al enviar notificación: {e}")


def enviar_ubicacion_conductor(id_conductor: int, latitud: float, longitud: float):
    ref = db.reference(f"ubicaciones/conductor_{id_conductor}")
    ref.set({
        "latitud": latitud,
        "longitud": longitud
    })

# notificaciones.py

def enviar_finalizacion_ruta(id_conductor: int):
    ref = db.reference(f"rutas_finalizadas/conductor_{id_conductor}")
    ref.set({
        "mensaje": "Ruta finalizada",
        "finalizada": True,
        "timestamp": datetime.now().isoformat()
    })


def eliminar_ubicacion_conductor(id_conductor: int):
    ref = db.reference(f"ubicaciones/conductor_{id_conductor}")
    ref.delete()
    
def enviar_notificacion_inicio_ruta(titulo: str, cuerpo: str, tokens: list[str]):
    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=titulo,
            body=cuerpo,
        ),
        tokens=tokens
    )
    response = messaging.send_multicast(message)
    return response