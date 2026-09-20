from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from pydantic import BaseModel, Field
from app.database import get_db
from app import models
import shutil
import os

router = APIRouter(prefix="/precio-evento-mesa", tags=["Precio Evento Mesa"])

# --- ESQUEMAS PYDANTIC PARA VALIDACIÓN PROFESIONAL ---
class AsignacionMesaBase(BaseModel):
    evento_id: int
    mesa_id: int
    precio: float = Field(..., ge=0.0, description="Precio de reserva de la mesa")
    consumo_minimo: float = Field(..., ge=0.0, description="Consumo mínimo obligatorio")

class ActualizacionAsignacionBase(BaseModel):
    precio: float = Field(..., ge=0.0)
    consumo_minimo: float = Field(..., ge=0.0)


@router.post("/")
def asignar_mesa_evento(data: AsignacionMesaBase, db: Session = Depends(get_db)):
    """
    Vincula una mesa a un evento o actualiza sus valores si ya existe (Upsert).
    """
    try:
        existente = db.query(models.PrecioEventoMesa).filter(
            models.PrecioEventoMesa.evento_id == data.evento_id,
            models.PrecioEventoMesa.mesa_id == data.mesa_id
        ).first()

        if existente:
            existente.precio_reserva = data.precio
            existente.consumo_minimo = data.consumo_minimo
            db.commit()
            db.refresh(existente)
            return {"mensaje": "Mesa actualizada en el evento con éxito", "id": existente.id}
        else:
            nuevo_registro = models.PrecioEventoMesa(
                evento_id=data.evento_id,
                mesa_id=data.mesa_id,
                precio_reserva=data.precio,
                consumo_minimo=data.consumo_minimo
            )
            db.add(nuevo_registro)
            db.commit()
            db.refresh(nuevo_registro)
            return {"mensaje": "Mesa vinculada al evento con éxito", "id": nuevo_registro.id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error al procesar la vinculación: {str(e)}")


@router.put("/{asignacion_id}")
def actualizar_asignacion_por_id(asignacion_id: int, data: ActualizacionAsignacionBase, db: Session = Depends(get_db)):
    """
    Actualiza una asignación existente mediante su ID único.
    """
    registro = db.query(models.PrecioEventoMesa).filter(models.PrecioEventoMesa.id == asignacion_id).first()
    if not registro:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    
    try:
        registro.precio_reserva = data.precio
        registro.consumo_minimo = data.consumo_minimo
            
        db.commit()
        db.refresh(registro)
        return {"mensaje": "Asignación actualizada con éxito", "id": registro.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error al actualizar: {str(e)}")


@router.get("/")
def listar_precios_mesas(local_id: int = None, db: Session = Depends(get_db)):
    query = db.query(models.PrecioEventoMesa)
    if local_id is not None:
        query = query.join(models.Mesa, models.PrecioEventoMesa.mesa_id == models.Mesa.id)\
                     .join(models.Zona, models.Mesa.zona_id == models.Zona.id)\
                     .filter(models.Zona.local_id == local_id)
    registros = query.all()
    return [
        {
            "id": r.id,
            "evento_id": r.evento_id,
            "nombre_evento": r.evento.nombre_evento if r.evento else "Desconocido",
            "mesa_id": r.mesa_id,
            "numero_mesa": r.mesa.numero_mesa if r.mesa else "Desconocida",
            "precio_reserva": float(r.precio_reserva),
            "consumo_minimo": float(r.consumo_minimo),
            "local_id": r.mesa.zona.local_id if r.mesa and r.mesa.zona else None
        } for r in registros
    ]

# ==========================================
# ENDPOINTS DE GESTIÓN DE MESAS Y PLANOS
# ==========================================
@router.post("/mesas")
def crear_mesa(data: dict, db: Session = Depends(get_db)):
    ultimo_id = db.query(func.max(models.Mesa.id)).scalar()
    siguiente_id = (ultimo_id + 1) if ultimo_id else 1
    
    nuevo_registro = models.Mesa(
        id=siguiente_id,
        zona_id=data.get("zona_id"),
        numero_mesa=data.get("numero_mesa"),
        capacidad=data.get("capacidad", 4),
        forma=data.get("forma", "rectangulo"),
        activo=data.get("activo", True)
    )
    db.add(nuevo_registro)
    db.commit()
    db.refresh(nuevo_registro)
    return {"mensaje": "Mesa creada exitosamente", "id": nuevo_registro.id}

@router.delete("/mesas/{mesa_id}")
def eliminar_mesa(mesa_id: int, db: Session = Depends(get_db)):
    mesa = db.query(models.Mesa).filter(models.Mesa.id == mesa_id).first()
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa no encontrada")
    
    db.delete(mesa)
    db.commit()
    return {"mensaje": "Mesa eliminada correctamente"}

@router.put("/mesas/{mesa_id}")
def actualizar_mesa(mesa_id: int, data: dict, db: Session = Depends(get_db)):
    mesa = db.query(models.Mesa).filter(models.Mesa.id == mesa_id).first()
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa no encontrada")
    
    for key, value in data.items():
        if hasattr(mesa, key):
            setattr(mesa, key, value)
        
    db.commit()
    db.refresh(mesa)
    return {"mensaje": "Mesa actualizada correctamente", "mesa": mesa}

@router.post("/plano-mesas/{local_id}")
def subir_plano_mesas(local_id: int, file: UploadFile = File(...)):
    os.makedirs("app/static/planos_mesas", exist_ok=True)
    file_path = f"app/static/planos_mesas/local_{local_id}.png"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"mensaje": "Plano de mesas guardado con éxito", "url": f"/static/planos_mesas/local_{local_id}.png"}

@router.get("/plano-mesas/{local_id}")
def obtener_plano_mesas(local_id: int):
    file_path = f"app/static/planos_mesas/local_{local_id}.png"
    if os.path.exists(file_path):
        return {"url": f"/static/planos_mesas/local_{local_id}.png"}
    return {"url": None}

@router.get("/mesas")
def listar_mesas_por_local(local_id: int = None, db: Session = Depends(get_db)):
    query = db.query(models.Mesa).join(models.Zona, models.Mesa.zona_id == models.Zona.id)
    if local_id is not None:
        query = query.filter(models.Zona.local_id == local_id)
    
    mesas = query.all()
    return [
        {
            "id": m.id,
            "zona_id": m.zona_id,
            "numero_mesa": m.numero_mesa,
            "capacidad": m.capacidad,
            "local_id": m.zona.local_id if m.zona else None
        } for m in mesas
    ]