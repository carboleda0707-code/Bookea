from datetime import date, datetime
import calendar
import configparser
import os
import requests
import streamlit as st

def render_cartelera_publica(api_url):
  """Renderiza la cartelera de eventos de un local específico para usuarios
  NO logueados (Vista Pública). 
  """
  
  # ==========================================
  # 0. OBTENCIÓN DE DATOS DEL LOCAL SELECCIONADO
  # ==========================================
  id_local_actual = st.session_state.get("id_local_actual")
  
  try:
    resp_locales = requests.get(f"{api_url}/locales", timeout=5)
    locales = resp_locales.json() if resp_locales.status_code == 200 else []
  except Exception:
    locales = []

  # Buscar la información completa del local actual
  info_local_actual = None
  if id_local_actual and locales:
    for l in locales:
      if str(l.get("id")) == str(id_local_actual):
        info_local_actual = l
        break

  if not info_local_actual and locales:
    info_local_actual = locales[0]
    st.session_state["id_local_actual"] = info_local_actual.get("id")

  if not info_local_actual:
    info_local_actual = {
        "id": 1,
        "nombre_local": "Mi Local",
        "tipo_establecimiento": "Restaurante/Bar",
        "ciudad": "Guayaquil",
    }

  nombre_local_cal = (
      info_local_actual.get("nombre_local")
      or info_local_actual.get("nombre")
      or "Mi Local"
  )
  tipo_local_cal = (
      info_local_actual.get("tipo_establecimiento")
      or info_local_actual.get("tipo_negocio")
      or "Restaurante/Bar"
  )
  ciudad_local_cal = info_local_actual.get("ciudad", "Local")

  # ==========================================
  # 1. OBTENCIÓN Y FILTRADO DE EVENTOS DEL LOCAL
  # ==========================================
  eventos = []
  eventos_a_mostrar = []

  if id_local_actual:
    try:
      # Intentamos traer los eventos del endpoint específico del local
      resp_l = requests.get(
          f"{api_url}/locales/{id_local_actual}/eventos", timeout=5
      )
      if resp_l.status_code == 200:
        evs_l = resp_l.json()
        if isinstance(evs_l, list):
          eventos = evs_l
    except Exception:
      eventos = []

    # Si por alguna razón el endpoint anterior no devuelve nada, intentamos filtrar de la lista general
    if not eventos:
      try:
        resp_gen = requests.get(f"{api_url}/eventos", timeout=5)
        if resp_gen.status_code == 200:
          todos = resp_gen.json()
          if isinstance(todos, list):
            eventos = [
                e for e in todos 
                if str(e.get("local_id") or e.get("establecimiento_id")) == str(id_local_actual)
            ]
      except Exception:
        pass

  for ev in eventos:
    estado_ev = str(ev.get("estado", "activo")).strip().lower()
    if estado_ev in ["pendiente", "rechazado"]:
      continue
    eventos_a_mostrar.append(ev)

  # Si la lista está vacía, forzamos la Plantilla "Tu Evento" para que la UI muestre contenido
  if not eventos_a_mostrar:
    eventos_a_mostrar = [{
        "id": 999,
        "titulo": "Tu Evento",
        "estado": "plantilla",
        "fecha": "Personalizada",
        "artista_orquesta": "A tu elección"
    }]

  # ==========================================
  # 2. ENCABEZADO DE LA CARTELERA PÚBLICA
  # ==========================================
  st.markdown(
      f"""
      ##### 🗓️ Cartelera de Eventos - {nombre_local_cal}
      #📍 **Ubicación:** {ciudad_local_cal} | **Tipo:** {tipo_local_cal}  
      *Explora Eventos o Crea el tuyo - reserva iniciando sesión.*
      """, unsafe_allow_html=True, )
  
  # ==========================================
  # 3. DISTRIBUCIÓN EN 4 COLUMNAS DE TARJETAS
  # ==========================================
  num_columnas = 3
  cols = st.columns(num_columnas)

  for i, evento in enumerate(eventos_a_mostrar):
    evento_id = evento.get("id")
    nombre_ev = evento.get("titulo") or evento.get("nombre_evento", "Sin nombre")
    estado_ev = str(evento.get("estado", "")).strip().lower()
    es_tu_evento = (
        estado_ev == "plantilla"
        or str(nombre_ev).strip().lower() == "tu evento"
    )

    col_actual = cols[i % num_columnas]

    with col_actual.container(border=True):
      nombre_imagen = evento.get("imagen")
      imagen_encontrada = None
      posibles_nombres = []
      
      if nombre_imagen:
        posibles_nombres.append(str(nombre_imagen))

      posibles_nombres.append(f"eventos_{evento_id}.jpg")
      posibles_nombres.append(f"eventos_{evento_id}.png")
      
      if es_tu_evento:
        posibles_nombres.append("Tu Evento.png")
        posibles_nombres.append("Tu Evento.jpg")

      for nom in posibles_nombres:
        limpio = os.path.basename(nom)
        rutas_prueba = [
            os.path.join("static", "uploads", limpio),
            os.path.join("app", "static", "uploads", limpio),
            os.path.join("static", "uploads", "diseño", limpio),
            os.path.join("app", "static", "uploads", "diseño", limpio),
        ]
        for r in rutas_prueba:
          if os.path.exists(r):
            imagen_encontrada = r
            break
        if imagen_encontrada:
          break

      if imagen_encontrada:
        st.image(imagen_encontrada, use_container_width=True)
      else:
        st.markdown("🎧 **Experiencia Bookea**  \n*Evento Exclusivo*", unsafe_allow_html=True)
      
      st.markdown(f"#### {nombre_ev}")

      if es_tu_evento:
        st.markdown("📅 Fecha personalizada")
        st.markdown("🎤 A tu elección")
        
        if st.button(
            "✨ Reservar / Crear",
            key=f"pub_tu_evento_{evento_id}_{i}",
            use_container_width=True,
            type="primary"
        ):
          st.session_state.evento_a_reservar = evento_id
          st.session_state.vista_actual_publica = "login"
          st.rerun()
      else:
        fecha_corta = evento.get("fecha", "N/A")
        artista = evento.get("artista_orquesta", "N/A")
        st.markdown(f"📅 {fecha_corta}")
        st.markdown(f"🎤 {artista}")

        if st.button(
            "Reservar Evento",
            key=f"pub_res_grid_{evento_id}_{i}",
            use_container_width=True,
            type="primary"
        ):
          st.session_state.evento_a_reservar = evento_id
          st.session_state.vista_actual_publica = "login"
          st.rerun()
          