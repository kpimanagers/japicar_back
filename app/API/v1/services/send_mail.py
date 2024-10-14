# send_mail.py
import sys
from typing import List
from jinja2 import Template
from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr

from ....config import config as config_env


conf = ConnectionConfig(
    MAIL_USERNAME =config_env.MAIL_FROM,
    MAIL_PASSWORD =config_env.MAIL_PASSWORD,
    MAIL_FROM =config_env.MAIL_FROM,
    MAIL_PORT = 465,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_STARTTLS = False,
    MAIL_SSL_TLS = True,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

# Función para leer y renderizar el HTML desde un archivo
def render_html_from_file(file_path: str, context: dict) -> str:
    # Leer el contenido del archivo HTML
    template_content = Path(file_path).read_text()
    # Crear una instancia de Template con el contenido del archivo
    template = Template(template_content)
    # Renderizar la plantilla con el contexto proporcionado
    return template.render(context)

# Función para enviar un correo electrónico
async def send_email(
    recipients: List[EmailStr],
    subject: str,
    template_file_path: str,
    context: dict
):
    try:
        # Renderiza el HTML con los valores proporcionados
        html_content = render_html_from_file(template_file_path, context)
        
        # Crear el mensaje
        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            body=html_content,
            subtype="html"
        )
        
        # Crear una instancia de FastMail con la configuración
        fm = FastMail(conf)
        
        # Enviar el mensaje
        await fm.send_message(message)
    except Exception as err:
        print("Error in line send_email________________________________________________________________________:", sys.exc_info()[-1].tb_lineno)
        print("Error message_______________________________________ : {0}".format(err))
