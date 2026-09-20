from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Usuario, UsuarioFinal, Local
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/admin", tags=["Administración"])

class LocalCompletoUpdateModel(BaseModel):
    nombre_propietario: Optional[str] = None
    nombre_local: Optional[str] = None
    correo: Optional[str] = None
    email_contacto: Optional[str] = None
    telefono: Optional[str] = None
    telefono_contacto: Optional[str] = None
    direccion: Optional[str] = None
    tipo_plan: Optional[str] = "Normal"
    pagado: Optional[bool] = False
    slug: Optional[str] = None
    correo_envio: Optional[str] = None
    password_app: Optional[str] = None
    activo: Optional[bool] = True

@router.get("/propietarios")
def listar_locales_completos(db: Session = Depends(get_db)):
    locales = db.query(Local).all()
    resultado = []
    
    # Detección dinámica de la clave primaria de la tabla Usuario
    pk_usuario = list(Usuario.__table__.primary_key.columns)[0].name
    
    for local in locales:
        propietario = None
        prop_id = getattr(local, 'propietario_id', None)
        emp_id = getattr(local, 'empresa_id', None)
        
        if prop_id:
            propietario = db.query(Usuario).filter(getattr(Usuario, pk_usuario) == prop_id).first()
        elif emp_id and hasattr(Usuario, 'empresa_id'):
            propietario = db.query(Usuario).filter(Usuario.empresa_id == emp_id).first()
        
        prop_id_val = getattr(propietario, pk_usuario, None) if propietario else None
        
        resultado.append({
            "id": local.id,
            "propietario_id": prop_id_val,
            "nombre_propietario": getattr(propietario, 'nombre', 'Sin Propietario') if propietario else "Sin Propietario",
            "nombre_local": getattr(local, 'nombre', '') or getattr(local, 'nombre_local', 'Local Principal'),
            "correo": getattr(local, 'email_contacto', None) or (getattr(propietario, 'correo', '') if propietario else ""),
            "email_contacto": getattr(local, 'email_contacto', '') or "",
            "telefono": getattr(local, 'telefono', '') or "",
            "telefono_contacto": getattr(local, 'telefono_contacto', '') or "",
            "direccion": getattr(local, 'direccion', '') or "",
            "tipo_plan": getattr(local, 'tipo_plan', getattr(propietario, 'tipo_plan', 'Normal') if propietario else 'Normal'),
            "pagado": getattr(local, 'pagado', getattr(propietario, 'pagado', False) if propietario else False),
            "slug": getattr(local, 'slug', '') or "",
            # Se leen prioritariamente del propietario (tabla usuarios), con fallback al local
            "correo_envio": getattr(propietario, 'correo_envio', '') if propietario else (getattr(local, 'correo_envio', '') or ""),
            "password_app": getattr(propietario, 'password_app', '') if propietario else (getattr(local, 'password_app', '') or ""),
            "activo": getattr(local, 'activo', True)
        })
            
    return resultado

@router.get("/clientes")
def listar_clientes(db: Session = Depends(get_db)):
    return db.query(UsuarioFinal).all()

