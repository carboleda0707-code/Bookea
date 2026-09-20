from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# --- Esquemas para Reservas ---
class ReservaCreate(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    evento_id: int
    mesas_ids: List[int]
    cliente_id: int
    cantidad_personas: int
    tipo_celebracion: Optional[str] = "ninguna"


class ReservaResponse(BaseModel):
    id: int
    evento_id: int
    mesa_id: int
    cliente_id: int
    cantidad_personas: int
    tipo_celebracion: str
    estado_reserva: str
    codigo_reserva: str
    comprobante_pago: Optional[str] = None
    mensaje_personalizado: Optional[str] = None  # <--- ¡Añade esta línea aquí!
    creado_en: datetime

    class Config:
        from_attributes = True


# --- Esquemas para Empresa y Local ---
class EmpresaBase(BaseModel):
    nombre_comercial: str
    ruc_nit: str

class EmpresaCreate(EmpresaBase):
    pass

class EmpresaResponse(EmpresaBase):
    id: int
    activo: bool
    creado_en: datetime

    class Config:
        from_attributes = True


class LocalBase(BaseModel):
    nombre_local: str = Field(..., min_length=2, max_length=100)
    tipo_negocio: Optional[str] = "gastronomico"
    tipo_establecimiento: Optional[str] = "Restaurante/Bar"
    tipo_cocina: Optional[str] = None
    zona_ubicacion: Optional[str] = None
    aforo_maximo: Optional[int] = 100
    direccion: str = Field(..., min_length=5)
    ciudad: str = Field(..., min_length=2)
    email_contacto: EmailStr
    telefono: str = Field(..., min_length=7, max_length=20)

class LocalCreate(LocalBase):
    empresa_id: Optional[int] = None 

class LocalUpdate(BaseModel):
    nombre_local: Optional[str] = Field(None, min_length=2, max_length=100)
    tipo_negocio: Optional[str] = None
    tipo_establecimiento: Optional[str] = None
    tipo_cocina: Optional[str] = None
    zona_ubicacion: Optional[str] = None
    aforo_maximo: Optional[int] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    email_contacto: Optional[EmailStr] = None
    telefono: Optional[str] = None

class LocalResponse(LocalBase):
    id: int
    empresa_id: int
    slug: Optional[str] = None
    activo: bool
    creado_en: datetime

    class Config:
        from_attributes = True


# --- Esquemas para Zonas y Mesas ---
class ZonaBase(BaseModel):
    nombre_zona: str
    descripcion: Optional[str] = None

class ZonaCreate(ZonaBase):
    local_id: int

class ZonaResponse(ZonaBase):
    id: int
    local_id: int

    class Config:
        from_attributes = True


class MesaBase(BaseModel):
    numero_mesa: str
    capacidad: int
    forma: Optional[str] = "rectangulo"
    pos_x: Optional[int] = 0
    pos_y: Optional[int] = 0

class MesaCreate(MesaBase):
    zona_id: int

class MesaResponse(MesaBase):
    id: int
    zona_id: int
    activo: bool

    class Config:
        from_attributes = True


# --- Esquemas para Eventos y Precios ---
class EventoBase(BaseModel):
    nombre_evento: str
    artista_orquesta: Optional[str] = None
    genero_musical: Optional[str] = None
    incluye_piqueos: Optional[bool] = False
    tipo_ambiente: Optional[str] = None
    capacidad_total: Optional[int] = 50
    fecha_hora: datetime
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    estado: Optional[str] = "programado"  # <--- Agregado aquí para que sea opcional al crear

class EventoCreate(EventoBase):
    local_id: int

class EventoResponse(EventoBase):
    id: int
    local_id: int
    estado: str

    class Config:
        from_attributes = True


class PrecioMesaCreate(BaseModel):
    evento_id: int
    mesa_id: int
    precio_reserva: float
    consumo_minimo: float


# --- Esquemas para Clientes y Reservas ---
class ClienteBase(BaseModel):
    nombres: str
    apellidos: str
    whatsapp: str
    correo: Optional[str] = None
    cedula: Optional[str] = None

class ClienteCreate(ClienteBase):
    pass

class ClienteResponse(ClienteBase):
    id: int
    creado_en: datetime

    class Config:
        from_attributes = True
        
# --- Esquema para Actualización de Ubicación GPS ---
class UbicacionUpdate(BaseModel):
    latitud: float
    longitud: float