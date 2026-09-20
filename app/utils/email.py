import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def enviar_correo_smtp(remitente: str, password: str, destinatario: str, asunto: str, html_content: str):
    """
    Envía un correo electrónico usando las credenciales SMTP configuradas en el Local.
    """
    if not remitente or not password:
        print("⚠️ [SMTP] El local no tiene configurado un correo de envío o clave de aplicación.")
        return False

    try:
        servidor_smtp = "smtp.gmail.com"
        puerto = 587

        mensaje = MIMEMultipart("alternative")
        mensaje["Subject"] = asunto
        mensaje["From"] = remitente
        mensaje["To"] = destinatario

        parte_html = MIMEText(html_content, "html")
        mensaje.attach(parte_html)

        with smtplib.SMTP(servidor_smtp, puerto) as servidor:
            servidor.starttls()
            servidor.login(remitente, password)
            servidor.sendmail(remitente, destinatario, mensaje.as_string())
            
        print(f"✅ [SMTP] Correo enviado exitosamente a {destinatario} usando {remitente}")
        return True
    except Exception as e:
        print(f"❌ [SMTP Error] No se pudo enviar el correo: {e}")
        return False