@router.put("/local/{local_id}")
def actualizar_local_completo(local_id: int, data: LocalCompletoUpdateModel, db: Session = Depends(get_db)):
    
    local = db.query(Local).filter(Local.id == local_id).first()
    if not local:
        raise HTTPException(status_code=404, detail="Local no encontrado")
    
    # 🔑 Asignación directa y obligatoria al local (fuera del else)
    local.correo_envio = data.correo_envio
    local.password_app = data.password_app
    
       
    print(f"🔍 [CHIVATO BACKEND] Actualizando Local ID: {local_id}")
    print(f"🔍 [CHIVATO BACKEND] correo_envio recibido: {repr(data.correo_envio)}")
    print(f"🔍 [CHIVATO BACKEND] password_app recibido: {repr(data.password_app)}")
    
    if data.telefono is not None:
        local.telefono = data.telefono
    if data.telefono_contacto is not None:
        local.telefono_contacto = data.telefono_contacto
    elif data.telefono is not None:
        local.telefono_contacto = data.telefono
        
    if data.direccion is not None:
        local.direccion = data.direccion
    if data.slug is not None:
        local.slug = data.slug
    
    if data.tipo_plan is not None:
        local.tipo_plan = data.tipo_plan
        if data.tipo_plan == "VIP":
            local.pagado = True
        elif data.pagado is not None:
            local.pagado = data.pagado

    if data.email_contacto is not None:
        local.email_contacto = data.email_contacto
    elif data.correo is not None:
        local.email_contacto = data.correo
        
    if data.nombre_local is not None:
        local.nombre = data.nombre_local
            
    local.activo = data.activo
    
    propietario = None
    pk_usuario = list(Usuario.__table__.primary_key.columns)[0].name
    
    if local.propietario_id:
        propietario = db.query(Usuario).filter(getattr(Usuario, pk_usuario) == local.propietario_id).first()
    elif hasattr(local, 'empresa_id') and local.empresa_id and hasattr(Usuario, 'empresa_id'):
        propietario = db.query(Usuario).filter(Usuario.empresa_id == local.empresa_id).first()
        
    if propietario:
        if data.nombre_propietario is not None and hasattr(propietario, 'nombre'):
            propietario.nombre = data.nombre_propietario
        if data.correo is not None and hasattr(propietario, 'correo'):
            propietario.correo = data.correo
        if data.tipo_plan is not None and hasattr(propietario, 'tipo_plan'):
            propietario.tipo_plan = data.tipo_plan
            if data.tipo_plan == "VIP" and hasattr(propietario, 'pagado'):
                propietario.pagado = True
            elif data.pagado is not None and hasattr(propietario, 'pagado'):
                propietario.pagado = data.pagado
            
        # 🔑 Asignación directa de credenciales SMTP a la tabla del usuario propietario
        if hasattr(propietario, 'correo_envio'):
            propietario.correo_envio = data.correo_envio
        if hasattr(propietario, 'password_app'):
            propietario.password_app = data.password_app
            
        prop_id_val = getattr(propietario, pk_usuario, None)
        if prop_id_val == 1:
            if hasattr(propietario, 'activo'):
                propietario.activo = True
            local.activo = True
        else:
            if hasattr(propietario, 'activo'):
                propietario.activo = data.activo
    else:
        # Fallback por si el local no tuviera un usuario asociado vinculado
        local.correo_envio = data.correo_envio
        local.password_app = data.password_app

          
    if data.tipo_plan is not None:
        local.tipo_plan = data.tipo_plan
    
    db.commit()
    db.refresh(local)
    if propietario:
        db.refresh(propietario)
        
    correo_val = getattr(propietario, 'correo_envio', 'N/A') if propietario else "N/A"
    print(f"✅ [CHIVATO] Guardado exitoso -> Correo Envío: {correo_val}")
    
    return {"mensaje": "Registro actualizado correctamente"}

@router.put("/cliente/{cliente_id}/estado")
def actualizar_estado_cliente(cliente_id: int, activo: bool, db: Session = Depends(get_db)):
    cliente = db.query(UsuarioFinal).filter(UsuarioFinal.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    cliente.es_activo = activo
    db.commit()
    db.refresh(cliente)     
    return {"mensaje": "Local actualizado correctamente"}

@router.delete("/local/{local_id}")
def eliminar_local(local_id: int, db: Session = Depends(get_db)):
    local = db.query(Local).filter(Local.id == local_id).first()
    if not local:
        raise HTTPException(status_code=404, detail="Local no encontrado")
    
    if local_id == 1:
        raise HTTPException(status_code=400, detail="No se puede eliminar el local del SuperAdmin.")
        
    db.delete(local)
    db.commit()
    return {"mensaje": "Local eliminado correctamente"}