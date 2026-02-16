import os
from typing import Optional


async def enviar_email_invitacion(
    email: str,
    nombre: str,
    token: str,
    invitado_por: str
) -> None:
    """
    Envía un email de invitación al usuario.
    Por ahora es un placeholder que solo imprime en consola.
    En producción deberías usar SendGrid, AWS SES, o similar.
    """
    
    # URL del frontend (configurable por variable de entorno)
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    link_registro = f"{frontend_url}/register?token={token}"
    
    # Contenido del email
    asunto = "Invitación a F29 Manager"
    cuerpo = f"""
    Hola {nombre},
    
    Has sido invitado por {invitado_por} a unirte a F29 Manager.
    
    Para completar tu registro, haz clic en el siguiente enlace:
    
    {link_registro}
    
    Este enlace expirará en 7 días.
    
    Si no esperabas esta invitación, puedes ignorar este correo.
    
    Saludos,
    Equipo F29 Manager
    """
    
    # Por ahora solo imprimimos en consola
    print("=" * 60)
    print(f"📧 EMAIL DE INVITACIÓN")
    print("=" * 60)
    print(f"Para: {email}")
    print(f"Asunto: {asunto}")
    print(f"\n{cuerpo}")
    print("=" * 60)
    print(f"🔗 Link de registro: {link_registro}")
    print("=" * 60)
    
    # TODO: Implementar envío real de email
    # Ejemplo con SendGrid:
    # from sendgrid import SendGridAPIClient
    # from sendgrid.helpers.mail import Mail
    # 
    # message = Mail(
    #     from_email='noreply@tuempresa.com',
    #     to_emails=email,
    #     subject=asunto,
    #     html_content=cuerpo
    # )
    # sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
    # response = sg.send(message)