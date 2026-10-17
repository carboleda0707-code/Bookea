import os
import socket
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def enviar_correo_smtp(remitente: str = None, password: str = None, destinatario: str = "", asunto: str = "", html_content: str = ""):
    """
    Envía un correo electrónico usando SMTP forzando IPv4 para evitar [Errno 101] en la nube.
    """
    if not remitente or not password:
        print("⚠️ [SMTP Error] Faltan las credenciales del remitente o contraseña de app.")
        return False

    try:
        servidor_smtp = "smtp.gmail.com"
        puerto = 587

        # 🚀 Forzar resolución IPv4 para evitar el error "Network is unreachable" en Railway
        print(f"🌐 [SMTP] Resolviendo IPv4 para {servidor_smtp}...")
        try:
            info_addr = socket.getaddrinfo(servidor_smtp, puerto, socket.AF_INET, socket.SOCK_STREAM)
            ip_servidor = info_addr[0][4][0]
        except Exception as e:
            print(f"⚠️ [SMTP] No se pudo resolver por IPv4 directo, usando nombre por defecto: {e}")
            ip_servidor = servidor_smtp

        mensaje = MIMEMultipart("alternative")
        mensaje["Subject"] = asunto
        mensaje["From"] = remitente
        mensaje["To"] = destinatario

        parte_html = MIMEText(html_content, "html")
        mensaje.attach(parte_html)

        print(f"🔌 [SMTP] Conectando a {ip_servidor}:{puerto}...")
        with smtplib.SMTP(ip_servidor, puerto, timeout=10) as servidor:
            servidor.starttls()
            servidor.login(remitente, password)
            servidor.sendmail(remitente, destinatario, mensaje.as_string())
            
        print(f"✅ [SMTP] Correo enviado exitosamente a {destinatario} usando {remitente}")
        return True
    except Exception as e:
        print(f"❌ [SMTP Error detallado] No se pudo enviar el correo: {e}")
        return False