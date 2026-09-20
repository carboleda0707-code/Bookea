from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from app.database import get_db
from app import models

router = APIRouter(prefix="/clientes-auth", tags=["Autenticación de Clientes / Usuarios Finales"])

# Configuración de encriptación de contraseñas con bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- ESQUEMAS PYDANTIC ---
class RegistroClienteSchema(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    telefono: str = None

class LoginClienteSchema(BaseModel):
    email: EmailStr
    password: str

class InscripcionEventoSchema(BaseModel):
    usuario_final_id: int
    evento_id: int
    propietario_id: int
    monto_pagado: float
    metodo_pago: str
    referencia_pago: str = None


# --- 1. REGISTRO DE USUARIOS FINALES ---
@router.post("/registro")
def registrar_cliente(datos: RegistroClienteSchema, db: Session = Depends(get_db)):
    
    # Verificar si el correo ya está registrado en 'usuarios_finales'
    existe = db.query(models.UsuarioFinal).filter(models.UsuarioFinal.email == datos.email).first()
    if existe:
        raise HTTPException(status_code=400, detail="Este correo ya se encuentra registrado.")
    
    # Encriptar la contraseña
    password_bytes = datos.password.encode("utf-8")[:72]
    password_segura = password_bytes.decode("utf-8", errors="ignore")
    password_hashed = pwd_context.hash(password_segura)
    
    # Crear el nuevo registro apuntando al modelo de la tabla 'usuarios_finales'
    nuevo_usuario = models.UsuarioFinal(
        nombre=datos.nombre,
        email=datos.email,
        password_hash=password_hashed,
        telefono=datos.telefono
    )
    
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    return {
        "mensaje": "¡Registro exitoso!",
        "id": nuevo_usuario.id,
        "nombre": nuevo_usuario.nombre,
        "email": nuevo_usuario.email
    }


# --- 2. LOGIN DE USUARIOS FINALES ---
@router.post("/login")
def login_cliente(datos: LoginClienteSchema, db: Session = Depends(get_db)):
    usuario = db.query(models.UsuarioFinal).filter(models.UsuarioFinal.email == datos.email).first()
    
    if not usuario or not pwd_context.verify(datos.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos.")
    
    return {
        "mensaje": "¡Bienvenido de nuevo!",
        "id": usuario.id,
        "nombre": usuario.nombre,
        "email": usuario.email
    }


# --- 3. INSCRIPCIÓN Y SELECCIÓN DE EVENTOS ---
@router.post("/inscribir-evento")
def inscribir_a_evento(datos: InscripcionEventoSchema, db: Session = Depends(get_db)):
    nueva_inscripcion = models.InscripcionPago(
        usuario_final_id=datos.usuario_final_id,
        evento_id=datos.evento_id,
        propietario_id=datos.propietario_id,
        monto_pagado=datos.monto_pagado,
        metodo_pago=datos.metodo_pago,
        estado_pago="completado",
        referencia_pago=datos.referencia_pago
    )
    
    db.add(nueva_inscripcion)
    db.commit()
    db.refresh(nueva_inscripcion)
    
    return {
        "mensaje": "Inscripción registrada correctamente al evento.",
        "inscripcion_id": nueva_inscripcion.id
    }