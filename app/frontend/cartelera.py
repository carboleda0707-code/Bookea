from datetime import date, datetime
import calendar
import configparser
import os
import requests
import streamlit as st
from filtro_locales import render_filtro_locales
from pie_pagina import render_pie_pagina
from header_global import render_header

def render_cartelera(api_url, cliente_id=None):
  
  # ==========================================================
  # RENDERIZAR CABECERA GLOBAL UNIFICADA
  # ==========================================================
  render_header("Catálogo de Eventos")

  # ==========================================
  # 0.1. CARGA DE PAÍSES Y CONFIGURACIÓN INI
  # ==========================================
  config_paises = configparser.ConfigParser()
  if os.path.exists("paises.ini"):
    config_paises.read("paises.ini", encoding="utf-8")
  paises_dict = (
      dict(config_paises["PREFIJOS"])
      if "PREFIJOS" in config_paises
      else {"Ecuador": "+593"}
  )
  paises_dict = {pais.title(): prefijo for pais, prefijo in paises_dict.items()}

  # ==========================================
  # 0.2. OBTENCIÓN ROBUSTA DE LOCALES
  # ==========================================
  try:
    resp_locales = requests.get(f"{api_url}/locales", timeout=5)
    locales = resp_locales.json() if resp_locales.status_code == 200 else []
  except Exception:
    locales = []

  if not locales:
    locales = [{
        "id": 1,
        "nombre": "Mi Local",
        "tipo_establecimiento": "Restaurante/Bar",
        "ciudad": "Guayaquil",
        "pais": "Ecuador",
        "direccion": "Av. Principal 123",
        "telefono_contacto": "0999999999"
    }]

  # ==========================================
  # 0.3. DETECCIÓN DEL LOCAL INICIAL (OPTIMIZADO)
  # ==========================================
  from sesion_local import obtener_local_actual, fijar_local_actual
  
  local_inicial = obtener_local_actual(locales)

  if not local_inicial and locales:
    local_inicial = locales[0]

  def_id = local_inicial.get("id")

  # ==========================================
  # 1. VERIFICACIÓN CONDICIONAL DE BÚSQUEDA / FILTROS
  # ==========================================
  menu_cliente_actual = (
      st.session_state.get("menu_cliente_actual") 
      or st.session_state.get("menu_cliente") 
      or st.session_state.get("seleccion_menu") 
      or "Catálogo de Eventos"
  )
  
  busqueda_evento = st.session_state.get("busqueda_evento", "")
  
  if "buscar" in menu_cliente_actual.lower() or "local" in menu_cliente_actual.lower():
      info_local_actual, busqueda_evento, _ = render_filtro_locales(api_url)
      id_local_actual = info_local_actual.get("id")
      fijar_local_actual(id_local_actual)
  else:
      id_local_actual = local_inicial.get("id")
      info_local_actual = local_inicial

  st.session_state["id_local_actual"] = id_local_actual

  # ==========================================
  # 🔍 CONSULTA AUTOMÁTICA DE DETALLE
  # ==========================================
  if id_local_actual:
    try:
      resp_det = requests.get(f"{api_url}/locales/{id_local_actual}", timeout=3)
      if resp_det.status_code == 200:
        detalles_remotos = resp_det.json()
        if isinstance(detalles_remotos, dict):
          info_local_actual.update(detalles_remotos)
    except Exception:
      pass

  # ==========================================
  # 2. OBTENCIÓN Y FILTRADO DE EVENTOS
  # ==========================================
  eventos = []
  if id_local_actual:
    try:
      cliente_email_actual = (
          st.session_state.get("user_email")
          or st.session_state.get("email")
          or st.session_state.get("correo")
          or ""
      )
      
      params_ev = {"local_id": id_local_actual}
      if cliente_email_actual:
        params_ev["cliente_email"] = cliente_email_actual

      resp_l = requests.get(
          f"{api_url}/reservas/eventos/", params=params_ev, timeout=5
      )
      if resp_l.status_code == 200:
        evs_l = resp_l.json()
        if isinstance(evs_l, list):
          eventos = evs_l
    except Exception:
      eventos = []

  eventos_a_mostrar = []
  for ev in eventos:
    nombre_ev_str = (
        str(ev.get("titulo") or ev.get("nombre_evento", "")).strip().lower()
    )
    estado_ev = str(ev.get("estado", "activo")).strip().lower()

    if estado_ev in ["pendiente", "rechazado"]:
      continue

    es_plantilla = estado_ev == "plantilla" or nombre_ev_str == "tu evento"

    ev_local_id = ev.get("local_id")
    if ev_local_id is not None and id_local_actual is not None:
      if str(ev_local_id).strip() != str(id_local_actual).strip():
        continue

    if es_plantilla:
      eventos_a_mostrar.append(ev)
      continue

    if busqueda_evento:
      term = busqueda_evento.strip().lower()
      artista_str = str(ev.get("artista_orquesta", "")).lower()
      desc_str = str(ev.get("descripcion", "")).lower()
      if term in nombre_ev_str or term in artista_str or term in desc_str:
        eventos_a_mostrar.append(ev)
    else:
      eventos_a_mostrar.append(ev)

  plantilla_tu_evento = [
      ev
      for ev in eventos_a_mostrar
      if str(ev.get("estado", "")).strip().lower() == "plantilla"
      or str(ev.get("titulo") or ev.get("nombre_evento", ""))
      .strip()
      .lower()
      == "tu evento"
  ]
  otros_eventos = [ev for ev in eventos_a_mostrar if ev not in plantilla_tu_evento]
  otros_eventos = sorted(otros_eventos, key=lambda x: x.get("id", 0), reverse=True)
  eventos_a_mostrar = plantilla_tu_evento + otros_eventos

  if (
      "filtro_fecha_comensal" in st.session_state
      and st.session_state.filtro_fecha_comensal
  ):
    f_sel = st.session_state.filtro_fecha_comensal
    eventos_filtrados_por_fecha = []
    for ev in eventos_a_mostrar:
      estado_ev = str(ev.get("estado", "")).strip().lower()
      nombre_ev = (
          str(ev.get("titulo") or ev.get("nombre_evento", "")).strip().lower()
      )
      f_raw = str(ev.get("fecha_hora", "") or ev.get("fecha", ""))
      if estado_ev == "plantilla" or nombre_ev == "tu evento":
        eventos_filtrados_por_fecha.append(ev)
      elif f_sel in f_raw:
        eventos_filtrados_por_fecha.append(ev)
    eventos_a_mostrar = eventos_filtrados_por_fecha

  # ==========================================
  # EXTRACCIÓN DE DATOS DEL LOCAL
  # ==========================================
  nombre_local_cal = (
      info_local_actual.get("nombre")
      or info_local_actual.get("nombre_local")
      or "Mi Local"
  )
  tipo_local_cal = (
      info_local_actual.get("tipo_establecimiento")
      or info_local_actual.get("tipo_negocio")
      or "Restaurante/Bar"
  )
  ciudad_local_cal = (
      info_local_actual.get("ciudad") 
      or info_local_actual.get("zona_ubicacion") 
      or "Local"
  )
  direccion_local_cal = (
      info_local_actual.get("direccion")
      or info_local_actual.get("direccion_local")
      or info_local_actual.get("ubicacion")
      or "S/D"
  )
  telefono_local_cal = (
      info_local_actual.get("telefono_contacto")
      or info_local_actual.get("telefono")
      or info_local_actual.get("celular")
      or "S/D"
  )

  num_evs = len(eventos_a_mostrar)
  if num_evs == 1:
    MAX_COLS = 1
    ancho_bloque_px = 260
    elementos_render = eventos_a_mostrar
  elif num_evs == 2:
    MAX_COLS = 4
    ancho_bloque_px = 1040
    elementos_render = [None, eventos_a_mostrar[0], eventos_a_mostrar[1], None]
  elif num_evs == 3:
    MAX_COLS = 3
    ancho_bloque_px = 780
    elementos_render = eventos_a_mostrar
  else:
    MAX_COLS = 4
    ancho_bloque_px = 1040
    elementos_render = eventos_a_mostrar

  # ==========================================
  # 2.5. CABECERA UNIFICADA Y BOTÓN "ME GUSTA" AL LADO
  # ==========================================
  col_caja_info, col_caja_like = st.columns([ancho_bloque_px, 160])

  with col_caja_info:
      st.markdown(f"""
      <div style="background: rgba(16, 14, 36, 0.85); border: 1px solid rgba(150, 55, 255, 0.35); padding: 8px 12px; border-radius: 8px; max-width: 850px; margin: 0 auto;">
          <div style="display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 4px;">
              <h3 style="color: #ffffff; font-size: 13px; font-weight: 800; margin: 0;">🗓️ Eventos - {nombre_local_cal}</h3>
              <span style="font-size: 15px; color: #ffffff; background: rgba(150, 55, 255, 0.2); padding: 2px 6px; border-radius: 4px;">{tipo_local_cal}</span>
          </div>
          <hr style="border: none; border-top: 1px solid rgba(150, 55, 255, 0.2); margin: 4px 0;">
          <p style="font-size: 10px; color: #d6d5df; margin: 0; line-height: 1.3; text-align: center;">
              📍 <b>Ciudad:</b> {ciudad_local_cal} &nbsp;|&nbsp; 
              🏠 <b>Dirección:</b> {direccion_local_cal} &nbsp;|&nbsp; 
              📞 <b>Teléfono:</b> {telefono_local_cal} &nbsp;|&nbsp; 
              🎟️ <b>Encontrados:</b> {len(eventos_a_mostrar)}
          </p>
      </div>
      """, unsafe_allow_html=True)

  with col_caja_like:
      st.markdown("<div style='margin-top: 2px;'></div>", unsafe_allow_html=True)
      likes_actuales = info_local_actual.get("likes", 0) or 0
      if st.button(f"❤️ Like ({likes_actuales})", key=f"btn_like_local_{id_local_actual}", use_container_width=True):
          try:
              resp_like = requests.post(f"{api_url}/auth/locales/{id_local_actual}/like", timeout=3)
              if resp_like.status_code == 200:
                  data_like = resp_like.json()
                  st.toast(f"¡Gracias por tu like! ❤️ (Total: {data_like.get('likes')})")
                  st.rerun()
              else:
                  st.error("No se pudo registrar el like")
          except Exception:
            st.error("Error de conexión con el servidor")

  st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

  # ==========================================
  # 3. VISTA: CALENDARIO DEL MES
  # ==========================================
  vista_seleccionada = st.session_state.get("modo_vista_cartelera", "📅 Agenda de Eventos")
  if vista_seleccionada == "🗓️ Calendario del Mes":
    st.subheader("📅 Calendario del Mes")

    col_m1, col_m2 = st.columns(2)
    with col_m1:
      mes_actual = st.selectbox(
          "Mes",
          list(range(1, 13)),
          format_func=lambda x: calendar.month_name[x],
          index=date.today().month - 1,
          key="comensal_mes_sel",
      )
    with col_m2:
      anio_actual = st.number_input(
          "Año",
          min_value=2024,
          max_value=2035,
          value=date.today().year,
          key="comensal_anio_sel",
      )

    eventos_para_calendario = [
        ev
        for ev in eventos_a_mostrar
        if str(ev.get("estado", "")).strip().lower() not in ["plantilla"]
        and str(ev.get("titulo") or ev.get("nombre_evento", ""))
        .strip()
        .lower()
        != "tu evento"
    ]

    fechas_con_eventos = set()
    for ev in eventos_para_calendario:
      f_raw = ev.get("fecha_hora", "") or ev.get("fecha", "")
      if "T" in f_raw:
        fechas_con_eventos.add(f_raw.split("T")[0])
      elif len(f_raw) >= 10:
        fechas_con_eventos.add(f_raw[:10])

    cal = calendar.Calendar(firstweekday=0)
    dias_mes = cal.monthdatescalendar(anio_actual, mes_actual)

    if (
        "filtro_fecha_comensal" in st.session_state
        and st.session_state.filtro_fecha_comensal
    ):
      f_activa = st.session_state.filtro_fecha_comensal
      st.info(f"🔍 Filtrando por: {f_activa}")
      if st.button("🔄 Ver todos los eventos", use_container_width=True):
        del st.session_state.filtro_fecha_comensal
        st.rerun()

    dias_semana = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    cols_sem = st.columns(7)
    for idx, d_nom in enumerate(dias_semana):
      cols_sem[idx].markdown(
          f"<div style='text-align: center; font-size: 10px; color: #00cfff;"
          f" font-weight: bold;'>{d_nom}</div>",
          unsafe_allow_html=True,
      )

    for semana in dias_mes:
      cols_semana = st.columns(7)
      for idx, dia in enumerate(semana):
        str_dia = dia.strftime("%Y-%m-%d")
        es_mes_actual = dia.month == mes_actual
        tiene_evento = str_dia in fechas_con_eventos
        es_seleccionado = (
            st.session_state.get("filtro_fecha_comensal") == str_dia
        )

        with cols_semana[idx]:
          if not es_mes_actual:
            st.markdown(
                f"<div style='text-align: center; color: #4a5568; font-size:"
                f" 10px; padding: 4px;'>{dia.day}</div>",
                unsafe_allow_html=True,
            )
          elif not tiene_evento:
            st.markdown(
                f"<div style='text-align: center; color: #ffffff; font-size:"
                f" 11px; font-weight: 500; padding: 6px 0px;'>{dia.day}</div>",
                unsafe_allow_html=True,
            )
          else:
            btn_label = f"🟢 {dia.day}" if es_seleccionado else f"{dia.day} 🟢"
            if st.button(
                btn_label, key=f"comensal_btn_dia_{str_dia}", use_container_width=True
            ):
              if es_seleccionado:
                del st.session_state.filtro_fecha_comensal
              else:
                st.session_state.filtro_fecha_comensal = str_dia
              st.rerun()

    st.markdown(
        "<p style='font-size: 11px; color: #00cfff; margin-top: 4px;'>🟢 Días"
        " con eventos (haz clic para filtrar).</p>",
        unsafe_allow_html=True,
    )

  # ==========================================
  # 4. VISTA: AGENDA DE EVENTOS (GRILLA RESPONSIVA)
  # ==========================================
  if not eventos_a_mostrar:
    st.info(
        "Entra a Catálogo de Eventos y busca tu local preferido"
    )
  else:
    for i_lote in range(0, len(elementos_render), MAX_COLS):
      lote_actual = elementos_render[i_lote:i_lote + MAX_COLS]
      cols = st.columns(MAX_COLS)

      for j in range(MAX_COLS):
        with cols[j]:
          if j < len(lote_actual) and lote_actual[j] is not None:
            evento = lote_actual[j]
            evento_id = evento.get("id")
            i_global = i_lote + j
            nombre_ev = (
                evento.get("titulo") or evento.get("nombre_evento", "Sin nombre")
            )

            estado_ev = str(evento.get("estado", "")).strip().lower()
            es_tu_evento = (
                estado_ev == "plantilla"
                or str(nombre_ev).strip().lower() == "tu evento"
            )

            with st.container(border=True):
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
                st.markdown(
                    """
                    <div class="card-no-image">
                        <span style="font-size: 18px;">🎧</span><br>
                        <b style="color: #ffffff; font-size: 10px;">Reserva tu Espacio</b><br>
                        <span style="font-size: 9px; color: #d6d5df;">Sin póster</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

              st.markdown(
                  f"<p class='card-title' title='{nombre_ev}'>{nombre_ev}</p>",
                  unsafe_allow_html=True,
              )

              if es_tu_evento:
                st.markdown(
                    "<p class='card-text'>📅 Fecha personalizada</p>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    "<p class='card-text' style='white-space: nowrap; overflow:"
                    " hidden; text-overflow: ellipsis;'>🎤 A tu elección</p>",
                    unsafe_allow_html=True,
                )
              else:
                fecha_corta = evento.get("fecha", "N/A")
                artista = evento.get("artista_orquesta", "N/A")

                st.markdown(
                    f"<p class='card-text'>📅 {fecha_corta}</p>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<p class='card-text' style='white-space: nowrap; overflow:"
                    " hidden; text-overflow: ellipsis;'>🎤 {artista}</p>",
                    unsafe_allow_html=True,
                )

              if es_tu_evento:
                if st.button(
                    "✨ Crear mi Celebración",
                    key=f"btn_tu_evento_{evento_id}_{i_global}",
                    use_container_width=True,
                ):
                  st.session_state.paso_reserva = "crear_celebracion"
                  st.session_state.evento_a_reservar = evento_id
                  st.rerun()
              else:
                if st.button(
                    "Reservar Mesa",
                    key=f"res_grid_{evento_id}_{i_global}",
                    use_container_width=True,
                ):
                  st.session_state.evento_a_reservar = evento_id
                  st.session_state.paso_reserva = "seleccionar_mesa"
                  st.rerun()
          else:
            st.markdown(
                '<div class="columna-fantasma" style="width: 240px; min-height: 490px; visibility: hidden; pointer-events: none;"></div>',
                unsafe_allow_html=True
            )

render_cartelera_cliente = render_cartelera