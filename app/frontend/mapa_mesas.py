import requests
import streamlit as st


def render_mapa_mesas(api_url: str, usuario_id=None, local_id=None):
  # Estilos CSS para centrar los elementos de la interfaz
  st.markdown(
      """
        <style>
        .centered-title {
            text-align: center;
        }
        .centered-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .stSelectbox {
            max-width: 400px;
            margin: 0 auto;
        }
        </style>
    """,
      unsafe_allow_html=True,
  )

  st.markdown(
      "<h2 class='centered-title'>📊 Mapa de Mesas por Zonas</h2>",
      unsafe_allow_html=True,
  )

  # 1. Heredar de forma limpia el establecimiento activo recibido por parámetro o sesión
  local_id_elegido = (
      local_id
      or st.session_state.get("local_id")
      or st.session_state.get("selected_local_id")
      or st.session_state.get("local_id_elegido")
  )

  if not local_id_elegido:
    st.warning("⚠️ No se ha detectado un establecimiento activo en la sesión.")
    return

  usuario_id_actual = (
      usuario_id
      or st.session_state.get("usuario_id")
      or st.session_state.get("propietario_id")
  )

  # 2. Obtener eventos filtrados por el establecimiento activo y estado confirmado
  try:
    if local_id_elegido:
      url_evs = f"{api_url}/reservas/eventos/?local_id={local_id_elegido}"
    elif usuario_id_actual:
      url_evs = f"{api_url}/reservas/eventos/?usuario_id={usuario_id_actual}"
    else:
      url_evs = f"{api_url}/reservas/eventos/"

    resp_eventos = requests.get(url_evs, timeout=5)
    if resp_eventos.status_code != 200 or not resp_eventos.json():
      st.warning("No hay eventos creados para este establecimiento.")
      return

    eventos = resp_eventos.json()

    # Filtrar exclusivamente los eventos que estén en estado "confirmado"
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
        f"ID {e['id']} - {e['nombre_evento']}": e["id"]
        for e in eventos_confirmados
    }

    opciones_keys = list(evento_opciones.keys())
    default_index = 0
    if (
        "mapa_evento_seleccionado" in st.session_state
        and st.session_state.mapa_evento_seleccionado in opciones_keys
    ):
      default_index = opciones_keys.index(
          st.session_state.mapa_evento_seleccionado
      )

    nombre_elegido = st.selectbox(
        "Selecciona el evento para ver su mapa",
        opciones_keys,
        index=default_index,
        key="mapa_select_evento",
    )
    st.session_state.mapa_evento_seleccionado = nombre_elegido
    evento_id = evento_opciones[nombre_elegido]

    nombre_evento_actual = (
        nombre_elegido.split(" - ", 1)[1] if " - " in nombre_elegido else "Evento"
    )

    # 3. Obtener zonas
    resp_zonas = requests.get(f"{api_url}/zonas/")
    zonas_dict = {}
    if resp_zonas.status_code == 200:
      zonas_dict = {z["id"]: z["nombre_zona"] for z in resp_zonas.json()}

    # 4. Obtener la lista general de mesas
    resp_todas_mesas = requests.get(f"{api_url}/reservas/mesas")
    info_mesas_global = {}
    if resp_todas_mesas.status_code == 200:
      for m in resp_todas_mesas.json():
        info_mesas_global[m["id"]] = {
            "zona_id": m.get("zona_id", 1),
            "capacidad": m.get("capacidad", 4),
            "nombre_mesa": m.get("nombre_mesa")
            or m.get("numero_mesa")
            or f"#{m.get('id')}",
        }

    # Obtener reservas activas de este evento
    reservas_por_mesa = {}
    try:
      resp_reservas = requests.get(f"{api_url}/reservas/", timeout=5)
      if resp_reservas.status_code == 200:
        for r in resp_reservas.json():
          r_evento_id = r.get("evento_id") or r.get("id_evento")
          estado_res = r.get("estado_reserva", "")

          if str(r_evento_id) == str(evento_id) and estado_res != "cancelada":
            codigo_res = r.get("codigo_reserva", "N/A")
            nom_ev = r.get("nombre_evento", nombre_evento_actual)
            mesa_id_raw = r.get("mesa_id") or r.get("numero_mesa")
            if mesa_id_raw:
              for m_item in str(mesa_id_raw).split(","):
                m_clean = m_item.strip()
                if m_clean:
                  reservas_por_mesa[m_clean] = {
                      "codigo_reserva": codigo_res,
                      "nombre_evento": nom_ev,
                  }
                  if m_clean.isdigit():
                    reservas_por_mesa[int(m_clean)] = {
                        "codigo_reserva": codigo_res,
                        "nombre_evento": nom_ev,
                    }
    except Exception:
      pass

    # Obtener el estado de todos los pases QR
    asistencia_mesas = {}
    try:
      resp_qr_todos = requests.get(f"{api_url}/reservas/qr/todos", timeout=5)
      if resp_qr_todos.status_code == 200:
        for pase in resp_qr_todos.json():
          m_id_pase = pase.get("mesa_id")
          estado_ingreso = pase.get("estado_ingreso", "no_utilizado")
          es_presente = estado_ingreso in ["utilizado", "completada"]

          if m_id_pase is not None:
            clave = str(m_id_pase).strip()
            if clave:
              if clave not in asistencia_mesas:
                asistencia_mesas[clave] = {"total": 0, "presentes": 0}

              asistencia_mesas[clave]["total"] += 1
              if es_presente:
                asistencia_mesas[clave]["presentes"] += 1
    except Exception:
      pass

    # 5. Consultar disponibilidad de mesas del evento
    resp_mesas = requests.get(
        f"{api_url}/reservas/mesas-disponibles/{evento_id}"
    )
    if resp_mesas.status_code == 200:
      mesas = resp_mesas.json()

      if not mesas:
        st.info("Este evento aún no tiene mesas asignadas.")
        return

      mesas_por_zona = {}
      for mesa in mesas:
        mesa_id = mesa.get("mesa_id")
        datos_globales = info_mesas_global.get(
            mesa_id,
            {
                "zona_id": 1,
                "capacidad": 4,
                "nombre_mesa": mesa.get("numero_mesa"),
            },
        )

        zona_id = datos_globales["zona_id"]
        nombre_zona = zonas_dict.get(zona_id, f"Zona {zona_id}")
        if nombre_zona not in mesas_por_zona:
          mesas_por_zona[nombre_zona] = []
        mesas_por_zona[nombre_zona].append(mesa)

      # Selector de Zonas centrada
      lista_nombres_zonas = list(mesas_por_zona.keys())
      zona_seleccionada = st.selectbox(
          "Selecciona la Zona a visualizar",
          lista_nombres_zonas,
          key="select_zona_mapa",
      )

      st.markdown("<br>", unsafe_allow_html=True)

      # Leyenda centrada
      st.markdown(
          "<div style='text-align: center;'>"
          "<b>Leyenda del Mapa:</b> "
          "<span style='color:#28a745; font-weight:bold;'>■</span> Libre"
          " &nbsp;|&nbsp; "
          "<span style='color:#1C83E1; font-weight:bold;'>■</span> Reservado"
          " &nbsp;|&nbsp; "
          "<span style='color:#ff4b4b; font-weight:bold;'>■</span> Asistencia"
          " (Check-in)"
          "</div>",
          unsafe_allow_html=True,
      )
      st.markdown("<br>", unsafe_allow_html=True)

      # Paleta de colores automáticos por zona
      colores_automaticos = [
          "#FF4B4B",
          "#1C83E1",
          "#00C0F2",
          "#AB47BC",
          "#29B6F6",
          "#FFA726",
      ]

      # Renderizar únicamente la zona seleccionada
      if zona_seleccionada in mesas_por_zona:
        idx_zona = lista_nombres_zonas.index(zona_seleccionada)
        color_actual_zona = colores_automaticos[
            idx_zona % len(colores_automaticos)
        ]
        lista_mesas = mesas_por_zona[zona_seleccionada]

        st.markdown(
            f"<h3 style='color: {color_actual_zona}; text-align:"
            f" center;'>📍 {zona_seleccionada}</h3>",
            unsafe_allow_html=True,
        )

        # Mostrar mesas centradas en filas de 6 columnas
        cols = st.columns(6)
        for i, mesa in enumerate(lista_mesas):
          with cols[i % 6]:
            m_id = mesa.get("mesa_id")
            numero_mesa = mesa.get("numero_mesa")

            datos_mesa = info_mesas_global.get(m_id, {})
            capacidad_base = datos_mesa.get(
                "capacidad", mesa.get("capacidad", 4)
            )
            nombre_etiqueta_mesa = datos_mesa.get(
                "nombre_mesa", f"Mesa #{numero_mesa}"
            )

            info_asist = (
                asistencia_mesas.get(str(m_id))
                or asistencia_mesas.get(str(numero_mesa))
                or asistencia_mesas.get(str(nombre_etiqueta_mesa))
                or asistencia_mesas.get(f"Mesa #{numero_mesa}")
                or asistencia_mesas.get(f"Mesa #{m_id}")
                or {"total": 0, "presentes": 0}
            )
            presentes = info_asist["presentes"]
            total_qr_mesa = info_asist["total"]

            info_reserva_mesa = (
                reservas_por_mesa.get(str(nombre_etiqueta_mesa))
                or reservas_por_mesa.get(str(numero_mesa))
                or reservas_por_mesa.get(m_id)
                or reservas_por_mesa.get(f"Mesa #{numero_mesa}")
            )

            total_puntos = max(capacidad_base, total_qr_mesa, presentes)

            puntos_html = ""
            for asiento_idx in range(total_puntos):
              if asiento_idx < presentes:
                color_punto = "#ff4b4b"
              elif asiento_idx < total_qr_mesa or info_reserva_mesa:
                color_punto = "#1C83E1"
              else:
                color_punto = "#28a745"

              puntos_html += (
                  f'<span style="display:inline-block; width:9px; height:9px;'
                  f' background-color:{color_punto}; border-radius:50%;'
                  f' margin:2px;" title="Asiento {asiento_idx+1}"></span>'
              )

            if info_reserva_mesa:
              ev_nombre = info_reserva_mesa.get(
                  "nombre_evento", nombre_evento_actual
              )
              cod_res = info_reserva_mesa.get("codigo_reserva", "")
              texto_estado = (
                  f"<b>{ev_nombre}</b><br><span"
                  f" style='color:#1C83E1;'>{cod_res}</span>"
              )
            elif presentes > 0:
              texto_estado = f"{presentes}/{capacidad_base} en sitio"
            elif total_qr_mesa > 0:
              texto_estado = f"{total_qr_mesa}/{capacidad_base} Reservado"
            else:
              texto_estado = "Libre"

            st.markdown(
                f"""
                        <div style="border: 2px solid {color_actual_zona}; padding: 8px; border-radius: 8px; text-align: center; background: #ffffff; margin-bottom: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);" title="{nombre_etiqueta_mesa}">
                            <div style="font-weight: bold; color: #333; font-size: 11px; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{nombre_etiqueta_mesa}</div>
                            <div style="margin-bottom: 4px; line-height: 1.1; min-height: 14px;">{puntos_html}</div>
                            <div style="font-size: 9px; color: #444; font-weight: 500; line-height: 1.2; word-break: break-word;">{texto_estado}</div>
                        </div>
                    """,
                unsafe_allow_html=True,
            )
        st.markdown("---")

    else:
      st.error("Error al cargar las mesas del evento.")
  except Exception as e:
    st.error(f"Error de conexión: {e}")