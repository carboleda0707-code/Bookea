import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

servidor = os.getenv("SMTP_SERVER")
puerto = int(os.getenv("SMTP_PORT", 587))
usuario = os.getenv("SMTP_USER")
password = os.getenv("SMTP_PASSWORD")

print(f"Usuario cargado: {usuario}")
print(f"Longitud de contraseña cargada: {len(password) if password else 0}")

try:
    msg = EmailMessage()
    msg.set_content("Prueba de correo desde Bookea")
    msg["Subject"] = "Prueba SMTP"
    msg["From"] = usuario
    msg["To"] = usuario

    print("Conectando al servidor SMTP...")
    server = smtplib.SMTP(servidor, puerto)
    server.starttls()
    print("Iniciando sesión...")
    server.login(usuario, password)
    server.send_message(msg)
    server.quit()
    print("¡Correo enviado con éxito!")
except Exception as e:
    print(f"Error detallado: {e}")