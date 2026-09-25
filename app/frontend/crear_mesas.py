import requests
import streamlit as st


def render_crear_mesas(API_URL):
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
    div[data-testid="stTextArea"],
    div[data-testid="stNumberInput"],
    div[data-testid="stSelectbox"],
    div[data-testid="stFileUploader"] {
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

  # ==========================================================
  # TÍTULO PRINCIPAL
  # ==========================================================
  st.subheader("🛠️ Configuración de Mesas y Distribución")

  # ==========================================================
  # CAPTURAR LOCAL ID DESDE EL ESTABLECIMIENTO ACTIVO GLOBAL
  # ==========================================================
  local_id = (
      st.session_state.get("local_id_actual")
      or st.session_state.get("local_id")
      or st.session_state.get("local_activo_id")
      or 1
  )
  st.session_state["local_id"] = int(local_id)

  # Obtener nombre del local actual
  user_id = st.session_state.get("propietario_id") or st.session_state.get(
      "user_id"
  )
  nombre_local_actual = "Local Principal"
  if user_id:
    try:
      res_locales = requests.get(f"{API_URL}/locales/?propietario_id={user_id}")
      if res_locales.status_code == 200:
        data = res_locales.json()
        locales = data if isinstance(data, list) else [data]
        for loc in locales:
          if int(loc.get("id", loc.get("local_id", 0))) == int(local_id):
            nombre_local_actual = loc.get(
                "nombre_comercial",
                loc.get("nombre_del_local", loc.get("nombre", "Local")),
            )
            break
    except Exception:
      pass

  # ==========================================================
  # SELECCIÓN DE ZONA PERTENECIENTE AL LOCAL ACTUAL
  # ==========================================================
  try:
    response_zonas = requests.get(
        f"{API_URL}/zonas/", params={"local_id": local_id}
    )
    zonas = []
    if response_zonas.status_code == 200:
      datos_z = response_zonas.json()
      zonas = (
          [z for z in datos_z if int(z.get("local_id", 0)) == int(local_id)]
          if isinstance(datos_z, list)
          else []
      )

    if zonas:
      opciones_zonas = {
          f"{z.get('nombre_zona')} (ID: {z.get('id')})": z for z in zonas
      }
      zona_elegida_str = st.selectbox(
          f"📍 Selecciona la Zona en {nombre_local_actual}",
          list(opciones_zonas.keys()),
          key="select_zona_mesa_activo",
      )
      zona_seleccionada = opciones_zonas[zona_elegida_str]
      zona_id = zona_seleccionada.get("id")
      nombre_zona_actual = zona_seleccionada.get("nombre_zona")
    else:
      st.warning(
          f"⚠️ No hay zonas registradas para {nombre_local_actual}. Por favor"
          " cree una zona primero."
      )
      return
  except Exception as e:
    st.error(f"Error al cargar las zonas: {e}")
    return

  # ==========================================================
  # CREACIÓN DE NUEVA MESA (FORMULARIO)
  # ==========================================================
  st.markdown("---")
  st.subheader(f"➕ Crear Nueva Mesa en Zona: {nombre_zona_actual}")

  with st.form("form_crear_mesa"):
    numero_mesa = st.text_input("Número o Nombre de la Mesa (ej. MESA 1, VIP-1)")
    capacidad = st.number_input(
        "Capacidad de Personas", min_value=1, max_value=50, value=4
    )
    forma = st.selectbox(
        "Forma de la Mesa", ["rectangulo", "circulo", "cuadrado"]
    )
    submit_mesa = st.form_submit_button("Guardar Mesa")

  if submit_mesa:
    if not numero_mesa.strip():
      st.warning("El número o nombre de la mesa no puede estar vacío.")
    else:
      payload_mesa = {
          "numero_mesa": numero_mesa.strip(),
          "capacidad": int(capacidad),
          "forma": forma,
          "zona_id": int(zona_id),
          "local_id": int(local_id),
      }
      try:
        # Apuntando al endpoint correcto dentro de precios_mesas
        url_post = f"{API_URL}/precio-evento-mesa/mesas"
        res_m = requests.post(url_post, json=payload_mesa)
        if res_m.status_code in [200, 201]:
          st.success("¡Mesa creada con éxito!")
          st.rerun()
        else:
          st.error(f"Error al crear la mesa (Código {res_m.status_code})")
          st.code(
              f"CHIVATO POST:\nURL: {url_post}\nPayload enviado:"
              f" {payload_mesa}\nRespuesta del servidor: {res_m.text}"
          )
      except Exception as e:
        st.error(f"Error de conexión en POST: {e}")

  # ==========================================================
  # SECCIÓN DE MESAS REGISTRADAS
  # ==========================================================
  st.markdown("---")
  st.subheader(f"📋 Mesas Registradas en Zona → {nombre_zona_actual}")

  try:
    # Apuntando al endpoint de listado con el local_id correspondiente
    url_get = f"{API_URL}/precio-evento-mesa/mesas"
    params_get = {"local_id": local_id}
    res_mesas = requests.get(url_get, params=params_get)

    if res_mesas.status_code == 200:
      datos_mesas = res_mesas.json()
      mesas = (
          [
              m
              for m in datos_mesas
              if int(m.get("zona_id", 0)) == int(zona_id)
          ]
          if isinstance(datos_mesas, list)
          else []
      )

      if mesas:
        mesas_tabla = [
            {
                "ID": m.get("id"),
                "Mesa": m.get("numero_mesa"),
                "Capacidad": m.get("capacidad"),
                "Forma": m.get("forma", "rectangulo"),
            }
            for m in mesas
        ]

        st.dataframe(
            mesas_tabla,
            hide_index=True,
            use_container_width=False,
            column_config={
                "ID": st.column_config.NumberColumn("ID", width="small"),
                "Mesa": st.column_config.TextColumn("Mesa", width="medium"),
                "Capacidad": st.column_config.NumberColumn("Cap.", width="small"),
                "Forma": st.column_config.TextColumn("Forma", width="small"),
            },
        )

        opciones_mesas = {
            f"Mesa: {m.get('numero_mesa')} (Cap: {m.get('capacidad')}) - ID: {m.get('id')}": m
            for m in mesas
        }

        # EDICIÓN DE MESA
        st.markdown("### ✏️ Modificar / Editar Mesa")
        mesa_editar_str = st.selectbox(
            "Seleccione la mesa que desea modificar",
            list(opciones_mesas.keys()),
            key="select_editar_mesa",
        )
        mesa_sel = opciones_mesas[mesa_editar_str]

        with st.form("form_editar_mesa"):
          nuevo_num = st.text_input(
              "Nuevo Número o Nombre", value=mesa_sel.get("numero_mesa", "")
          )
          nueva_cap = st.number_input(
              "Nueva Capacidad",
              min_value=1,
              max_value=50,
              value=int(mesa_sel.get("capacidad", 4)),
          )
          forma_actual = mesa_sel.get("forma", "rectangulo")
          idx_forma = (
              ["rectangulo", "circulo", "cuadrado"].index(forma_actual)
              if forma_actual in ["rectangulo", "circulo", "cuadrado"]
              else 0
          )
          nueva_forma = st.selectbox(
              "Nueva Forma",
              ["rectangulo", "circulo", "cuadrado"],
              index=idx_forma,
          )
          submit_edit = st.form_submit_button("Guardar Cambios de Mesa")

          if submit_edit:
            payload_edit = {
                "numero_mesa": nuevo_num.strip(),
                "capacidad": int(nueva_cap),
                "forma": nueva_forma,
                "zona_id": int(zona_id),
            }
            try:
              res_upd = requests.put(
                  f"{API_URL}/precio-evento-mesa/mesas/{mesa_sel.get('id')}",
                  json=payload_edit,
              )
              if res_upd.status_code in [200, 201]:
                st.success("¡Mesa actualizada con éxito!")
                st.rerun()
              else:
                st.error(f"Error al actualizar: {res_upd.text}")
            except Exception as e:
              st.error(f"Error de conexión: {e}")

        # ELIMINACIÓN DE MESA
        st.markdown("### 🗑️ Eliminar Mesa")
        mesa_borrar_str = st.selectbox(
            "Seleccione la mesa que desea eliminar",
            list(opciones_mesas.keys()),
            key="select_borrar_mesa",
        )

        if st.button("Eliminar Mesa Seleccionada", type="primary"):
          id_mesa_del = opciones_mesas[mesa_borrar_str]["id"]
          try:
            res_del = requests.delete(
                f"{API_URL}/precio-evento-mesa/mesas/{id_mesa_del}"
            )
            if res_del.status_code in [200, 204]:
              st.success(f"Mesa ID {id_mesa_del} eliminada correctamente.")
              st.rerun()
            else:
              st.error(f"No se pudo eliminar: {res_del.text}")
          except Exception as e:
            st.error(f"Error de conexión al eliminar: {e}")
      else:
        st.info(f"No hay mesas registradas en la zona {nombre_zona_actual}.")
    else:
      st.error(
          "⚠️ CHIVATO GET: No se pudo cargar el listado de mesas desde el"
          f" servidor (Código {res_mesas.status_code})."
      )
      st.code(
          f"URL consultada: {url_get}\nParámetros: {params_get}\nCódigo HTTP:"
          f" {res_mesas.status_code}\nRespuesta de la API:\n{res_mesas.text}"
      )
  except Exception as e:
    st.error(f"Error crítico de conexión al listar mesas: {e}")