import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from fastapi import HTTPException

def enviar_correo_restablecer_contrasena(destinatario: str, token: str):
    url = f"https://movil-app-page.vercel.app/new-pass{token}"  # Puedes cambiar esto luego
    asunto = "Restablece tu contraseña Transporte Escolar"
    contenido = f"Haz clic en este enlace para restablecer tu contraseña:\n\n{url}"

    message = Mail(
        from_email="iv.bozo.catalan@gmail.com",  # el que verificaste en SendGrid
        to_emails=destinatario,
        subject=asunto,
        plain_text_content=contenido,
    )

    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
        if response.status_code >= 400:
            raise HTTPException(status_code=500, detail="Error al enviar el correo")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de envío: {str(e)}")
