import requests
import streamlit as st


def render_asignar_mesas(API_URL):
  # ==========================================================
  # ESTILOS CSS REFORZADOS (CENTRADO TOTAL Y COMPACTO 320PX)
  # ==========================================================
  st.markdown(
      """
    <style>
    /* 1. Centrar títulos, subtítulos y textos generales */
    .stMarkdown, h1, h2, h3, h4, h5, h6 {
        text-align: center !important;
    }

    /* 2. Forzar blanco brillante y negrita en absolutamente todos los títulos de campos */
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

    /* 3. Limitar ancho de TODOS los campos de entrada a 320px y centrarlos */
    div[data-testid="stTextInput"], 
    div[data-testid="stNumberInput"],
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

    /* 5. Centrar tablas / dataframes */
    div[data-testid="stDataFrame"] {
        display: flex !important;
        justify-content: center !important;
        margin: 0 auto !important;
    }

    /* 6. Botones centrados, compactos y modernos */
    div[data-testid="stFormSubmitButton"],
    div.stButton {
        display: flex !important;
        justify-content: center !important;
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

  # Encabezado principal centrado mediante columnas simétricas
  _, col_title, _ = st.columns([1, 3, 1])
  with col_title:
    st.subheader("🛠️ Asignar Mesas y Precios a Eventos")

  # ==========================================================
  # CAPTURAR LOCAL ID DESDE EL ESTABLECIMIENTO ACTIVO GLOBAL
  # ==========================================================
  local_id = (
      st.session_state.get("local_id_actual")
      or st.session_state.get("local_id")
      or st.session_state.get("local_activo_id")
      or 1
  )
  local_id_activo = int(local_id)
  st.session_state["local_id"] = local_id_activo
  params = {"local_id": local_id_activo}

  # ==========================================================
  # OBTENER DATOS DE EVENTOS Y MESAS FILTRADAS POR LOCAL
  # ==========================================================
  try:
    res_eventos = requests.get(
        f"{API_URL}/locales/{local_id_activo}/eventos-propietario"
    )
    eventos = res_eventos.json() if res_eventos.status_code == 200 else []
    if not isinstance(eventos, list):
      eventos = [eventos] if eventos else []
  except Exception:
    eventos = []

  try:
    res_mesas = requests.get(
        f"{API_URL}/precio-evento-mesa/mesas", params=params
    )
    mesas_crudo = res_mesas.json() if res_mesas.status_code == 200 else []
    mesas = (
        mesas_crudo
        if isinstance(mesas_crudo, list)
        else [mesas_crudo]
        if mesas_crudo
        else []
    )
  except Exception:
    mesas = []

  if not eventos:
    st.warning(
        "⚠️ No hay eventos registrados (ni plantilla master ni activos) para"
        " este local. Por favor, crea un evento primero."
    )
    return

  if not mesas:
    st.warning(
        "⚠️ No hay mesas registradas para este local. Por favor, crea mesas"
        " primero."
    )
    return

  opciones_eventos = {}
  for e in eventos:
    nombre_ev = e.get("nombre_evento", "Evento")
    es_master = "tu evento" in nombre_ev.lower() or e.get("es_master", False)
    tipo_etiqueta = (
        "⭐ Plantilla Master ('Tu Evento')"
        if es_master
        else f"📅 Evento [{e.get('estado', 'activo').upper()}]"
    )

    etiqueta = f"{tipo_etiqueta} - {nombre_ev} (ID: {e['id']})"
    opciones_eventos[etiqueta] = e["id"]

  opciones_mesas = {
      f"ID: {m['id']} - Mesa: {m['numero_mesa']} (Capacidad: {m['capacidad']})": m[
          "id"
      ]
      for m in mesas
  }

  tab1, tab2 = st.tabs(["➕ Nueva Asignación", "✏️ Modificar Asignación Existente"])

  with tab1:
    st.info(
        "💡 Asigna mesas a la **Plantilla Master** para habilitar que los"
        " comensales puedan crear su propio evento en este local, o"
        " selecciónalas para eventos programados."
    )
    with st.form("form_asignar"):
      evento_seleccionado = st.selectbox(
          "Selecciona el Evento o Plantilla Master",
          options=list(opciones_eventos.keys()),
          key="new_ev",
      )
      evento_id = opciones_eventos[evento_seleccionado]

      mesa_seleccionada = st.selectbox(
          "Selecciona la Mesa", options=list(opciones_mesas.keys()), key="new_me"
      )
      mesa_id = opciones_mesas[mesa_seleccionada]

      precio = st.number_input(
          "Precio de la Reserva ($)",
          min_value=0.0,
          value=20.0,
          step=5.0,
          key="new_pr",
      )
      consumo_minimo = st.number_input(
          "Consumo Mínimo Obligatorio ($)",
          min_value=0.0,
          value=10.0,
          step=5.0,
          key="new_cm",
      )

      submit = st.form_submit_button("Vincular Mesa al Evento / Plantilla")

      if submit:
        if consumo_minimo < 10.0:
          st.error(
              "⚠️ El consumo mínimo obligatorio debe ser mayor o igual a $10.0."
          )
        else:
          payload = {
              "evento_id": int(evento_id),
              "mesa_id": int(mesa_id),
              "precio": float(precio),
              "consumo_minimo": float(consumo_minimo),
          }
          res = requests.post(f"{API_URL}/precio-evento-mesa/", json=payload)
          if res.status_code == 200:
            st.success("¡Mesa vinculada con éxito!")
            st.rerun()
          else:
            st.error(f"Error al vincular: {res.text}")

  with tab2:
    st.info(
        "💡 Solo puedes modificar asignaciones que aún no tengan reservas"
        " registradas."
    )

    try:
      res_asig = requests.get(f"{API_URL}/precio-evento-mesa/", params=params)
      asignaciones = (
          res_asig.json() if res_asig.status_code == 200 else []
      )
      if not isinstance(asignaciones, list):
        asignaciones = [asignaciones] if asignaciones else []
    except Exception:
      asignaciones = []

    if not asignaciones:
      st.info("No hay asignaciones registradas para modificar en este local.")
    else:
      opciones_asignaciones = {
          f"ID Asignación: {a['id']} | Evento/Master: {a.get('nombre_evento', a['evento_id'])} | Mesa: {a.get('numero_mesa', a['mesa_id'])}": a
          for a in asignaciones
      }

      asig_seleccionada_key = st.selectbox(
          "Selecciona la Asignación a Modificar",
          options=list(opciones_asignaciones.keys()),
      )
      asig_data = opciones_asignaciones[asig_seleccionada_key]

      with st.form("form_modificar"):
        val_precio = float(
            asig_data.get("precio_reserva", asig_data.get("precio", 20.0))
        )
        val_consumo = float(asig_data.get("consumo_minimo", 10.0))

        nuevo_precio = st.number_input(
            "Nuevo Precio de la Reserva ($)",
            min_value=0.0,
            value=val_precio,
            step=5.0,
            key="mod_pr",
        )
        nuevo_consumo = st.number_input(
            "Nuevo Consumo Mínimo Obligatorio ($)",
            min_value=0.0,
            value=val_consumo,
            step=5.0,
            key="mod_cm",
        )

        submit_mod = st.form_submit_button("Actualizar Asignación")

        if submit_mod:
          if nuevo_consumo < 10.0:
            st.error(
                "⚠️ El consumo mínimo obligatorio debe ser mayor o igual a"
                " $10.0."
            )
          else:
            payload_mod = {
                "precio": float(nuevo_precio),
                "consumo_minimo": float(nuevo_consumo),
            }
            res_update = requests.put(
                f"{API_URL}/precio-evento-mesa/{asig_data['id']}",
                json=payload_mod,
            )
            if res_update.status_code == 200:
              st.success("¡Asignación actualizada con éxito!")
              st.rerun()
            else:
              st.error(
                  "⚠️ No se pudo modificar (es posible que ya tenga reservas"
                  f" asociadas): {res_update.text}"
              )

  st.markdown("---")
  with col_title:
    st.subheader("Asignaciones Actuales (Precios y Mesas Vinculadas)")

  if asignaciones:
    st.dataframe(
        asignaciones,
        use_container_width=False,
        column_order=[
            "id",
            "evento_id",
            "nombre_evento",
            "mesa_id",
            "numero_mesa",
            "precio_reserva",
            "consumo_minimo",
            "local_id",
        ],
        column_config={
            "id": st.column_config.NumberColumn("ID", width="small"),
            "evento_id": st.column_config.NumberColumn("Ev. ID", width="small"),
            "nombre_evento": st.column_config.TextColumn(
                "Evento / Master", width="medium"
            ),
            "mesa_id": st.column_config.NumberColumn(
                "Mesa ID", width="small"
            ),
            "numero_mesa": st.column_config.TextColumn(
                "Mesa", width="small"
            ),
            "precio_reserva": st.column_config.NumberColumn(
                "Precio ($)", width="small"
            ),
            "consumo_minimo": st.column_config.NumberColumn(
                "Consumo ($)", width="small"
            ),
            "local_id": st.column_config.NumberColumn(
                "Local ID", width="small"
            ),
        },
    )
  else:
    st.info("No hay mesas asignadas a eventos todavía para este local.")