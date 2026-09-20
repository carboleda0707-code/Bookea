import time
import requests
import streamlit as st

# Importación directa del componente de escáner QR
from escaner_qr_component import render_escaner_qr_html


def render_control_puerta(api_url, usuario_id=None, local_id=None):
  # Estilos CSS globales limpios, optimizados y sin duplicados
  st.markdown(
      """
    <style>
    .stMarkdown, h1, h2, h3, h4, h5, h6 {
        text-align: center !important;
    }
    
    h2 {
        margin-bottom: 0px !important;
        padding-bottom: 0px !important;
    }
    
    h3 {
        margin-top: 0px !important;
        margin-bottom: 2px !important;
    }
    
    hr {
        margin: 5px auto !important;
    }

    div.element-container {
        margin-bottom: -8px !important;
    }
    
    iframe {
        margin-bottom: -15px !important;
    }
    
    /* Etiquetas de widgets visibles, en blanco y centradas */
    .stApp label,
    div[data-testid="stWidgetLabel"] p {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        text-shadow: 0px 1px 3px rgba(0,0,0,0.9) !important;
        text-align: center !important;
        display: block !important;
        width: 100% !important;
    }

    /* Contenedor del selectbox centrado y con ancho proporcionado */
    div[data-testid="stSelectbox"] {
        max-width: 460px !important;
        width: 100% !important;
        margin-left: auto !important;
        margin-right: auto !important;
        margin-bottom: 0px !important;
        text-align: center !important;
    }

    /* Expander de la cámara centrado y estilizado */
    div[data-testid="stExpander"] {
        max-width: 500px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 8px !important;
    }
    div[data-testid="stExpander"] summary p {
        text-align: center !important;
        width: 100% !important;
        font-weight: 600 !important;
    }

    div[data-testid="stAlert"] {
        max-width: 700px !important;
        margin: 5px auto !important;
    }
    
    div.stButton {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
        margin: 2px auto !important;
    }
    div.stButton > button {
        max-width: 220px !important;
        width: 100% !important;
    }
    </style>
    """,
      unsafe_allow_html=True,
  )

  # Título compacto
  _, col_title, _ = st.columns([1, 3, 1])
  with col_title:
    st.header("🚪 Control de Puerta QR")
    st.write("Valida los pases QR individuales en tiempo real.")

  usuario_id_actual = (
      usuario_id
      or st.session_state.get("usuario_id")
      or st.session_state.get("propietario_id")
  )

  local_id_elegido = (
      local_id
      or st.session_state.get("local_id")
      or st.session_state.get("selected_local_id")
      or st.session_state.get("local_id_elegido")
  )

  if not local_id_elegido:
    try:
      resp_locales = (
          requests.get(
              f"{api_url}/locales/?propietario_id={usuario_id_actual}",
              timeout=5,
          )
          if usuario_id_actual
          else requests.get(f"{api_url}/locales/", timeout=5)
      )
      if resp_locales.status_code == 200 and resp_locales.json():
        locales = resp_locales.json()
        if locales:
          local_id_elegido = locales[0].get("id") or locales[0].get("local_id")
    except Exception:
      pass

  if not local_id_elegido:
    st.warning("No se ha detectado un establecimiento activo.")
    return

  # Obtención de eventos
  evento_id = None
  nombre_evento_seleccionado = "Evento General"
  fecha_evento_seleccionada = "N/A"
  eventos = []

  urls_intentos = [
      f"{api_url}/eventos/local/{local_id_elegido}",
      f"{api_url}/eventos/?local_id={local_id_elegido}",
      f"{api_url}/reservas/eventos/?local_id={local_id_elegido}",
  ]

  resp_eventos_raw = None
  try:
    for url in urls_intentos:
      resp = requests.get(url, timeout=5)
      if resp.status_code == 200 and resp.json():
        resp_eventos_raw = resp.json()
        break

    if not resp_eventos_raw:
      st.info("Este establecimiento no tiene eventos registrados en la API.")
      return

    eventos = (
        resp_eventos_raw
        if isinstance(resp_eventos_raw, list)
        else [resp_eventos_raw]
    )

    eventos_confirmados = [
        e
        for e in eventos
        if str(e.get("estado", "")).strip().lower() == "confirmado"
    ]

    if not eventos_confirmados:
      st.warning(
          "⚠️ No se encontraron eventos con estado 'confirmado' para este"
          " establecimiento."
      )
      return

    evento_opciones = {
        f"ID {e.get('id') or e.get('evento_id')} - {e.get('nombre_evento') or e.get('titulo')} [{e.get('estado', 's/n')}]": e
        for e in eventos_confirmados
    }

    opciones_keys = list(evento_opciones.keys())
    default_index = 0
    if (
        "puerta_evento_seleccionado" in st.session_state
        and st.session_state.puerta_evento_seleccionado in opciones_keys
    ):
      default_index = opciones_keys.index(
          st.session_state.puerta_evento_seleccionado
      )

    evento_label = st.selectbox(
        "Selecciona el Evento en Puerta:",
        opciones_keys,
        index=default_index,
        key="puerta_select_evento",
    )
    st.session_state.puerta_evento_seleccionado = evento_label

    evento_obj_elegido = evento_opciones[evento_label]
    evento_id = evento_obj_elegido.get("id") or evento_obj_elegido.get(
        "evento_id"
    )
    st.session_state.evento_id_puerta = evento_id

    nombre_evento_seleccionado = evento_obj_elegido.get(
        "nombre_evento"
    ) or evento_obj_elegido.get("titulo", "Evento General")
    fecha_evento_seleccionada = evento_obj_elegido.get(
        "fecha_hora"
    ) or evento_obj_elegido.get("fecha", "N/A")
    if "T" in str(fecha_evento_seleccionada):
      fecha_evento_seleccionada = str(fecha_evento_seleccionada).replace(
          "T", " "
      )[:16]

  except Exception as e:
    st.error(f"Error al cargar eventos: {e}")
    return

  st.markdown("---")

  # Escaneo y Validación QR por URL o Cámara
  query_params = st.query_params
  codigo_input = query_params.get("codigo_scanned", "").strip().upper()

  with st.expander("📷 Escáner con Cámara (Haz clic para abrir)", expanded=False):
    st.markdown(
        "<p style='text-align: center; margin-bottom: 8px; font-weight: 500;"
        " color: #FFFFFF;'>Apunta tu código QR hacia la cámara:</p>",
        unsafe_allow_html=True,
    )
    render_escaner_qr_html()

  if codigo_input:
    try:
      response = requests.get(
          f"{api_url}/reservas/qr/{codigo_input}", timeout=5
      )
      if response.status_code == 200:
        data = response.json()
        qr_id = data.get("ingreso_id")
        cliente = data.get("cliente_nombre", "Desconocido")
        mesa = data.get("mesa_id", "N/A")
        cantidad = data.get("cantidad_personas", 0)
        estado_qr = data.get("estado_ingreso", "no_utilizado")
        hora_checkin = (
            data.get("fecha_ingreso")
            or data.get("fecha_checkin")
            or data.get("updated_at")
        )
        if hora_checkin and "T" in str(hora_checkin):
          hora_checkin = str(hora_checkin).replace("T", " ")[:19]

        st.markdown("---")

        col_1, col_2, col_3 = st.columns([2, 1, 1])
        url_imagen_qr = f"{api_url}/static/uploads/qrs/{codigo_input}.png"

        if estado_qr in ["utilizado", "completada"]:
          st.error("🚨 ¡ALERTA: ESTE PASE QR YA FUE UTILIZADO!")
          with col_1:
            st.markdown(f"👤 **Titular de la Reserva:** {cliente}")
            st.markdown(f"🪑 **Mesa:** #{mesa} ({cantidad} personas)")
            st.markdown(f"🎟️ **Código QR:** `{codigo_input}`")
            if hora_checkin:
              st.markdown(
                  f"⏱️ **Ingresó previamente a las:** `{hora_checkin}`"
              )
            else:
              st.markdown("⏱️ **Ingreso previo registrado.**")
            st.warning("⚠️ Este código no puede volver a ser utilizado.")
          with col_2:
            st.image(url_imagen_qr, caption="Gráfica QR", width=150)
          with col_3:
            st.info("Acceso Bloqueado")
        else:
          with col_1:
            st.success("¡Pase QR Válido y Disponible!")
            st.markdown(f"👤 **Cliente Principal:** {cliente}")
            st.markdown(f"🎤 **Evento:** {nombre_evento_seleccionado}")
            st.markdown(f"📅 **Fecha:** {fecha_evento_seleccionada}")
            st.markdown(f"🪑 **Mesa Asignada:** #{mesa}")
            st.markdown(f"👥 **Cantidad de personas:** {cantidad}")
            st.markdown(f"🎟️ **Código QR:** `{codigo_input}`")
            st.markdown(f"🟢 **Estado del pase:** `{estado_qr}`")
          with col_2:
            st.image(url_imagen_qr, caption="Gráfica QR", width=150)
          with col_3:
            st.write("")
            st.write("")
            if st.button(
                "✅ Registrar Ingreso", type="primary", use_container_width=True
            ):
              res_checkin = requests.put(
                  f"{api_url}/reservas/qr/{qr_id}/checkin", timeout=10
              )
              if res_checkin.status_code == 200:
                st.success("¡Ingreso exitoso!")
                st.balloons()
                st.query_params.clear()
                time.sleep(1)
                st.rerun()
              else:
                st.error("No se pudo registrar el ingreso.")
      else:
        st.error(
            "❌ El código QR escaneado no es válido o no existe en el sistema."
        )
    except Exception as e:
      st.error(f"Error de conexión con la API: {e}")

  st.markdown("---")

  # Listado de Reservas Pendientes de Ingreso
  st.markdown("### 📋 Listado de Reservas Pendientes de Ingreso")

  try:
    eventos_dict = {
        str(e.get("id") or e.get("evento_id")): e for e in eventos
    }

    reservas_validas_ids = set()
    resp_res = None
    for r_url in [
        f"{api_url}/reservas/?evento_id={evento_id}",
        f"{api_url}/reservas/evento/{evento_id}",
        f"{api_url}/reservas/",
    ]:
      resp_res = requests.get(r_url, timeout=5)
      if resp_res.status_code == 200 and resp_res.json():
        break

    if resp_res and resp_res.status_code == 200:
      for r in resp_res.json():
        r_ev = r.get("evento_id") or r.get("id_evento")
        if isinstance(r_ev, dict):
          r_ev = r_ev.get("id") or r_ev.get("evento_id")
        elif not r_ev and isinstance(r.get("evento"), dict):
          r_ev = r.get("evento").get("id") or r.get("evento").get("evento_id")
        elif not r_ev and isinstance(r.get("evento"), (int, str)):
          r_ev = r.get("evento")

        if r_ev is None or str(r_ev) == str(evento_id):
          r_id = r.get("id") or r.get("reserva_id")
          if r_id:
            reservas_validas_ids.add(str(r_id))

    pases_a_mostrar = []
    resp_qr_evento = requests.get(
        f"{api_url}/reservas/qr/evento/{evento_id}", timeout=5
    )
    if resp_qr_evento.status_code == 200 and resp_qr_evento.json():
      pases_a_mostrar = resp_qr_evento.json()
    else:
      resp_all = requests.get(f"{api_url}/reservas/qr/todos", timeout=5)
      if resp_all.status_code == 200:
        for q in resp_all.json():
          q_res_id = str(q.get("reserva_id", ""))
          q_ev_id = q.get("evento_id") or q.get("id_evento")
          if isinstance(q_ev_id, dict):
            q_ev_id = q_ev_id.get("id") or q_ev_id.get("evento_id")
          elif not q_ev_id and isinstance(q.get("evento"), dict):
            q_ev_id = q.get("evento").get("id") or q.get("evento").get(
                "evento_id"
            )
          elif not q_ev_id and isinstance(q.get("evento"), (int, str)):
            q_ev_id = q.get("evento")

          if q_res_id in reservas_validas_ids or (
              q_ev_id is not None and str(q_ev_id) == str(evento_id)
          ):
            pases_a_mostrar.append(q)

    pases_pendientes = [
        p
        for p in pases_a_mostrar
        if p.get("estado_ingreso", "no_utilizado")
        not in ["utilizado", "completada"]
    ]

    if not pases_pendientes:
      st.info(
          "¡Excelente! No hay pases pendientes de ingreso para este evento."
      )
      return

    reservas_dict = {}
    for item in pases_pendientes:
      r_id = item.get("reserva_id", "General")
      if r_id not in reservas_dict:
        reservas_dict[r_id] = {
            "cliente": item.get("cliente_nombre", "Cliente"),
            "mesa": item.get("mesa_id", "N/A"),
            "pases": [],
        }
      reservas_dict[r_id]["pases"].append(item)

    for res_id, info in reservas_dict.items():
      with st.expander(
          f"🎟️ Reserva #{res_id} - Cliente: {info['cliente']} (Mesa:"
          f" #{info['mesa']}) ({len(info['pases'])} pases pendientes)"
      ):
        for idx, pase in enumerate(info["pases"]):
          p_id = pase.get("ingreso_id")
          p_codigo = pase.get("codigo_qr")

          p_hora = (
              pase.get("fecha_ingreso")
              or pase.get("fecha_checkin")
              or pase.get("hora_checkin")
          )
          if p_hora and "T" in str(p_hora):
            p_hora = str(p_hora).replace("T", " ")[:19]

          p_evento_id = str(
              pase.get("evento_id") or pase.get("id_evento") or evento_id
          )
          ev_pase = eventos_dict.get(p_evento_id, evento_obj_elegido)

          nombre_ev_pase = (
              pase.get("nombre_evento")
              or ev_pase.get("nombre_evento")
              or ev_pase.get("titulo")
              or nombre_evento_seleccionado
          )

          fecha_ev_pase = (
              pase.get("fecha_evento")
              or pase.get("fecha_hora")
              or ev_pase.get("fecha_hora")
              or ev_pase.get("fecha")
              or fecha_evento_seleccionada
          )
          if "T" in str(fecha_ev_pase):
            fecha_ev_pase = str(fecha_ev_pase).replace("T", " ")[:16]

          col_v1, col_v2, col_v3 = st.columns([2, 1, 1])

          with col_v1:
            st.markdown(f"**Pase #{idx+1}** ➔ Código: `{p_codigo}`")
            st.markdown(f"🎤 **Evento:** {nombre_ev_pase}")
            st.markdown(f"📅 **Fecha:** {fecha_ev_pase}")
            st.markdown("🔵 Estado: **Reservado (Pendiente de Ingreso)**")

          with col_v2:
            st.image(
                f"{api_url}/static/uploads/qrs/{p_codigo}.png",
                width=90,
                caption=f"QR {idx+1}",
            )

          with col_v3:
            if st.button("Check-in", key=f"btn_puerta_{p_id}"):
              requests.put(f"{api_url}/reservas/qr/{p_id}/checkin", timeout=5)
              st.rerun()

          st.markdown(
              "<hr style='margin: 3px 0; border: 0.3px solid #ddd;'>",
              unsafe_allow_html=True,
          )

  except Exception as e:
    st.info(f"A la espera de registros de puerta... ({e})")