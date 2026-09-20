from datetime import datetime
import math
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from .. import models
from ..database import get_db
from ..schemas import LocalCreate, LocalResponse

router = APIRouter(prefix="/locales", tags=["Locales y Sucursales"])


def calcular_distancia(lat1, lon1, lat2, lon2):
  """Calcula la distancia en kilómetros entre dos puntos geográficos (Fórmula de Haversine)."""
  if not lat1 or not lon1 or not lat2 or not lon2:
    return 999999

  R = 6371
  dlat = math.radians(lat2 - lat1)
  dlon = math.radians(lon2 - lon1)
  a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(
      math.radians(lat1)
  ) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
  return R * c


# --- RUTAS PARA EL PROPIETARIO ---


@router.post("/", response_model=dict)
def crear_sucursal(local_data: LocalCreate, db: Session = Depends(get_db)):
  """Permite registrar un nuevo local/sucursal vinculado a la base de datos."""
  nuevo_local = models.Local(
      nombre=getattr(local_data, "nombre_local", getattr(local_data, "nombre", "Establecimiento Principal")),
      tipo_establecimiento=getattr(local_data, "tipo_establecimiento", getattr(local_data, "tipo_negocio", "Restaurant")),
      direccion=getattr(local_data, "direccion", "Dirección Principal"),
      ciudad=getattr(local_data, "ciudad", "Samborondón"),
      email_contacto=getattr(local_data, "email_contacto", "contacto@establecimiento.com"),
      telefono=getattr(local_data, "telefono", getattr(local_data, "telefono_contacto", "0999999999")),
      activo=True,
      slug="establecimiento-principal",
  )

  db.add(nuevo_local)
  db.commit()
  db.refresh(nuevo_local)

  return {"mensaje": "Local registrado exitosamente.", "local_id": nuevo_local.id}


@router.get("/", response_model=List[dict])
def listar_todos_los_locales(
    propietario_id: int = None, db: Session = Depends(get_db)
):
  """Lista los locales incluyendo dirección, teléfono, correo y RUC de la empresa."""
  query = db.query(models.Local)
  if propietario_id:
    query = query.filter(models.Local.propietario_id == propietario_id)

  locales = query.all()
  resultado = []
  for loc in locales:
    ruc_empresa = loc.empresa.ruc_nit if hasattr(loc, "empresa") and loc.empresa else ""
    resultado.append({
        "id": loc.id,
        "nombre_local": loc.nombre,
        "nombre": loc.nombre,
        "tipo_establecimiento": loc.tipo_establecimiento,
        "ciudad": loc.ciudad,
        "direccion": getattr(loc, "direccion", "S/D"),
        "telefono_contacto": getattr(
            loc, "telefono", getattr(loc, "telefono_contacto", "S/D")
        ),
        "email_contacto": getattr(loc, "email_contacto", ""),
        "ruc_nit": ruc_empresa,
        "slug": loc.slug,
        "activo": loc.activo,
        "likes": loc.likes or 0,
    })
  return resultado


@router.get("/cercanos", response_model=List[dict])
def obtener_locales_cercanos(
    lat: float = Query(..., description="Latitud del usuario"),
    lon: float = Query(..., description="Longitud del usuario"),
    ciudad: str = Query(None, description="Filtrar opcionalmente por ciudad"),
    db: Session = Depends(get_db),
):
  """Calcula la distancia de los locales activos respecto a las coordenadas del usuario y los ordena por cercanía."""
  query = db.query(models.Local).filter(models.Local.activo == True)

  if ciudad and ciudad != "Todas":
    query = query.filter(models.Local.ciudad.ilike(f"%{ciudad}%"))

  locales = query.all()
  locales_cercanos = []

  for loc in locales:
    l_lat = getattr(loc, "latitud", None)
    l_lon = getattr(loc, "longitud", None)

    distancia = calcular_distancia(lat, lon, l_lat, l_lon)

    locales_cercanos.append({
        "id": loc.id,
        "nombre_local": loc.nombre,
        "tipo_establecimiento": loc.tipo_establecimiento,
        "ciudad": getattr(loc, "ciudad", "Samborondón"),
        "pais": getattr(loc, "pais", "Ecuador"),
        "latitud": l_lat,
        "longitud": l_lon,
        "slug": loc.slug,
        "activo": loc.activo,
        "distancia_km": round(distancia, 2),
        "likes": loc.likes or 0,
    })

  locales_cercanos.sort(key=lambda x: x["distancia_km"])
  return locales_cercanos


