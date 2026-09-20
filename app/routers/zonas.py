from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
import shutil
import os

router = APIRouter(prefix="/zonas", tags=["Zonas"])

@router.get("/")
def listar_zonas(local_id: int = None, db: Session = Depends(get_db)):
    query = db.query(models.Zona)
    if local_id:
        query = query.filter(models.Zona.local_id == local_id)
    return query.all()

@router.post("/", response_model=schemas.ZonaResponse)
def crear_zona(zona: schemas.ZonaCreate, db: Session = Depends(get_db)):
    ultimo_registro = db.query(models.Zona).order_by(models.Zona.id.desc()).first()
    nuevo_id = (ultimo_registro.id + 1) if ultimo_registro else 1
    
    datos_zona = zona.dict()
    datos_zona["id"] = nuevo_id
    
    nueva_zona = models.Zona(**datos_zona)
    db.add(nueva_zona)
    db.commit()
    db.refresh(nueva_zona)
    return nueva_zona

# ==========================================
# ENDPOINT AGREGADO PARA ACTUALIZAR ZONAS
# ==========================================
@router.put("/{zona_id}", response_model=schemas.ZonaResponse)
def actualizar_zona(zona_id: int, zona: schemas.ZonaCreate, db: Session = Depends(get_db)):
    zona_db = db.query(models.Zona).filter(models.Zona.id == zona_id).first()
    if not zona_db:
        raise HTTPException(status_code=404, detail="Zona no encontrada")
    
    zona_db.nombre_zona = zona.nombre_zona
    zona_db.descripcion = zona.descripcion
    zona_db.local_id = zona.local_id
    
    db.commit()
    db.refresh(zona_db)
    return zona_db

@router.delete("/{zona_id}")
def eliminar_zona(zona_id: int, db: Session = Depends(get_db)):
    zona = db.query(models.Zona).filter(models.Zona.id == zona_id).first()
    if not zona:
        raise HTTPException(status_code=404, detail="Zona no encontrada")
    
    db.delete(zona)
    db.commit()
    return {"mensaje": "Zona eliminada correctamente"}

# ==========================================
# ENDPOINTS PARA EL PLANO DE DISTRIBUCIÓN
# ==========================================
@router.post("/plano/{local_id}")
def subir_plano_local(local_id: int, file: UploadFile = File(...)):
    os.makedirs("app/static/planos", exist_ok=True)
    file_path = f"app/static/planos/local_{local_id}.png"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"mensaje": "Plano guardado con éxito", "url": f"/static/planos/local_{local_id}.png"}

@router.get("/plano/{local_id}")
def obtener_plano_local(local_id: int):
    file_path = f"app/static/planos/local_{local_id}.png"
    if os.path.exists(file_path):
        return {"url": f"/static/planos/local_{local_id}.png"}
    return {"url": None}