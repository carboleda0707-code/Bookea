# app/routers/recuperacion.py
import random
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel, EmailStr
from app.database import get_db
from app import models
from passlib.context import CryptContext

# Importamos la función centralizada y segura de correo que ya tienes probada en el proyecto
from app.utils.email import enviar_correo_smtp as enviar_correo_base

router = APIRouter(prefix="/auth-recuperacion", tags=["Recuperación de Contraseña"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def enviar_correo_recuperacion(db: Session, destinatario: str, codigo: str):
    """Envía el código OTP leyendo las credenciales reales de la base de datos."""
    
    remitente = None
    password = None

    # 1. Intentamos leer de la tabla de configuración de notificaciones (la que usa el admin)
    config_notif = db.execute(text("SELECT correo_remitente, password_correo FROM configuracion_notificaciones LIMIT 1")).fetchone()
    if config_notif and config_notif.correo_remitente and config_notif.password_correo:
        remitente = config_notif.correo_remitente
        password = config_notif.password_correo
    
    # 2. Si no hay, intentamos de la tabla locales
    if not remitente or not password:
        local_config = db.execute(text("SELECT correo_envio, password_app FROM locales WHERE correo_envio IS NOT NULL AND correo_envio != '' LIMIT 1")).fetchone()
        if local_config and local_config.correo_envio and local_config.password_app:
            remitente = local_config.correo_envio
            password = local_config.password_app

    # 3. Si aún no hay, ponemos tu correo por defecto asegurándonos de que no falle (coloca tu contraseña de aplicación aquí si deseas respaldo fijo)
    if not remitente:
        remitente = "carboleda0707@gmail.com"
    
    print(f"CHIVATO SMTP (Recuperación) -> Usuario: {remitente} | Password (longitud): {len(password) if password else 0}")

    if not password:
        print("❌ [Error Crítico] La contraseña de aplicación SMTP está vacía en la base de datos.")
        return False

    asunto = "🔐 Código de Recuperación de Contraseña - Bookea"
    
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

    return enviar_correo_base(
        remitente=remitente,
        password=password,
        destinatario=destinatario,
        asunto=asunto,
        html_content=html
    )

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
def solicitar_codigo(payload: SolicitarRecuperacion, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
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
        
    # Enviar correo en segundo plano usando la función segura con IPv4
    background_tasks.add_task(enviar_correo_recuperacion, db, payload.email, codigo_otp)

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