@router.get("/{local_id}/eventos-propietario", response_model=List[dict])
def listar_eventos_propietario(local_id: int, db: Session = Depends(get_db)):
  """Retorna todos los eventos y la plantilla de un local para la gestión del propietario."""
  eventos = (
      db.query(models.Evento)
      .filter(models.Evento.local_id == local_id)
      .all()
  )

  resultado = []
  for ev in eventos:
    fecha_str = (
        ev.fecha_hora.strftime("%Y-%m-%d %H:%M:%S") if ev.fecha_hora else ""
    )

    resultado.append({
        "id": ev.id,
        "local_id": ev.local_id,
        "nombre_evento": ev.nombre_evento,
        "descripcion": ev.descripcion or "",
        "artista_orquesta": getattr(ev, "artista_orquesta", ""),
        "estado": ev.estado,
        "fecha_hora": fecha_str,
        "imagen": getattr(ev, "imagen", None),
    })
  return resultado


@router.get("/empresa/{empresa_id}", response_model=List[dict])
def listar_locales_por_empresa(empresa_id: str, db: Session = Depends(get_db)):
  """Lista locales filtrados por empresa incluyendo RUC y correo."""
  locales = (
      db.query(models.Local)
      .filter(models.Local.empresa_id == empresa_id)
      .all()
  )
  resultado = []
  for loc in locales:
    ruc_empresa = loc.empresa.ruc_nit if hasattr(loc, "empresa") and loc.empresa else ""
    resultado.append({
        "id": loc.id,
        "nombre_local": loc.nombre,
        "nombre": loc.nombre,
        "tipo_establecimiento": loc.tipo_establecimiento,
        "ciudad": loc.ciudad,
        "direccion": getattr(loc, "direccion", ""),
        "telefono_contacto": getattr(loc, "telefono", getattr(loc, "telefono_contacto", "")),
        "email_contacto": getattr(loc, "email_contacto", ""),
        "ruc_nit": ruc_empresa,
        "slug": loc.slug,
        "activo": loc.activo,
        "likes": loc.likes or 0,
    })
  return resultado


# --- RUTA DE CONFIGURACIÓN PARA WHATSAPP ---


@router.get("/configuracion/")
def obtener_configuracion_local(
    local_id: int = Query(None, description="ID opcional del local actual"),
    db: Session = Depends(get_db),
):
  """Retorna la configuración del local para el envío de alertas por WhatsApp."""
  if local_id:
    local = db.query(models.Local).filter(models.Local.id == local_id).first()
  else:
    local = db.query(models.Local.id == 1).first()

  if not local:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Configuración de local no encontrada",
    )

  return {
      "nombre_local": local.nombre,
      "celular_remitente": getattr(local, "telefono", "")
      or getattr(local, "telefono_contacto", ""),
      "direccion": local.direccion,
      "email_contacto": local.email_contacto,
  }


# --- RUTAS EXCLUSIVAS PARA EL SUPERADMINISTRADOR ---


@router.patch("/superadmin/configurar/{local_id}")
def superadmin_activar_y_asignar_slug(
    local_id: int, slug: str, activo: bool, db: Session = Depends(get_db)
):
  """Permite al Superadmin asignar la URL amigable (slug) y cambiar el estado de activación."""
  local = db.query(models.Local).filter(models.Local.id == local_id).first()
  if not local:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Local no encontrado."
    )

  slug_limpio = slug.strip().lower()
  slug_existente = (
      db.query(models.Local)
      .filter(models.Local.slug == slug_limpio, models.Local.id != local_id)
      .first()
  )
  if slug_existente:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="El slug ingresado ya está en uso por otro establecimiento.",
    )

  local.slug = slug_limpio
  local.activo = activo

  db.commit()
  return {
      "mensaje": f"Local '{local.nombre}' actualizado correctamente.",
      "slug": local.slug,
      "activo": local.activo,
  }


# --- RUTA PARA DAR LIKE A UN LOCAL ---


