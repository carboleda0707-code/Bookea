import os
import urllib.parse
import requests
import streamlit as st


def render_control_reservas(api_url, usuario_id=None, local_id=None):
  # ==========================================================
  # ESTILOS CSS REFORZADOS (CENTRADO ABSOLUTO Y DISEÑO MODERNO)
  # ==========================================================
  st.markdown(
      """
    <style>
    /* 1. Centrar títulos, subtítulos y textos generales */
    .stMarkdown, h1, h2, h3, h4, h5, h6 {
        text-align: center !important;
    }

    /* 2. Forzar blanco brillante y negrita en etiquetas de campos */
    .stApp label,
    div[data-testid="stWidgetLabel"] p,
    div[data-testid="stForm"] label p,
    label[data-testid="stWidgetLabel"] p,
    .stMarkdown p strong {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        letter-spacing: 0.3px !important;
        text-shadow: 0px 1px 3px rgba(0,0,0,0.9) !important;
        text-align: center !important;
    }

    /* 3. Limitar ancho de campos de entrada a 320px y centrarlos */
    div[data-testid="stTextInput"], 
    div[data-testid="stTextArea"],
    div[data-testid="stDateInput"],
    div[data-testid="stTimeInput"],
    div[data-testid="stFileUploader"],
    div[data-testid="stSelectbox"] {
        max-width: 320px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }

    /* 4. Centrar formularios y contenedores internos */
    div[data-testid="stForm"] {
        max-width: 480px !important;
        margin: 0 auto !important;
        background-color: #0d0f1a !important;
        border: 1px solid rgba(150, 55, 255, 0.25) !important;
        border-radius: 12px !important;
        padding: 24px !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4) !important;
    }

    /* 5. Centrar expanders / contenedores desplegables generales */
    div[data-testid="stExpander"] {
        max-width: 700px !important;
        margin: 0 auto !important;
        background-color: #0d0f1a !important;
        border: 1px solid rgba(150, 55, 255, 0.25) !important;
        border-radius: 12px !important;
    }

    /* 6. Centrar mensajes de alerta (info, warning, success) para mantener la simetría central */
    div[data-testid="stAlert"] {
        max-width: 700px !important;
        margin: 10px auto !important;
    }

    /* 7. Centrar ABSOLUTAMENTE TODOS los botones (streamlit y personalizados) */
    div[data-testid="stFormSubmitButton"],
    div.stButton {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
        margin: 10px auto !important;
    }

    div[data-testid="stFormSubmitButton"] > button,
    div.stButton > button {
        max-width: 220px !important;
        width: 100% !important;
        padding: 10px 20px !important;
        background: linear-gradient(135deg, #7928CA 0%, #4A00E0 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        box-shadow: 0 4px 12px rgba(121, 40, 202, 0.35) !important;
        transition: all 0.2s ease-in-out !important;
        margin: 0 auto !important;
        display: block !important;
    }

    div[data-testid="stFormSubmitButton"] > button:hover,
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 18px rgba(121, 40, 202, 0.6) !important;
        border-color: #00cfff !important;
    }
    </style>
    """,
      unsafe_allow_html=True,
  )

  # Encabezado principal limpio y con espaciado optimizado
  st.markdown("<br>", unsafe_allow_html=True)
  _, col_title, _ = st.columns([1, 3, 1])
  with col_title:
    st.header("📋 Control y Gestión de Reservas")
    st.write(
        "Valida los datos , el pagos y aprueba las Reservaciones."
    )
  st.markdown("<br>", unsafe_allow_html=True)

  usuario_id_actual = (
      usuario_id
      or st.session_state.get("usuario_id")
      or st.session_state.get("propietario_id")
  )

  # Obtener el local elegido desde parámetro, session_state o selector previo
  local_id_elegido = (
      local_id
      or st.session_state.get("local_id")
      or st.session_state.get("selected_local_id")
      or st.session_state.get("local_id_elegido")
  )

  nombre_local_elegido = "Establecimiento General"
  locales_dict = {}

  try:
    resp_locales = (
        requests.get(
            f"{api_url}/locales/?propietario_id={usuario_id_actual}", timeout=5
        )
        if usuario_id_actual
        else requests.get(f"{api_url}/locales/", timeout=5)
    )
    if resp_locales.status_code == 200 and resp_locales.json():
      locales = resp_locales.json()
      locales_dict = {
          str(l.get("id") or l.get("local_id")): (
              l.get("nombre_local") or l.get("nombre")
          )
          for l in locales
      }

      if not local_id_elegido and locales:
        local_id_elegido = locales[0].get("id") or locales[0].get("local_id")

      for l in locales:
        l_id = str(l.get("id") or l.get("local_id"))
        if l_id == str(local_id_elegido):
          nombre_local_elegido = l.get("nombre_local") or l.get(
              "nombre"
          ) or "Establecimiento General"
          break
  except Exception:
    pass

  if not local_id_elegido:
    st.warning(
        "No se ha detectado un establecimiento activo. Por favor seleccione uno"
        " arriba."
    )
    return

  # 2. Obtener eventos excluyendo la plantilla genérica
  try:
    resp_eventos = requests.get(
        f"{api_url}/locales/{local_id_elegido}/eventos", timeout=5
    )

    if resp_eventos.status_code != 200 or not resp_eventos.json():
      st.warning("Este establecimiento no tiene eventos programados.")
      return

    eventos_raw = resp_eventos.json()
    eventos = []
    for e in eventos_raw:
      estado_ev = str(
          e.get("estado") or e.get("estado_evento") or ""
      ).lower()
      titulo_ev = str(e.get("titulo") or e.get("nombre_evento") or "").lower()

      if estado_ev == "plantilla" or "tu evento" in titulo_ev:
        continue
      eventos.append(e)

    if not eventos:
      st.warning("No hay eventos disponibles para este establecimiento.")
      return

    evento_opciones = {
        f"ID {e.get('id')} - {e.get('titulo') or e.get('nombre_evento')}": e
        for e in eventos
    }
    evento_label = st.selectbox(
        "Selecciona el Evento:",
        list(evento_opciones.keys()),
        key="ctrl_res_select_evento",
    )
    evento_obj_elegido = evento_opciones[evento_label]
    evento_id = evento_obj_elegido.get("id")

  except Exception as e:
    st.error(f"Error al cargar eventos: {e}")
    return

  try:
    eventos_dict = {
        str(e.get("id") or e.get("evento_id")): e for e in eventos
    }

    response = requests.get(f"{api_url}/reservas/", timeout=5)
    if response.status_code != 200:
      response = requests.get(f"{api_url}/reservas/evento/{evento_id}", timeout=5)

    if response.status_code == 200:
      data_res = response.json()
      reservas_raw = data_res if isinstance(data_res, list) else []

      reservas = []
      for r in reservas_raw:
        r_ev_id = str(
            r.get("evento_id") or r.get("id_evento") or r.get("evento", "")
        )
        if (
            not r_ev_id
            or r_ev_id == str(evento_id)
            or str(evento_id) in r_ev_id
        ):
          reservas.append(r)

      if not reservas and reservas_raw:
        for r in reservas_raw:
          r_ev_id = str(
              r.get("evento_id") or r.get("id_evento") or r.get("evento", "")
          )
          if r_ev_id == str(evento_id):
            reservas.append(r)

      if not reservas:
        st.info(
            "No hay reservas registradas para este evento en este"
            " establecimiento."
        )
        return

      st.markdown(f"### Listado de Solicitudes ({len(reservas)} encontradas)")

      for r in reservas:
        res_id = r.get("id") or r.get("reserva_id")
        codigo = r.get("codigo_reserva", "N/A")
        cliente_nombre = r.get("cliente_nombre", "Sin Nombre")
        cliente_correo = r.get("cliente_correo", "Sin Correo")
        cliente_telefono = r.get("cliente_telefono", "Sin Teléfono")

        r_evento_id = r.get("evento_id") or r.get("id_evento")
        r_evento_id_str = str(r_evento_id or evento_id)
        ev_asociado = eventos_dict.get(r_evento_id_str, {})

        nombre_evento = (
            r.get("nombre_evento")
            or ev_asociado.get("nombre_evento")
            or ev_asociado.get("titulo")
        )
        fecha_evento = (
            r.get("fecha_evento")
            or r.get("fecha_hora")
            or ev_asociado.get("fecha_hora")
            or ev_asociado.get("fecha")
        )

        if (
            not fecha_evento
            or "2099-12-31" in str(fecha_evento)
            or not nombre_evento
        ):
          try:
            if r_evento_id:
              resp_ev_single = requests.get(
                  f"{api_url}/eventos/{r_evento_id}", timeout=2
              )
              if resp_ev_single.status_code == 200:
                ev_data = resp_ev_single.json()
                nombre_evento = nombre_evento or ev_data.get(
                    "nombre_evento"
                ) or ev_data.get("titulo")
                fecha_evento = ev_data.get("fecha_hora") or ev_data.get(
                    "fecha"
                )
          except Exception:
            pass

        nombre_evento = (
            nombre_evento
            or evento_obj_elegido.get("titulo")
            or evento_obj_elegido.get("nombre_evento")
            or "Evento General"
        )
        fecha_evento = (
            fecha_evento
            or evento_obj_elegido.get("fecha_hora")
            or evento_obj_elegido.get("fecha")
            or "N/A"
        )

        if "2099-12-31" in str(fecha_evento):
          fecha_evento = (
              evento_obj_elegido.get("fecha_hora")
              or evento_obj_elegido.get("fecha")
              or "N/A"
          )

        if "T" in str(fecha_evento):
          fecha_evento = str(fecha_evento).replace("T", " ")[:16]

        r_local_id = str(r.get("local_id") or local_id_elegido)
        nombre_local_reserva = locales_dict.get(
            r_local_id, nombre_local_elegido
        )

        mesa_id = r.get("mesa_id", "N/A")
        personas = r.get("cantidad_personas", 1)
        estado = r.get("estado_reserva", "pendiente_pago")
        comprobante = r.get("comprobante_pago")
        estado_emoji = "✅" if estado == "confirmada" else "⏳"

        with st.expander(
            f"{estado_emoji} [{codigo}] - Cliente: {cliente_nombre} | Evento:"
            f" {nombre_evento} | Estado: {estado}"
        ):
          c1, c2 = st.columns(2)

          with c1:
            st.markdown(f"#### 👤 Datos del Cliente")
            st.markdown(f"**Nombre:** {cliente_nombre}")
            st.markdown(f"**Correo:** {cliente_correo}")
            st.markdown(f"**Celular:** {cliente_telefono}")
            st.markdown("---")
            st.markdown(f"📅 **Fecha del Evento:** {fecha_evento}")
            st.markdown(f"🎤 **Nombre del Evento:** {nombre_evento}")
            st.markdown(f"📍 **Establecimiento:** {nombre_local_reserva}")
            st.markdown("---")
            st.markdown(f"🪑 **ID Mesa:** {mesa_id}")
            st.markdown(f"👥 **Personas:** {personas}")
            st.markdown(f"📌 **Estado Actual:** `{estado}`")

            if estado == "confirmada":
              st.markdown("#### 🎫 Pases QR Individuales Generados")
              try:
                resp_qr = requests.get(f"{api_url}/reservas/qr/todos", timeout=5)
                if resp_qr.status_code == 200:
                  todos_los_qr = resp_qr.json()
                  pases_reserva = [
                      q
                      for q in todos_los_qr
                      if str(q.get("reserva_id")) == str(res_id)
                  ]

                  if pases_reserva:
                    for idx, pase in enumerate(pases_reserva):
                      codigo_ind = pase.get("codigo_qr")
                      st.markdown(f"**Pase {idx+1}:** `{codigo_ind}`")
                      url_img_qr = (
                          f"{api_url}/static/uploads/qrs/{codigo_ind}.png"
                      )
                      try:
                        st.image(
                            url_img_qr, width=140, caption=f"Pase {idx+1}"
                        )
                      except Exception:
                        st.info(f"Imagen gráfica pendiente para {codigo_ind}")
                  else:
                    st.info(
                        "ℹ️ No se encontraron pases QR asociados en este"
                        " momento."
                    )
              except Exception:
                st.info(
                    "ℹ️ Reserva confirmada (El QR fue enviado al cliente)."
                )

          with c2:
            st.markdown("#### 💳 Comprobante de Pago Subido")
            if comprobante:
              posibles_rutas = [
                  os.path.join(
                      "app", "static", "uploads", "comprobantes", comprobante
                  ),
                  os.path.join("static", "uploads", "comprobantes", comprobante),
                  os.path.join("uploads", comprobante),
                  comprobante,
              ]
              imagen_encontrada = next(
                  (r for r in posibles_rutas if os.path.exists(r)), None
              )
              if imagen_encontrada:
                st.image(
                    imagen_encontrada,
                    caption="Comprobante del cliente",
                    width=280,
                )
              else:
                st.warning(
                    f"Archivo registrado (`{comprobante}`), pero no se halló"
                    " la imagen en el servidor."
                )
            else:
              st.info("⚠️ El cliente aún no ha adjuntado comprobante.")

          st.markdown("---")

          # Campo de mensaje personalizado único para esta reserva
          mensaje_personalizado = st.text_input(
              "✏️ Mensaje personalizado para el correo de aprobación de este"
              " cliente:",
              placeholder=(
                  "Ej: Hola! Te hemos ubicado en una excelente mesa cerca de"
                  " tarima por tu festejo..."
              ),
              key=f"input_msg_{res_id}",
          )

          col_btn1, col_btn2, col_btn3 = st.columns(3)

          with col_btn1:
            if st.button(f"✅ Aprobar y Enviar QR", key=f"aprobar_{res_id}"):
              try:
                payload = {"mensaje_personalizado": mensaje_personalizado}
                res_aprobacion = requests.put(
                    f"{api_url}/reservas/{res_id}/aprobar",
                    json=payload,
                    timeout=15,
                )
                if res_aprobacion.status_code == 200:
                  data_resp = res_aprobacion.json()
                  remitente_usado = data_resp.get(
                      "enviado_desde_correo", "Sistema"
                  )
                  st.success(
                      f"¡Reserva {codigo} aprobada con éxito! Correo enviado"
                      f" desde: {remitente_usado}"
                  )
                  st.balloons()
                  import time

                  time.sleep(2)
                  st.rerun()
                else:
                  st.error("No se pudo aprobar la reserva en el servidor.")
              except Exception as e:
                st.error(f"Error de conexión: {e}")

          with col_btn2:
            if st.button(f"❌ Rechazar", key=f"rechazar_{res_id}"):
              try:
                res_rechazo = requests.put(
                    f"{api_url}/reservas/{res_id}/rechazar", timeout=15
                )
                if res_rechazo.status_code == 200:
                  st.warning(f"La reserva {codigo} fue rechazada con éxito.")
                  import time

                  time.sleep(2)
                  st.rerun()
                else:
                  st.error("No se pudo rechazar la reserva en el servidor.")
              except Exception as e:
                st.error(f"Error de conexión: {e}")

          with col_btn3:
            if estado == "confirmada":
              tel_limpio = cliente_telefono.strip()
              if tel_limpio.startswith("0"):
                tel_limpio = "593" + tel_limpio[1:]
              cant_pers = int(personas)

              mensaje_wapp = (
                  f"¡Hola {cliente_nombre}! Tu reserva para"
                  f" *{nombre_evento}* en {nombre_local_reserva} está"
                  f" confirmada.\n"
              )
              mensaje_wapp += f"📅 Fecha: {fecha_evento}\n"
              mensaje_wapp += f"🪑 Mesa #{mesa_id}\n"
              mensaje_wapp += f"👥 Total asistentes: *{cant_pers} personas*\n\n"
              mensaje_wapp += f"🎫 *Tus Pases QR Individuales:*\n"

              try:
                resp_qr_wapp = requests.get(
                    f"{api_url}/reservas/qr/todos", timeout=3
                )
                if resp_qr_wapp.status_code == 200:
                  pases_wapp = [
                      q
                      for q in resp_qr_wapp.json()
                      if str(q.get("reserva_id")) == str(res_id)
                  ]
                  for idx, p in enumerate(pases_wapp):
                    c_ind = p.get("codigo_qr")
                    url_grafica = f"{api_url}/static/uploads/qrs/{c_ind}.png"
                    mensaje_wapp += f"------------------------\n"
                    mensaje_wapp += f"• *Pase {idx+1}*\n"
                    mensaje_wapp += f"  Código: `{c_ind}`\n"
                    mensaje_wapp += f"  🔗 {url_grafica}\n"
                else:
                  for i in range(cant_pers):
                    mensaje_wapp += f"• Pase {i+1}: `QR-{codigo}-{i+1}`\n"
              except Exception:
                for i in range(cant_pers):
                  mensaje_wapp += f"• Pase {i+1}: `QR-{codigo}-{i+1}`\n"

              mensaje_wapp += (
                  "\n------------------------\n¡Cada invitado puede presionar"
                  " su enlace para ver el QR al llegar! ¡Te esperamos!"
              )

              url_whatsapp = f"https://wa.me/{tel_limpio}?text={urllib.parse.quote(mensaje_wapp)}"
              st.markdown(
                  f'<div style="display: flex; justify-content: center; width:'
                  ' 100%; margin: 10px auto;"><a href="{url_whatsapp}"'
                  ' target="_blank" style="width: 100%; max-width: 220px;"'
                  f'><button style="background-color:#25D366; color:white;'
                  " border:none; padding:10px 18px; border-radius:8px;"
                  " cursor:pointer; font-weight:bold; font-size:14px; width:"
                  ' 100%;">💬 Enviar QRs Wapp</button></a></div>',
                  unsafe_allow_html=True,
              )
            else:
              st.markdown(
                  f'<div style="display: flex; justify-content: center; width:'
                  ' 100%; margin: 10px auto;"><button style="background-color:'
                  "#cccccc; color:#666666; border:none; padding:10px 18px;"
                  " border-radius:8px; cursor:not-allowed; font-weight:bold;"
                  ' font-size:14px; width: 100%; max-width: 220px;" disabled>🔒'
                  " Wapp (Pendiente)</button></div>",
                  unsafe_allow_html=True,
              )
    else:
      st.error(
          f"Error al cargar de la API (Código {response.status_code}):"
          f" {response.text}"
      )
  except Exception as e:
    st.error(f"Error de conexión con el servidor: {e}")