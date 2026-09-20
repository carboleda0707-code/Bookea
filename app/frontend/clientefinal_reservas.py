from datetime import datetime
import os
import requests
import streamlit as st


def render_mis_reservas(api_url: str, cliente_id: int):

  # ============================================================
  # ESTILOS CSS GLOBALES (FILTRAR RESERVAS Y TÍTULO UNIFICADO)
  # ============================================================
  st.markdown(
      """
    <style>
    /* Centrar la sección principal y limitar el estiramiento visual excesivo */
    .block-container {
        max-width: 900px !important;
        margin: 0 auto !important;
    }

    /* Forzar que el saludo superior y título no se dividan en dos líneas */
    .titulo-unificado {
        white-space: nowrap !important;
        font-size: 1.1rem;
        font-weight: 500;
        margin-bottom: 1rem;
    }

    /* ============================================================
       CONTENEDOR DEL RADIO: TÍTULO ARRIBA Y OPCIONES JUNTAS ABAJO
       ============================================================ */
    div[data-testid="stRadio"] {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        width: 100% !important;
        max-width: 520px !important;
        margin: 0 auto 20px auto !important;
        background-color: #141625 !important;
        border: 1px solid rgba(150, 55, 255, 0.35) !important;
        border-radius: 12px !important;
        padding: 12px 15px !important;
        text-align: center !important;
    }

    div.row-widget.stRadio {
        text-align: center !important;
        display: flex !important;
        justify-content: center !important;
    }
    
    /* Título superior centrado */
    div[data-testid="stRadio"] > label {
        margin-bottom: 6px !important;
    }

    div[data-testid="stRadio"] label div[data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }

    /* Forzar fondo transparente y evitar efectos blancos en hover/click */
    div[data-testid="stRadio"] label, 
    div[data-testid="stRadio"] label:hover, 
    div[data-testid="stRadio"] label:active,
    div[data-testid="stRadio"] label:focus,
    div[data-testid="stRadio"] div[data-baseweb="radio"] div {
        background-color: transparent !important;
    }

    div[data-testid="stRadio"] label:hover div[data-testid="stMarkdownContainer"] p {
        color: #38bdf8 !important;
    }

    /* Opciones en una sola línea horizontal abajo */
    div[data-testid="stRadio"] div[role="radiogroup"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        justify-content: center !important;
        gap: 15px !important;
        align-items: center !important;
        width: 100% !important;
    }

    /* Reducir ligeramente el margen interno de los radio items para que encajen perfectos */
    div[data-testid="stRadio"] div[role="radiogroup"] label {
        padding: 2px 4px !important;
    }

    /* ============================================================
       ELIMINAR EL BLOQUE BLANCO DE LOS EXPANDERS EN STREAMLIT
       ============================================================ */
    div[data-testid="stExpander"] {
        background-color: #121420 !important;
        border: 1px solid rgba(150, 55, 255, 0.25) !important;
        border-radius: 10px !important;
    }

    div[data-testid="stExpander"] details {
        background-color: #121420 !important;
        border-radius: 10px !important;
    }

    div[data-testid="stExpander"] summary {
        background-color: #121420 !important;
        color: #ffffff !important;
        border-radius: 10px !important;
    }

    div[data-testid="stExpander"] summary:hover {
        background-color: #1a1d2e !important;
        color: #38bdf8 !important;
    }
    
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
        background-color: #0f111a !important;
        border-top: 1px solid rgba(150, 55, 255, 0.15) !important;
        border-bottom-left-radius: 10px;
        border-bottom-right-radius: 10px;
    }
    </style>
    """,
      unsafe_allow_html=True,
  )

  st.header("🎟️ Mis Reservas")
  st.write(
      "Aquí verás el estado de tus reservas, tu comprobante de pago y tus"
      " pases QR individuales."
  )

  # Filtro de visualización (Título arriba, opciones en una sola línea abajo)
  filtro_estado = st.radio(
      "Filtrar reservas:",
      ["🟢 Activas ", "📁 Historial "],
      horizontal=True,
      key="filtro_estado_mis_reservas",
  )

  try:
    # Consultamos las reservas filtradas por el ID del cliente logueado
    response = requests.get(
        f"{api_url}/reservas/cliente/{cliente_id}", timeout=5
    )

    if response.status_code == 200:
      reservas = response.json()

      if not reservas:
        st.info("Aún no tienes reservas registradas.")
        return

      ahora = datetime.now()

      # Filtrar las reservas según la selección del usuario y el tiempo transcurrido
      reservas_filtradas = []
      for res in reservas:
        estado_raw = (
            str(res.get("estado_reserva", "pendiente")).strip().lower()
        )

        # Si el cliente ya la ocultó ('bc'), la ignoramos por completo
        if estado_raw == "bc":
          continue

        # Determinar si la fecha del evento ya pasó
        fecha_evento_str = res.get("fecha_hora_evento", "")
        es_pasada = False
        if fecha_evento_str:
          for formato in (
              "%d/%m/%Y %H:%M",
              "%Y-%m-%d %H:%M:%S",
              "%Y-%m-%d %H:%M",
          ):
            try:
              dt_evento = datetime.strptime(fecha_evento_str.strip(), formato)
              if dt_evento < ahora:
                es_pasada = True
              break
            except ValueError:
              continue

        # Clasificación inteligente basada en estado explícito o fecha vencida
        if "Activas" in filtro_estado:
          if (
              estado_raw in ["pendiente", "pendiente_pago", "confirmada"]
              and not es_pasada
          ):
            reservas_filtradas.append(res)
        else:  # Historial / Pasadas
          if (
              estado_raw in ["disfrutada", "completada", "cancelada"]
              or es_pasada
          ):
            reservas_filtradas.append(res)

      if not reservas_filtradas:
        if "Activas" in filtro_estado:
          st.info("No tienes reservas activas en este momento.")
        else:
          st.info("No tienes reservas en tu historial.")
        return

      for res in reservas_filtradas:
        res_id = res.get("id")
        codigo = res.get("codigo_reserva", "N/A")
        evento = res.get("nombre_evento", "Evento")
        fecha_evento = res.get("fecha_hora_evento", "")

        mesa = res.get("numero_mesa", "N/A")
        estado = res.get("estado_reserva", "pendiente")
        personas = res.get("cantidad_personas", 1)
        celebracion = res.get("tipo_celebracion", "Ninguna")
        comprobante = res.get("comprobante_pago")
        mensaje_custom = res.get("mensaje_personalizado")

        estado_emoji = "⏳" if estado == "pendiente_pago" else "✅"

        with st.expander(
            f"{estado_emoji} [{codigo}] - {evento} | Mesa(s): #{mesa} | Estado:"
            f" {estado}"
        ):
          c1, c2 = st.columns(2)

          with c1:
            st.markdown(f"📅 **Fecha del Evento:** {fecha_evento}")
            st.markdown(
                f"📍 **Establecimiento:** {res.get('nombre_local', 'N/A')}"
            )
            st.markdown(f"🪑 **Mesa(s) asignada(s):** #{mesa}")
            st.markdown(f"👥 **Cantidad de Personas:** {personas}")
            st.markdown(f"🎉 **Celebración:** {celebracion}")
            st.markdown(f"📌 **Estado Actual:** `{estado}`")

            if estado == "confirmada":
              st.success(
                  "¡Tu reserva ha sido aprobada por el local! Te esperamos."
              )
            else:
              st.warning(
                  "Tu reserva se encuentra pendiente de verificación de pago."
              )

            if mensaje_custom:
              st.markdown(
                  f"""
                <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 15%, #ffffff 100%); border-left: 5px solid #1976D2; padding: 14px 18px; border-radius: 0 16px 16px 16px; margin: 15px 0; box-shadow: 0 4px 12px rgba(25, 118, 210, 0.15); color: #0d3c61; font-family: sans-serif;">
                    <p style="margin: 0 0 6px 0; font-weight: bold; font-size: 13px; color: #1565C0; display: flex; align-items: center;">
                        💬 Mensaje especial del establecimiento:
                    </p>
                    <p style="margin: 0; font-size: 14px; line-height: 1.5; white-space: pre-line; color: #263238;">
                        {mensaje_custom}
                    </p>
                </div>
                """,
                  unsafe_allow_html=True,
              )

            # Botón para ocultar del historial del cliente (cambia estado a 'BC')
            if "Historial" in filtro_estado:
              st.markdown("---")
              if st.button(
                  "🗑️ Ocultar del historial", key=f"btn_bc_{res_id}"
              ):
                try:
                  resp_patch = requests.patch(
                      f"{api_url}/reservas/{res_id}/estado",
                      json={"estado": "BC"},
                      timeout=5,
                  )
                  if resp_patch.status_code == 200:
                    st.success(
                        "Reserva ocultada correctamente de tu vista."
                    )
                    st.rerun()
                  else:
                    st.error(
                        "No se pudo actualizar el estado de la reserva."
                    )
                except Exception as err:
                  st.error(f"Error de conexión al actualizar: {err}")

          with c2:
            st.markdown("#### 💳 Tu Comprobante de Pago")
            if comprobante:
              posibles_rutas = [
                  os.path.join(
                      "app", "static", "uploads", "comprobantes", comprobante
                  ),
                  os.path.join("static", "uploads", "comprobantes", comprobante),
                  os.path.join("uploads", comprobante),
                  comprobante,
              ]

              imagen_encontrada = None
              for ruta in posibles_rutas:
                if os.path.exists(ruta):
                  imagen_encontrada = ruta
                  break

              if imagen_encontrada:
                st.image(
                    imagen_encontrada,
                    caption="Comprobante enviado",
                    width=250,
                )
              else:
                st.warning(
                    f"El comprobante está registrado (`{comprobante}`), pero no"
                    " se encontró el archivo físico en el servidor."
                )
            else:
              st.info("⚠️ No has adjuntado un comprobante de pago.")

          # --- SECCIÓN DE PASES QR INDIVIDUALES EN VERTICAL ---
          if estado == "confirmada":
            st.markdown("---")
            st.markdown("### 📱 Tus Pases QR Individuales")
            st.write("Presenta tu código o imagen QR al ingresar al evento:")

            try:
              resp_qr = requests.get(f"{api_url}/reservas/qr/todos", timeout=5)
              if resp_qr.status_code == 200:
                todos_los_qr = resp_qr.json()
                pases_reserva = [
                    q for q in todos_los_qr if q.get("reserva_id") == res_id
                ]

                if pases_reserva:
                  for idx, pase in enumerate(pases_reserva):
                    codigo_ind = pase.get("codigo_qr")
                    estado_qr = pase.get("estado_ingreso", "no_utilizado")

                    with st.container():
                      st.markdown(f"**🔹 Pase #{idx+1}**")
                      st.markdown(f"• Código: `{codigo_ind}`")

                      if estado_qr in ["utilizado", "completada"]:
                        st.markdown("🟢 Estado: **Ya utilizado**")
                      else:
                        st.markdown("🟡 Estado: *Disponible*")

                      ruta_img_qr = os.path.join(
                          "app",
                          "static",
                          "uploads",
                          "qrs",
                          f"{codigo_ind}.png",
                      )
                      if os.path.exists(ruta_img_qr):
                        st.image(
                            ruta_img_qr,
                            width=150,
                            caption=f"Pase #{idx+1}",
                        )
                      else:
                        url_img_net = (
                            f"{api_url}/static/uploads/qrs/{codigo_ind}.png"
                        )
                        st.image(
                            url_img_net,
                            width=150,
                            caption=f"Pase #{idx+1}",
                        )

                      st.markdown("", unsafe_allow_html=True)
                else:
                  st.info(
                      "Tus códigos QR individuales se están procesando."
                  )
              else:
                st.info("Revisa tu WhatsApp para ver los pases directos.")
            except Exception:
              st.info("Pases QR disponibles para la entrada.")
    else:
      st.error("No se pudieron cargar tus reservas desde el servidor.")

  except Exception as e:
    st.error(f"Error de conexión al cargar tus reservas: {e}")