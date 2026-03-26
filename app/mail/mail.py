import logging
import html
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def send_email(lead, result):
    sender = settings.smtp_user
    password = settings.smtp_password
    receiver = getattr(lead, "email", None)

    # Validar email
    if not receiver:
        logger.error("Email del lead vacío")
        return

    # Crear mensaje
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Estimado Cliente"
    msg["From"] = sender
    msg["To"] = receiver

    # Obtener respuesta de la IA y sanitizar
    response = result.get(
        "message",
        "Queríamos saber cómo estás y si podemos ayudarte en algo."
    )
    safe_response = html.escape(response)

    # Personalización
    name = getattr(lead, "name", "Cliente")

    # Contenido en texto plano (fallback)
    text_content = f"""
Hola {name},

{response}

Nos encantaría retomar la conversación contigo:
https://t.me/LeadReactivatorBot

Si no deseas recibir más mensajes, puedes ignorar este correo.
"""

    # Contenido HTML
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 10px;">
            
            <h2 style="color: #2c3e50;">Hola {name}</h2>
            
            <p style="font-size: 16px; color: #555;">
                {safe_response}
            </p>

            <p style="font-size: 16px; color: #555;">
                Nos encantaría retomar la conversación contigo.
            </p>

            <a href="https://t.me/LeadReactivatorBot"
               style="display: inline-block; padding: 12px 20px; margin-top: 15px;
                      background-color: #0088cc; color: white; text-decoration: none;
                      border-radius: 5px;">
                Abrir en Telegram
            </a>

            <hr style="margin: 20px 0;">

            <p style="font-size: 12px; color: #999;">
                Si no deseas recibir más mensajes, puedes ignorar este correo.
            </p>

        </div>
    </body>
    </html>
    """

    # Adjuntar contenido
    msg.attach(MIMEText(text_content, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    # Enviar correo con manejo de errores
    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)

        logger.info(f"Correo enviado a {receiver}")

    except Exception as e:
        logger.error(f"Error enviando correo a {receiver}: {e}")