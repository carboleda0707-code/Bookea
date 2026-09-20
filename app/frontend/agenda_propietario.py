import base64
import calendar
from datetime import date, datetime
import os
import requests
import streamlit as st


def render_agenda_propietario(api_url):
  
  # ============================================================
  # ESTILOS CSS GLOBALES Y SÚPER COMPACTOS PARA MÓVIL
  # ============================================================
  st.markdown("""
  <style>
  .block-container {
      padding-top: 0.4rem !important;
      padding-bottom: 2rem !important;
      max-width: 1200px !important;
  }
  
  /* CONTENEDOR EXTREMADAMENTE COMPACTO PARA EL CALENDARIO */
  .mini-calendar-wrapper {
      max-width: 220px !important;
      margin: 0 auto !important;
  }
  .mini-calendar-wrapper div[data-testid="stVerticalBlockBorderWrapper"],
  .mini-calendar-wrapper div[data-testid="stVerticalBlock"] {
      padding: 4px !important;
  }

  /* REDUCIR AL MÁXIMO LOS SELECTORES DE MES Y AÑO */
  .mini-calendar-wrapper div[data-testid="stSelectbox"],
  .mini-calendar-wrapper div[data-testid="stNumberInput"] {
      max-width: 90px !important;
      margin: 0 auto !important;
  }
  .mini-calendar-wrapper div[data-testid="stSelectbox"] label p,
  .mini-calendar-wrapper div[data-testid="stNumberInput"] label p {
      color: #00cfff !important;
      font-weight: 700 !important;
      font-size: 8px !important;
      margin-bottom: 0px !important;
  }
  .mini-calendar-wrapper div[data-testid="stSelectbox"] [data-baseweb="select"],
  .mini-calendar-wrapper div[data-testid="stNumberInput"] input {
      background-color: #141625 !important;
      border: 1px solid rgba(0, 207, 255, 0.4) !important;
      border-radius: 4px !important;
      min-height: 20px !important;
      height: 22px !important;
      font-size: 9px !important;
      padding: 0px 4px !important;
  }
  .mini-calendar-wrapper div[data-testid="stNumberInput"] button {
      height: 10px !important;
      padding: 0px !important;
  }

  /* FORZAR QUE LAS 7 COLUMNAS TENGAN ANCHO EXACTO Y MÁS JUNTAS */
  .mini-calendar-wrapper div[data-testid="column"] {
      width: 24px !important;
      min-width: 24px !important;
      max-width: 24px !important;
      flex: 0 0 24px !important;
      padding: 0px !important;
  }

  .mini-calendar-wrapper [data-testid="stHorizontalBlock"] {
      display: flex !important;
      justify-content: center !important;
      gap: 1px !important;
  }

  /* BOTONES ULTRA PEQUEÑOS Y CUADRADOS PARA LOS DÍAS DEL CALENDARIO */
  .mini-calendar-wrapper div.stButton button {
      min-height: 22px !important;
      height: 24px !important;
      width: 24px !important;
      padding: 0px !important;
      font-size: 9px !important;
      background-color: #1a1e29 !important;
      border: 1px solid rgba(255, 255, 255, 0.1) !important;
      color: #ffffff !important;
      border-radius: 3px !important;
      margin: 0 auto !important;
      display: block !important;
  }
  .mini-calendar-wrapper div.stButton button:hover {
      background-color: #00cfff !important;
      color: #000000 !important;
      font-weight: bold;
  }

  /* ESTILOS PARA EL SELECTOR DE VISTA / RADIO PESTAÑAS */
  div[data-testid="stRadio"] {
      background: transparent !important;
      padding: 4px;
      border-radius: 12px;
      border: 1px solid rgba(150, 55, 255, 0.3);
      width: fit-content;
      margin: 0 auto !important;
  }
  div[data-testid="stRadio"] > div {
      gap: 6px;
      flex-direction: row !important;
      justify-content: center !important;
  }
  div[data-testid="stRadio"] input,
  div[data-testid="stRadio"] div[role="radiogroup"] label > div:first-child {
      display: none !important;
  }
  div[data-testid="stRadio"] label {
      padding: 6px 12px !important;
      border-radius: 8px !important;
      color: #ffffff !important;
      font-weight: 700 !important;
      font-size: 12px !important;
      background-color: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(255, 255, 255, 0.08);
      cursor: pointer;
  }
  div[data-testid="stRadio"] label p {
      color: #ffffff !important;
  }
  div[data-testid="stRadio"] label:hover {
      background-color: rgba(0, 207, 255, 0.15) !important;
      border-color: rgba(0, 207, 255, 0.4) !important;
      color: #00cfff !important;
  }

  /* TARJETAS DE CARTELERA (AISLADAS) */
  .cartelera-section [data-testid="stHorizontalBlock"] {
      display: flex !important;
      justify-content: center !important;
      gap: 20px !important;
  }
  .cartelera-section div[data-testid="column"] {
      width: 240px !important;
      min-width: 240px !important;
      max-width: 240px !important;
      flex: 0 0 240px !important;
  }
  .cartelera-section div[data-testid="stVerticalBlockBorderWrapper"],
  .cartelera-section div[data-testid="stVerticalBlock"] {
      width: 100% !important;
      max-width: 240px !important;
      padding: 10px !important;
      background-color: #121620 !important;
      border: 1px solid rgba(150, 55, 255, 0.25) !important;
      border-radius: 8px !important;
  }
  .cartelera-section [data-testid="stImage"] img {
      width: 100% !important;
      height: 350px !important;
      object-fit: cover !important;
      border-radius: 6px !important;
  }

  .card-title {
      color: #ffffff !important;
      font-weight: 700 !important;
      font-size: 12px !important;
      margin: 10px 0 4px 0 !important;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      text-align: center;
      width: 100%;
  }
  .card-info {
      color: #b8b9c5 !important;
      font-size: 11px !important;
      margin: 0 0 4px 0 !important;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      text-align: center;
      width: 100%;
  }
  </style>
  """, unsafe_allow_html=True)

  user_id = st.session_state.get("propietario_id") or st.session_state.get("user_id")

  locales_propietario = []
  local_id_actual = st.session_state.get("local_id_actual")
  eventos = []

  try:
    if user_id:
      res_api = requests.get(f"{api_url}/locales/?propietario_id={user_id}")
      if res_api.status_code == 200:
        data_locales = res_api.json()
        locales_propietario = data_locales if isinstance(data_locales, list) else [data_locales]
  except Exception:
    locales_propietario = []

  if locales_propietario:
    opciones_locales = {
        f"{loc.get('nombre', loc.get('nombre_local', loc.get('nombre_comercial', 'Local')))} (ID: {loc.get('id')})": loc.get("id")
        for loc in locales_propietario
    }
    nombres_opciones = list(opciones_locales.keys())
    if local_id_actual not in opciones_locales.values() and nombres_opciones:
      local_id_actual = opciones_locales[nombres_opciones[0]]
      st.session_state["local_id_actual"] = local_id_actual
  else:
    opciones_locales = {}
    nombres_opciones = []

  try:
    if local_id_actual:
      response = requests.get(f"{api_url}/locales/{local_id_actual}/eventos-propietario")
      if response.status_code == 200:
        eventos = response.json()
  except Exception:
    eventos = []

  existe_plantilla = any(
      str(ev.get("estado", "")).strip().lower() == "plantilla" for ev in eventos
  )

  if not existe_plantilla:
    with st.container(border=True):
      st.subheader("⚡ Plantilla General del Local")
      st.write("Haz clic para crear por primera vez el evento maestro **'Tu Evento'**.")
      local_id_plantilla = local_id_actual if local_id_actual else 1

      if st.button("🚀 Crear / Habilitar 'Tu Evento'"):
        data_plantilla = {
            "local_id": int(local_id_plantilla),
            "nombre_evento": "Tu Evento",
            "artista_orquesta": "Plantilla General",
            "estado": "plantilla",
            "genero_musical": "General",
            "incluye_piqueos": False,
            "tipo_ambiente": "Principal",
            "capacidad_total": 50,
            "fecha_hora": "2099-12-31T20:00:00",
            "descripcion": "Plantilla oficial para celebraciones y reservas de comensales.",
        }
        try:
          res_crear = requests.post(f"{api_url}/reservas/eventos/", data=data_plantilla)
          if res_crear.status_code in [200, 201]:
            st.success("✨ ¡Plantilla 'Tu Evento' creada con éxito!")
            st.rerun()
          else:
            st.error(f"Error al crear la plantilla: {res_crear.text}")
        except Exception as e:
          st.error(f"Error de conexión: {e}")
  else:
    st.markdown(
        """
        <div style="display: flex; justify-content: center; width: 100%; margin-bottom: 12px;">
            <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(16, 14, 36, 0.9)); border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 8px; padding: 6px 12px; color: #34d399; font-size: 12px; display: inline-flex; align-items: center; gap: 6px;">
                <span>✅</span> Plantilla <b>'Tu Evento'</b> activa y disponible.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

  # SELECTOR DE VISTA CENTRADO
  col_cent_1, col_cent_2, col_cent_3 = st.columns([1, 2, 1])
  with col_cent_2:
    vista_seleccionada = st.radio(
        "Seleccionar vista",
        ["🖼️ Cartelera de Eventos", "📅 Calendario del Mes"],
        key="selector_vista_propietario",
        label_visibility="collapsed",
        horizontal=True,
    )

  st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

  if vista_seleccionada == "📅 Calendario del Mes":
    # CONTENEDOR EXTREMADAMENTE COMPACTO AL CENTRO
    st.markdown('<div class="mini-calendar-wrapper">', unsafe_allow_html=True)
    with st.container(border=True):
      st.markdown(
          "<p style='text-align:center; font-weight:bold; font-size:10px; color:#00cfff; margin-bottom: 1px;'>📅 Calendario</p>",
          unsafe_allow_html=True,
      )

      col_m1, col_m2 = st.columns(2)
      with col_m1:
        mes_actual = st.selectbox(
            "Mes",
            list(range(1, 13)),
            format_func=lambda x: calendar.month_abbr[x],
            index=date.today().month - 1,
            key="cal_mes_sel",
        )
      with col_m2:
        anio_actual = st.number_input(
            "Año", min_value=2024, max_value=2035, value=date.today().year, key="cal_anio_sel"
        )

      fechas_con_eventos = set()
      for ev in eventos:
        f_raw = ev.get("fecha_hora", "") or ev.get("fecha", "")
        if "T" in f_raw:
          fechas_con_eventos.add(f_raw.split("T")[0])
        elif " " in f_raw:
          fechas_con_eventos.add(f_raw.split(" ")[0])
        elif len(f_raw) >= 10:
          fechas_con_eventos.add(f_raw[:10])

      if "filtro_fecha_calendario" in st.session_state and st.session_state.filtro_fecha_calendario:
        f_activa = st.session_state.filtro_fecha_calendario
        st.markdown(
            f"<p style='text-align:center; font-size:9px; color:#38bdf8; margin: 2px 0;'>Filtro: <b>{f_activa}</b></p>",
            unsafe_allow_html=True,
        )
        if st.button("🔄 Quitar", use_container_width=True, key="btn_reset_filtro_agenda"):
          del st.session_state.filtro_fecha_calendario
          st.rerun()

      cal = calendar.Calendar(firstweekday=0)
      dias_mes = cal.monthdayscalendar(anio_actual, mes_actual)
      dias_semana = ["L", "M", "X", "J", "V", "S", "D"]

      cols_sem = st.columns(7)
      for idx, d_nom in enumerate(dias_semana):
        cols_sem[idx].markdown(
            f"<div style='text-align: center; font-size: 9px; color: #a5b4fc; font-weight: bold; margin-bottom: 1px;'>{d_nom}</div>",
            unsafe_allow_html=True,
        )

      for semana in dias_mes:
        cols_semana = st.columns(7)
        for idx, dia_num in enumerate(semana):
          with cols_semana[idx]:
            if dia_num == 0:
              st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
            else:
              str_dia = f"{anio_actual}-{mes_actual:02d}-{dia_num:02d}"
              tiene_evento = str_dia in fechas_con_eventos
              es_seleccionado = st.session_state.get("filtro_fecha_calendario") == str_dia

              if es_seleccionado:
                label_btn = f"[{dia_num}]"
              elif tiene_evento:
                label_btn = f"{dia_num}*"
              else:
                label_btn = str(dia_num)

              if st.button(label_btn, key=f"btn_dia_mini_{str_dia}"):
                if es_seleccionado:
                  del st.session_state.filtro_fecha_calendario
                else:
                  st.session_state.filtro_fecha_calendario = str_dia
                st.rerun()

      st.markdown(
          "<p style='font-size: 8px; color: #34d399; margin-top: 2px; text-align: center;'>* Días con eventos.</p>",
          unsafe_allow_html=True,
      )
    st.markdown('</div>', unsafe_allow_html=True)

  else:
    plantilla_tu_evento = [
        ev for ev in eventos if ev.get("nombre_evento", "").strip().lower() == "tu evento"
    ]
    otros_eventos = [
        ev for ev in eventos if ev.get("nombre_evento", "").strip().lower() != "tu evento"
    ]
    otros_eventos = sorted(otros_eventos, key=lambda x: x.get("id", 0), reverse=True)

    if "filtro_fecha_calendario" in st.session_state and st.session_state.filtro_fecha_calendario:
      f_sel = st.session_state.filtro_fecha_calendario
      otros_eventos_filtrados = [
          ev for ev in otros_eventos if (ev.get("fecha_hora", "") or "").startswith(f_sel)
      ]
      st.markdown(
          f"<p style='text-align: center; font-size: 12px; color: #38bdf8;'>Cartelera filtrada para la fecha: <b>{f_sel}</b> (La plantilla 'Tu Evento' se mantiene visible).</p>",
          unsafe_allow_html=True,
      )
      eventos_a_mostrar = plantilla_tu_evento + otros_eventos_filtrados
    else:
      eventos_a_mostrar = plantilla_tu_evento + otros_eventos

    # ENVOLTORIO CON CLASE PARA LA CARTELERA
    st.markdown('<div class="cartelera-section">', unsafe_allow_html=True)
    if eventos_a_mostrar:
      num_evs = len(eventos_a_mostrar)
      if num_evs == 1:
        MAX_COLS = 3
        elementos_render = [None, eventos_a_mostrar[0], None]
      elif num_evs == 2:
        MAX_COLS = 4
        elementos_render = [None, eventos_a_mostrar[0], eventos_a_mostrar[1], None]
      elif num_evs == 3:
        MAX_COLS = 3
        elementos_render = eventos_a_mostrar
      else:
        MAX_COLS = 4
        elementos_render = eventos_a_mostrar

      for i_lote in range(0, len(elementos_render), MAX_COLS):
        lote_actual = elementos_render[i_lote:i_lote + MAX_COLS]
        cols = st.columns(MAX_COLS)

        for j in range(MAX_COLS):
          with cols[j]:
            if j < len(lote_actual) and lote_actual[j] is not None:
              evento = lote_actual[j]
              evento_id = evento.get("id")
              i_global = i_lote + j
              nombre_ev = evento.get("nombre_evento", "Sin nombre")

              with st.container(border=True):
                nombre_imagen = evento.get("imagen")
                imagen_encontrada = None

                if nombre_imagen:
                  posibles_rutas = [
                      os.path.join("app", "static", "uploads", nombre_imagen),
                      os.path.join("static", "uploads", nombre_imagen),
                      os.path.join("uploads", nombre_imagen),
                      nombre_imagen,
                  ]
                  for ruta in posibles_rutas:
                    if os.path.exists(ruta):
                      imagen_encontrada = ruta
                      break

                if imagen_encontrada:
                  st.image(imagen_encontrada, use_container_width=True)
                else:
                  st.markdown(
                      """
                      <div style="background: #141625; padding: 12px 4px; text-align: center; border-radius: 6px; border: 1px dashed rgba(255,255,255,0.15); height: 350px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                          <span style="font-size: 18px;">🎧</span><br>
                          <b style="color: #ffffff; font-size: 10px;">Tu Evento</b><br>
                          <span style="font-size: 9px; color: #d6d5df;">Sin póster</span>
                      </div>
                      """,
                      unsafe_allow_html=True,
                  )

                st.markdown(f"<p class='card-title' title='{nombre_ev}'>{nombre_ev}</p>", unsafe_allow_html=True)

                fecha_raw = evento.get("fecha_hora", "N/A")
                fecha_corta = fecha_raw.split("T")[0] if "T" in fecha_raw else fecha_raw
                artista = evento.get("artista_orquesta", "N/A")

                st.markdown(f"<p class='card-info'>🆔 <b>ID:</b> {evento_id}</p>", unsafe_allow_html=True)
                st.markdown(f"<p class='card-info'>📅 {fecha_corta}</p>", unsafe_allow_html=True)
                st.markdown(f"<p class='card-info' title='{artista}'>🎤 {artista}</p>", unsafe_allow_html=True)

                estado_ev = evento.get("estado", "aprobado")
                if estado_ev == "pendiente":
                  st.markdown("<p style='color: #fbbf24; font-size: 10px; margin: 0 0 4px 0; text-align: center;'>⏳ Pendiente</p>", unsafe_allow_html=True)
                  if st.button("✅ Aprobar", key=f"aprobar_{evento_id}_{i_global}"):
                    try:
                      res_aprob = requests.put(
                          f"{api_url}/reservas/eventos/{evento_id}/estado", json={"estado": "aprobado"}
                      )
                      if res_aprob.status_code in [200, 201]:
                        st.success("¡Aprobado!")
                        st.rerun()
                      else:
                        st.error(f"Error: {res_aprob.text}")
                    except Exception as ex:
                      st.error(f"Error: {ex}")

                if st.button("✏️ Editar", key=f"edit_{evento_id}_{i_global}"):
                  st.session_state.editando_evento_id = evento_id
                  st.rerun()

                if st.button("🗑️ Borrar", key=f"del_{evento_id}_{i_global}"):
                  try:
                    del_response = requests.delete(f"{api_url}/reservas/eventos/{evento_id}")
                    if del_response.status_code == 404:
                      del_response = requests.delete(f"{api_url}/eventos/{evento_id}")

                    if del_response.status_code in [200, 204]:
                      st.success("¡Eliminado!")
                      st.rerun()
                    else:
                      st.error("No se pudo eliminar.")
                  except Exception as ex:
                    st.error(f"Error: {ex}")
            else:
              st.markdown(
                  '<div style="width: 240px; min-height: 480px; visibility: hidden; pointer-events: none;"></div>',
                  unsafe_allow_html=True
              )
    else:
      st.info("No hay eventos programados para esta fecha.")
    st.markdown('</div>', unsafe_allow_html=True)

  if "editando_evento_id" in st.session_state and st.session_state.editando_evento_id:
    id_a_editar = st.session_state.editando_evento_id
    evento_actual = next((ev for ev in eventos if int(ev.get("id", 0)) == int(id_a_editar)), None)

    if not evento_actual:
      try:
        res_all = requests.get(f"{api_url}/reservas/eventos/")
        if res_all.status_code == 200:
          todos_evs = res_all.json()
          evento_actual = next((ev for ev in todos_evs if int(ev.get("id", 0)) == int(id_a_editar)), None)
      except Exception:
        pass

    st.markdown("---")
    st.info(f"✏️ Estás editando el Evento ID: {id_a_editar}")

    if evento_actual:
      with st.form(f"form_editar_evento_{id_a_editar}"):
        n_nombre = st.text_input("Nombre del Evento", value=evento_actual.get("nombre_evento", ""))
        n_artista = st.text_input("Artista u Orquesta", value=evento_actual.get("artista_orquesta", ""))
        n_desc = st.text_area("Descripción", value=evento_actual.get("descripcion", ""))

        f_raw = evento_actual.get("fecha_hora", "")
        try:
          dt_parsed = datetime.fromisoformat(f_raw.replace("Z", ""))
          d_val = dt_parsed.date()
          t_val = dt_parsed.time()
        except Exception:
          d_val = datetime.today().date()
          t_val = datetime.now().time()

        col_f, col_h = st.columns(2)
        with col_f:
          min_d = datetime(2024, 1, 1).date()
          max_d = datetime(2100, 12, 31).date()
          if d_val > max_d:
            d_val = min_d
          n_fecha = st.date_input("Nueva Fecha / Vigencia Plantilla", value=d_val, min_value=min_d, max_value=max_d)

        with col_h:
          n_hora = st.time_input("Nueva Hora", value=t_val)

        n_imagen = st.file_uploader("Actualizar Imagen o Flyer (Opcional)", type=["jpg", "jpeg", "png"])
        btn_guardar = st.form_submit_button("💾 Guardar Cambios")

        if btn_guardar:
          fecha_hora_str = f"{n_fecha}T{n_hora.strftime('%H:%M:%S')}"
          data_act = {
              "nombre_evento": n_nombre,
              "artista_orquesta": n_artista,
              "fecha_hora": fecha_hora_str,
              "descripcion": n_desc,
          }
          files_act = (
              {"file": (n_imagen.name, n_imagen.getvalue(), n_imagen.type)}
              if n_imagen
              else None
          )

          try:
            resp_upd = requests.put(
                f"{api_url}/reservas/eventos/{id_a_editar}", data=data_act, files=files_act
            )
            if resp_upd.status_code in [200, 201]:
              st.success("¡Evento actualizado con éxito!")
              del st.session_state.editando_evento_id
              st.rerun()
            else:
              st.error(f"Error al actualizar: {resp_upd.text}")
          except Exception as e:
            st.error(f"Error de conexión: {e}")
    else:
      st.error(f"No se pudo cargar la información del evento ID {id_a_editar}.")

    if st.button("❌ Cancelar Edición"):
      del st.session_state.editando_evento_id
      st.rerun()