@router.post("/{local_id}/like", response_model=dict)
def dar_like_local(local_id: int, db: Session = Depends(get_db)):
  """Incrementa en 1 el contador de likes del local y lo guarda en la base de datos."""
  local = db.query(models.Local).filter(models.Local.id == local_id).first()
  if not local:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Local no encontrado."
    )

  local.likes = (local.likes or 0) + 1
  db.commit()
  db.refresh(local)

  return {"mensaje": "Like registrado exitosamente.", "likes": local.likes}


@router.get("/{identificador}", response_model=dict)
def obtener_local_por_id_o_slug(identificador: str, db: Session = Depends(get_db)):
  """Busca un local ya sea por ID numérico o por su slug amigable, devolviendo RUC y correo."""
  local = None
  if identificador.isdigit():
    local = (
        db.query(models.Local)
        .filter(models.Local.id == int(identificador))
        .first()
    )

  if not local:
    local = (
        db.query(models.Local)
        .filter(models.Local.slug.ilike(identificador.strip()))
        .first()
    )

  if not local:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Local no encontrado."
    )

  ruc_empresa = local.empresa.ruc_nit if hasattr(local, "empresa") and local.empresa else ""

  return {
      "id": local.id,
      "nombre": local.nombre,
      "nombre_local": local.nombre,
      "tipo_establecimiento": local.tipo_establecimiento,
      "descripcion": getattr(
          local, "descripcion", "Bienvenidos a nuestra mini web de reservas."
      ),
      "imagen_url": getattr(local, "imagen_url", ""),
      "slug": local.slug,
      "activo": local.activo,
      "direccion": getattr(local, "direccion", "Dirección no especificada"),
      "telefono_contacto": getattr(
          local, "telefono", getattr(local, "telefono_contacto", "S/D")
      ),
      "email_contacto": getattr(local, "email_contacto", ""),
      "ruc_nit": ruc_empresa,
      "ciudad": getattr(local, "ciudad", "Samborondón"),
      "likes": local.likes or 0,
  }


# --- RUTAS DE EVENTOS Y CARTELERA PARA LA MINI WEB ---


@router.get("/{local_id}/eventos", response_model=List[dict])
def listar_eventos_por_local(local_id: int, db: Session = Depends(get_db)):
  """Retorna la cartelera de eventos activos, plantilla y confirmados de un local específico."""
  eventos = (
      db.query(models.Evento)
      .filter(
          models.Evento.local_id == local_id,
          (models.Evento.estado == "plantilla")
          | (models.Evento.estado == "activo")
          | (models.Evento.estado == "pendiente")
          | (models.Evento.estado == "confirmado")
          | (models.Evento.estado == None),
      )
      .all()
  )

  resultado = []
  for ev in eventos:
    fecha_str = ev.fecha_hora.strftime("%Y-%m-%d") if ev.fecha_hora else ""
    hora_str = ev.fecha_hora.strftime("%H:%M") if ev.fecha_hora else ""

    resultado.append({
        "id": ev.id,
        "titulo": ev.nombre_evento,
        "descripcion": ev.descripcion or "",
        "fecha": fecha_str,
        "hora": hora_str,
        "estado": ev.estado,
        "imagen": getattr(ev, "imagen", None),
    })
  return resultado


@router.post("/eventos/", response_model=dict)
def crear_evento_desde_web(evento_data: dict, db: Session = Depends(get_db)):
  """Permite al propietario registrar un nuevo evento en la cartelera desde el panel móvil."""
  fecha_str = evento_data.get("fecha")
  hora_str = evento_data.get("hora", "00:00")

  try:
    fecha_hora_dt = datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
  except ValueError:
    fecha_hora_dt = datetime.utcnow()

  nuevo_evento = models.Evento(
      local_id=evento_data.get("local_id"),
      nombre_evento=evento_data.get("titulo"),
      descripcion=evento_data.get("descripcion"),
      fecha_hora=fecha_hora_dt,
      estado="activo",
  )

  db.add(nuevo_evento)
  db.commit()
  db.refresh(nuevo_evento)

  return {
      "mensaje": "Evento creado exitosamente en la cartelera.",
      "evento_id": nuevo_evento.id,
  }