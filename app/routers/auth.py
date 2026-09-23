from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional
import re
import traceback

from ..database import get_db
from .. import models
from ..seguridad import obtener_password_hash, verificar_password, crear_token_acceso

router = APIRouter(prefix="/auth", tags=["Autenticación"])

class LoginRequest(BaseModel):
    correo: str
    contrasena: str
    latitud: Optional[float] = None
    longitud: Optional[float] = None

class RegistroPropietarioSchema(BaseModel):
    nombre_comercial: str
    tipo_negocio: Optional[str] = "Salsoteca"
    nombre: str
    correo: str
    contrasena: str
    telefono: Optional[str] = None
    ruc: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None

def generar_slug(texto: str) -> str:
    """Genera un slug limpio a partir del nombre comercial."""
    texto = texto.lower().strip()
    reemplazos = (
        ("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ñ", "n")
    )
    for a, b in reemplazos:
        texto = texto.replace(a, b)
    texto = re.sub(r'[^a-z0-9]+', '-', texto)
    return texto.strip('-')

@router.post("/login")
def login_usuario(credentials: LoginRequest, db: Session = Depends(get_db)):
    try:
        # --- CHIVATO DE DIAGNÓSTICO TOTAL ---
        todos_los_usuarios = db.query(models.Usuario).all()
        lista_emails = [u.correo for u in todos_los_usuarios]
        print(f"🔍 [CHIVATO NUBE] Conectado a BD. Correos encontrados en la tabla: {lista_emails}")
        
        correo_limpio = credentials.correo.strip().lower()
        usuario = db.query(models.Usuario).filter(func.lower(models.Usuario.correo) == correo_limpio).first()
        
        if not usuario:
            # Si no lo encuentra, devolvemos un 401 que incluye la lista para verla de inmediato
            raise HTTPException(
                status_code=401, 
                detail=f"Usuario no encontrado. Busqué '{correo_limpio}'. Encontrados en BD: {lista_emails}"
            )
            
        if not usuario.activo:
            raise HTTPException(status_code=401, detail=f"El usuario existe pero 'activo' es: {usuario.activo}")
        
        # Verificación segura con bcrypt
        if not verificar_password(credentials.contrasena, usuario.contrasena):
            raise HTTPException(status_code=401, detail="Contraseña incorrecta")
        
        # Persistir coordenadas GPS si el cliente las envía en el login
        if credentials.latitud is not None and credentials.longitud is not None:
            usuario.latitud = credentials.latitud
            usuario.longitud = credentials.longitud
            db.commit()
        
        local_id_default = None
        try:
            if usuario.empresa_id:
                local_asociado = db.query(models.Local).filter(models.Local.empresa_id == str(usuario.empresa_id)).first()
                if local_asociado:
                    local_id_default = local_asociado.id
            elif usuario.propietario_id:
                local_asociado = db.query(models.Local).filter(models.Local.propietario_id == usuario.propietario_id).first()
                if local_asociado:
                    local_id_default = local_asociado.id
        except Exception:
            local_id_default = None

        # Generar token JWT listo para la web y la app móvil
        access_token = crear_token_acceso(data={"sub": usuario.correo})

        return {
            "mensaje": "Login exitoso",
            "access_token": access_token,
            "token_type": "bearer",
            "usuario_id": usuario.propietario_id,
            "nombre": usuario.nombre,
            "rol": usuario.rol,
            "empresa_id": usuario.empresa_id,
            "local_id": local_id_default,
            "nombre_comercial": usuario.nombre_comercial,
            "tipo_negocio": usuario.tipo_negocio
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"❌ Error crítico en login: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.post("/registro")
def registrar_propietario(
    datos: RegistroPropietarioSchema, db: Session = Depends(get_db)
):
  try:
    correo_limpio = datos.correo.strip().lower()
    existente = (
        db.query(models.Usuario)
        .filter(func.lower(models.Usuario.correo) == correo_limpio)
        .first()
    )

    slug_generado = generar_slug(datos.nombre_comercial)
    password_hash = obtener_password_hash(datos.contrasena)

    # 1. VALIDAR Y CREAR LA EMPRESA PRIMERO (Evita el error de llave foránea)
    empresa_id_val = None
    if datos.ruc and datos.ruc.isdigit():
      empresa_id_val = int(datos.ruc)
      empresa_existente = (
          db.query(models.Empresa)
          .filter(models.Empresa.id == empresa_id_val)
          .first()
      )
      if not empresa_existente:
        nueva_empresa = models.Empresa(
            id=empresa_id_val,
            nombre_comercial=datos.nombre_comercial,
            ruc_nit=datos.ruc,
            activo=True,
        )
        db.add(nueva_empresa)
        db.flush()  # Guarda de forma provisional en la transacción

    if existente:
      existente.rol = "propietario"
      existente.nombre_comercial = datos.nombre_comercial
      existente.tipo_negocio = datos.tipo_negocio
      existente.contrasena = password_hash
      existente.empresa_id = empresa_id_val
      if datos.latitud is not None and datos.longitud is not None:
        existente.latitud = datos.latitud
        existente.longitud = datos.longitud
      db.commit()
      db.refresh(existente)

      nuevo_local = models.Local(
          nombre=datos.nombre_comercial,
          slug=slug_generado,
          tipo_establecimiento=datos.tipo_negocio,
          propietario_id=existente.propietario_id,
          telefono=datos.telefono,
          empresa_id=empresa_id_val,
      )
      db.add(nuevo_local)
      db.commit()
      db.refresh(nuevo_local)

      return {
          "mensaje": (
              "¡Negocio registrado con éxito para tu cuenta existente!"
          ),
          "usuario_id": existente.propietario_id,
          "local_id": nuevo_local.id,
      }

    # --- Si es un usuario nuevo ---
    max_id = db.query(func.max(models.Usuario.propietario_id)).scalar()
    siguiente_id = (max_id or 0) + 1

    nuevo_propietario = models.Usuario(
        propietario_id=siguiente_id,
        nombre=datos.nombre,
        correo=correo_limpio,
        contrasena=password_hash,
        nombre_comercial=datos.nombre_comercial,
        tipo_negocio=datos.tipo_negocio,
        empresa_id=empresa_id_val,
        rol="propietario",
        activo=True,
        latitud=datos.latitud,
        longitud=datos.longitud,
    )

    db.add(nuevo_propietario)
    db.flush()

    nuevo_local = models.Local(
        nombre=datos.nombre_comercial,
        slug=slug_generado,
        tipo_establecimiento=datos.tipo_negocio,
        propietario_id=nuevo_propietario.propietario_id,
        telefono=datos.telefono,
        empresa_id=empresa_id_val,
    )
    db.add(nuevo_local)

    db.commit()
    db.refresh(nuevo_local)

    return {
        "mensaje": "¡Negocio y propietario registrados con éxito!",
        "usuario_id": nuevo_propietario.propietario_id,
        "local_id": nuevo_local.id,
    }

  except HTTPException as he:
    db.rollback()
    raise he
  except Exception as e:
    db.rollback()
    print(f"❌ Error crítico en registro: {e}")
    traceback.print_exc()
    raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.get("/vip/por-slug/{slug}")
def obtener_propietario_por_slug(slug: str, db: Session = Depends(get_db)):
    slug_limpio = slug.strip().lower()
    propietario = db.query(models.Usuario).filter(
        func.lower(models.Usuario.slug) == slug_limpio,
        models.Usuario.rol == "propietario"
    ).first()

    if not propietario:
        raise HTTPException(status_code=404, detail="El enlace del local VIP no existe.")

    if propietario.tipo_plan != "VIP":
        raise HTTPException(status_code=403, detail="Este establecimiento no cuenta con plan VIP activo.")

    return {
        "id": propietario.id,
        "nombre": propietario.nombre,
        "tipo_plan": propietario.tipo_plan,
        "slug": propietario.slug,
        "tipo_negocio": propietario.tipo_negocio
    }
    
@router.get("/configuracion/notificaciones")
def obtener_configuracion(db: Session = Depends(get_db)):
    config = db.query(models.ConfiguracionNotificaciones).first()
    if not config:
        return {"correo_remitente": "", "celular_remitente": "", "password_correo": ""}
    return config

@router.post("/configuracion/notificaciones")
def guardar_configuracion(
    correo_remitente: str = Form(...),
    password_correo: str = Form(""),
    celular_remitente: str = Form(...),
    db: Session = Depends(get_db)
):
    config = db.query(models.ConfiguracionNotificaciones).first()
    if not config:
        config = models.ConfiguracionNotificaciones(
            correo_remitente=correo_remitente,
            password_correo=password_correo,
            celular_remitente=celular_remitente
        )
        db.add(config)
    else:
        config.correo_remitente = correo_remitente
        config.password_correo = password_correo
        config.celular_remitente = celular_remitente
    
    db.commit()
    return {"mensaje": "Configuración de notificaciones guardada con éxito"}

@router.get("/stats/social-proof")
def obtener_estadisticas_globales(db: Session = Depends(get_db)):
    try:
        total_usuarios = db.query(func.count(models.UsuarioFinal.id)).scalar() or 0
        total_locales = db.query(func.count(models.Local.id)).scalar() or 0
        
        return {
            "total_usuarios": total_usuarios,
            "total_locales": total_locales
        }
    except Exception as e:
        return {"total_usuarios": 0, "total_locales": 0}

@router.post("/locales/{local_id}/like")
def dar_like_local(local_id: int, db: Session = Depends(get_db)):
    try:
        local = db.query(models.Local).filter(models.Local.id == local_id).first()
        if not local:
            raise HTTPException(status_code=404, detail="Local no encontrado")
        
        local.likes = (local.likes or 0) + 1
        db.commit()
        db.refresh(local)
        
        return {"success": True, "likes": local.likes}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))