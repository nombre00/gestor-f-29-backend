

# Bibliotecas.
import os
import resend
from typing import Optional
# Módulos.
from f29_backend.core.settings import settings


# Configurar API key al importar el módulo 
resend.api_key = settings.RESEND_API_KEY.get_secret_value()

# Remitente configurable por variable de entorno
FROM_EMAIL = settings.RESEND_FROM_EMAIL.get_secret_value()
FRONTEND_URL = settings.FRONTEND_URL.get_secret_value()


def _html_invitacion(nombre: str, invitado_por: str, link_registro: str) -> str:
    """
    Template HTML del email de invitación.
    Limpio, funcional, compatible con la mayoría de clientes de email.
    """
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Invitación a F29 Manager</title>
    </head>
    <body style="margin:0; padding:0; background-color:#f4f6f9; font-family: Arial, sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f6f9; padding: 40px 0;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:8px; overflow:hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                        
                        <!-- Header -->
                        <tr>
                            <td style="background-color:#0d6efd; padding: 32px 40px; text-align:center;">
                                <h1 style="margin:0; color:#ffffff; font-size:24px; font-weight:700;">
                                    📄 F29 Manager
                                </h1>
                                <p style="margin: 8px 0 0 0; color:#cfe2ff; font-size:14px;">
                                    Sistema de gestión de formularios SII
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Body -->
                        <tr>
                            <td style="padding: 40px 40px 32px 40px;">
                                <h2 style="margin: 0 0 16px 0; color:#212529; font-size:20px;">
                                    Hola {nombre},
                                </h2>
                                <p style="margin: 0 0 16px 0; color:#495057; font-size:15px; line-height:1.6;">
                                    <strong>{invitado_por}</strong> te ha invitado a unirte a <strong>F29 Manager</strong>, 
                                    la plataforma de gestión de formularios F29 del SII.
                                </p>
                                <p style="margin: 0 0 32px 0; color:#495057; font-size:15px; line-height:1.6;">
                                    Para activar tu cuenta y elegir tu contraseña, haz clic en el botón:
                                </p>
                                
                                <!-- CTA Button -->
                                <table width="100%" cellpadding="0" cellspacing="0">
                                    <tr>
                                        <td align="center">
                                            <a href="{link_registro}" 
                                               style="display:inline-block; background-color:#0d6efd; color:#ffffff; 
                                                      text-decoration:none; padding:14px 32px; border-radius:6px; 
                                                      font-size:16px; font-weight:600;">
                                                Activar mi cuenta
                                            </a>
                                        </td>
                                    </tr>
                                </table>
                                
                                <!-- Link alternativo -->
                                <p style="margin: 24px 0 0 0; color:#6c757d; font-size:13px; text-align:center;">
                                    Si el botón no funciona, copia este enlace en tu navegador:<br>
                                    <a href="{link_registro}" style="color:#0d6efd; word-break:break-all;">
                                        {link_registro}
                                    </a>
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Aviso expiración -->
                        <tr>
                            <td style="padding: 0 40px 32px 40px;">
                                <div style="background-color:#fff3cd; border:1px solid #ffc107; border-radius:6px; padding:16px;">
                                    <p style="margin:0; color:#664d03; font-size:13px;">
                                        ⏰ <strong>Este enlace expirará en 7 días.</strong> 
                                        Si no completas tu registro antes, deberás solicitar una nueva invitación.
                                    </p>
                                </div>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="background-color:#f8f9fa; padding: 24px 40px; border-top: 1px solid #e9ecef;">
                                <p style="margin:0; color:#adb5bd; font-size:12px; text-align:center;">
                                    Si no esperabas esta invitación, puedes ignorar este correo con seguridad.<br>
                                    © F29 Manager — Sistema de gestión SII
                                </p>
                            </td>
                        </tr>
                        
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


async def enviar_email_invitacion(
    email: str,
    nombre: str,
    token: str,
    invitado_por: str
) -> None:
    """
    Envía un email de invitación usando Resend.
    Lanza excepción si falla (el router la captura y elimina la invitación).
    """
    if not resend.api_key:
        raise ValueError("RESEND_API_KEY no está configurada en las variables de entorno")

    link_registro = f"{FRONTEND_URL}/registro?token={token}"

    params: resend.Emails.SendParams = {
        "from": f"F29 Manager <{FROM_EMAIL}>",
        "to": [email],
        "subject": f"{invitado_por} te invita a F29 Manager",
        "html": _html_invitacion(nombre, invitado_por, link_registro),
    }

    try:
        response = resend.Emails.send(params)
        print(f"✅ Email enviado a {email} | ID: {response.get('id', 'N/A')}")
    except Exception as e:
        print(f"❌ Error al enviar email a {email}: {str(e)}")
        raise  # Re-lanzar para que el router maneje la transacción