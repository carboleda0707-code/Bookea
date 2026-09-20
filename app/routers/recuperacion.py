# app/routers/recuperacion.py
import random
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv
from app.database import get_db
from app import models
from passlib.context import CryptContext

router = APIRouter(prefix="/auth-recuperacion", tags=["Recuperación de Contraseña"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def enviar_correo_smtp(destinatario: str, codigo: str):
    """Envía el código OTP por correo electrónico usando SMTP."""
    load_dotenv() # Asegura que lea el .env fresco en tiempo de ejecución
    
    remitente = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))

    # Chivato para verificar en la terminal la lectura correcta de credenciales
    print(f"CHIVATO SMTP -> Usuario: {remitente} | Password (longitud): {len(password) if password else 0}")

    mensaje = MIMEMultipart("alternative")
    mensaje["Subject"] = "🔐 Código de Recuperación de Contraseña - Bookea"
    mensaje["From"] = remitente
    mensaje["To"] = destinatario

    # Cuerpo del correo en HTML estilizado
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
        <div style="max-width: 600px; background: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
          <h2 style="color: #ff007f; text-align: center;">Bookea - Recuperación de Acceso</h2>
          <p>Hola,</p>
          <p>Has solicitado restablecer tu contraseña. Utiliza el siguiente código de verificación de 6 dígitos (válido por 15 minutos):</p>
          <div style="background: #f8f9fa; padding: 15px; text-align: center; font-size: 28px; font-weight: bold; letter-spacing: 5px; color: #333; border-radius: 5px; margin: 20px 0;">
            {codigo}
          </div>
          <p>Si no solicitaste este cambio, puedes ignorar este mensaje de forma segura.</p>
          <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
          <p style="font-size: 12px; color: #888; text-align: center;">Este es un mensaje automático, por favor no respondas a este correo.</p>
        </div>
      </body>
    </html>
    """
    
    mensaje.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as servidor:
            servidor.starttls()
            servidor.login(remitente, password)
            servidor.sendmail(remitente, destinatario, mensaje.as_string())
        print(f"--- CORREO SMTP ENVIADO EXITOSAMENTE A: {destinatario} ---")
    except Exception as e:
        print(f"--- ERROR AL ENVIAR CORREO SMTP: {e} ---")
        raise HTTPException(status_code=500, detail=f"No se pudo enviar el correo electrónico: {str(e)}")

@router.on_event("startup")
def asegurar_columnas_recuperacion():
    from app.database import engine
    with engine.connect() as conn:
        for tabla in ["usuarios_finales", "usuarios"]:
            try:
                conn.execute(text(f"ALTER TABLE {tabla} ADD COLUMN IF NOT EXISTS reset_token VARCHAR(10);"))
                conn.commit()
            except Exception as e:
                print(f"Nota en tabla {tabla} (reset_token): {e}")
                
            try:
                conn.execute(text(f"ALTER TABLE {tabla} ADD COLUMN IF NOT EXISTS reset_token_expires TIMESTAMP;"))
                conn.commit()
            except Exception as e:
                print(f"Nota en tabla {tabla} (reset_token_expires): {e}")

class SolicitarRecuperacion(BaseModel):
    email: EmailStr

class VerificarCambioPassword(BaseModel):
    email: EmailStr
    codigo: str
    nueva_password: str

@router.post("/solicitar-codigo")
def solicitar_codigo(payload: SolicitarRecuperacion, db: Session = Depends(get_db)):
    usuario = None
    es_cliente = True
    
    try:
        if hasattr(models.UsuarioFinal, 'email'):
            usuario = db.query(models.UsuarioFinal).filter(models.UsuarioFinal.email == payload.email).first()
        elif hasattr(models.UsuarioFinal, 'correo'):
            usuario = db.query(models.UsuarioFinal).filter(models.UsuarioFinal.correo == payload.email).first()
    except Exception:
        pass
        
    if not usuario:
        es_cliente = False
        try:
            if hasattr(models.Usuario, 'correo'):
                usuario = db.query(models.Usuario).filter(models.Usuario.correo == payload.email).first()
            elif hasattr(models.Usuario, 'email'):
                usuario = db.query(models.Usuario).filter(models.Usuario.email == payload.email).first()
        except Exception:
            pass
        
    if not usuario:
        raise HTTPException(status_code=404, detail="Correo no registrado en el sistema.")
    
    codigo_otp = f"{random.randint(100000, 999999)}"
    usuario.reset_token = codigo_otp
    usuario.reset_token_expires = datetime.utcnow() + timedelta(minutes=15)
    db.commit()
    
    # Envío real a través del servidor SMTP configurado
    enviar_correo_smtp(payload.email, codigo_otp)

    return {"mensaje": "Código de recuperación enviado con éxito al correo."}

@router.post("/cambiar-password")
def cambiar_password(payload: VerificarCambioPassword, db: Session = Depends(get_db)):
    usuario = None
    es_cliente = True
    
    try:
        if hasattr(models.UsuarioFinal, 'email'):
            usuario = db.query(models.UsuarioFinal).filter(models.UsuarioFinal.email == payload.email).first()
        elif hasattr(models.UsuarioFinal, 'correo'):
            usuario = db.query(models.UsuarioFinal).filter(models.UsuarioFinal.correo == payload.email).first()
    except Exception:
        pass
        
    if not usuario:
        es_cliente = False
        try:
            if hasattr(models.Usuario, 'correo'):
                usuario = db.query(models.Usuario).filter(models.Usuario.correo == payload.email).first()
            elif hasattr(models.Usuario, 'email'):
                usuario = db.query(models.Usuario).filter(models.Usuario.email == payload.email).first()
        except Exception:
            pass
        
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        
    if not usuario.reset_token or usuario.reset_token != payload.codigo:
        raise HTTPException(status_code=400, detail="Código de verificación incorrecto.")
        
    if usuario.reset_token_expires and datetime.utcnow() > usuario.reset_token_expires:
        raise HTTPException(status_code=400, detail="El código ha expirado. Solicita uno nuevo.")
        
    if es_cliente:
        if hasattr(usuario, 'password_hash'):
            usuario.password_hash = pwd_context.hash(payload.nueva_password)
        elif hasattr(usuario, 'contrasena'):
            usuario.contrasena = pwd_context.hash(payload.nueva_password)
    else:
        if hasattr(usuario, 'contrasena'):
            usuario.contrasena = pwd_context.hash(payload.nueva_password)
        elif hasattr(usuario, 'password_hash'):
            usuario.password_hash = pwd_context.hash(payload.nueva_password)

    usuario.reset_token = None
    usuario.reset_token_expires = None
    db.commit()
    
    return {"mensaje": "Contraseña actualizada exitosamente."}