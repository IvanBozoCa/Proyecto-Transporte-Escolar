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
    
def enviar_inicio_ruta(id_conductor: int):
    ref = db.reference(f"rutas_activas/conductor_{id_conductor}")
    ref.set({
        "mensaje": "Ruta iniciada",
        "activa": True,
        "timestamp": datetime.now().isoformat()
    })
    
def eliminar_inicio_ruta(id_conductor: int):
    ref = db.reference(f"rutas_activas/conductor_{id_conductor}")
    ref.delete()

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
    print(f"Notificación grupal enviada. Éxito: {response.success_count}, Fallos: {response.failure_count}")
    
    for idx, resp in enumerate(response.responses):
        if not resp.success:
            print(f"Error en token {tokens[idx]}: {resp.exception}")
    
    return response

def marcar_ruta_activa(id_conductor: int):
    ref = db.reference(f"rutas_activas/conductor_{id_conductor}")
    ref.set({
        "mensaje": "Ruta activa",
        "activa": True,
        "timestamp": datetime.now().isoformat()
    })
    
def eliminar_ruta_activa(id_conductor: int):
    ref = db.reference(f"rutas_activas/conductor_{id_conductor}")
    ref.delete()
    
def enviar_notificacion_recogida_estudiante(nombre_estudiante: str, token: str, nombre_conductor: str = ""):
    cuerpo = f"Tu estudiante {nombre_estudiante} ha sido recogido por el conductor {nombre_conductor}." if nombre_conductor else f"Tu hijo/a {nombre_estudiante} ha sido recogido."
    enviar_notificacion(
        titulo="Estudiante recogido",
        cuerpo=cuerpo,
        token=token
    )

def enviar_notificacion_asistencia_conductor(nombre_estudiante: str, asiste: bool, token: str):
    if asiste:
        titulo = "Estudiante reincorporado"
        cuerpo = f"El estudiante {nombre_estudiante} vuelve a la ruta."
    else:
        titulo = "Estudiante ausente"
        cuerpo = f"El estudiante {nombre_estudiante} no asistirá. Ha sido retirado de la ruta."

    enviar_notificacion(
        titulo=titulo,
        cuerpo=cuerpo,
        token=token
    )


def enviar_notificacion_inicio_ruta(nombre_estudiante: str, nombre_conductor: str, token: str):
    titulo = "Inicio de ruta"
    cuerpo = f"El conductor {nombre_conductor} ha iniciado la ruta de {nombre_estudiante}"
    enviar_notificacion(
        titulo=titulo,
        cuerpo=cuerpo,
        token=token
    )
