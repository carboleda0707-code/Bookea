import requests
import streamlit as st

def render_crear_zonas(API_URL):
    # ==========================================================
    # ESTILOS CSS REFORZADOS (CENTRADO ABSOLUTO DE BOTONES Y ELEMENTOS)
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

        /* 5. Centrar y compactar la tabla / dataframe */
        div[data-testid="stDataFrame"] {
            display: flex !important;
            justify-content: center !important;
            margin: 0 auto !important;
            max-width: 600px !important;
        }
        div[data-testid="stDataFrame"] > div {
            margin: 0 auto !important;
        }

        /* 6. Estilos para la imagen del plano */
        div[data-testid="stImage"] img {
            border-radius: 10px !important;
            border: 1px solid rgba(150, 55, 255, 0.3) !important;
            box-shadow: 0 4px 16px rgba(0,0,0,0.5) !important;
            display: block !important;
            margin-left: auto !important;
            margin-right: auto !important;
        }

        /* 7. Centrar ABSOLUTAMENTE TODOS los botones (formularios y normales) */
        div[data-testid="stFormSubmitButton"],
        div.stButton {
            display: flex !important;
            justify-content: center !important;
            width: 100% !important;
            margin: 15px auto 0 auto !important;
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
    nombre_local_actual = st.session_state.get(
        "nombre_local_actual", f"Local (ID: {local_id})"
    )

    # Detectar cambio de establecimiento para regresar limpiamente a Agenda de Eventos
    if "ultimo_local_id_zonas" not in st.session_state:
        st.session_state["ultimo_local_id_zonas"] = local_id

    if st.session_state["ultimo_local_id_zonas"] != local_id:
        st.session_state["ultimo_local_id_zonas"] = local_id
        st.session_state["menu_gestion"] = "Agenda de Eventos"
        st.rerun()

    # Redirección controlada tras guardar
    if st.session_state.get("redirigir_a_agenda_zonas", False):
        st.session_state["redirigir_a_agenda_zonas"] = False
        st.session_state["menu_gestion"] = "Agenda de Eventos"
        st.rerun()

    # TÍTULO PRINCIPAL
    col_t1, col_t2, col_t3 = st.columns([1, 3, 1])
    with col_t2:
        st.subheader("🗺️ Gestión de Zonas y Distribución")
        st.markdown("🗺️ **Plano o Distribución de Mesas del Local**")

    # ==========================================================
    # 1. MOSTRAR PLANO (CENTRADO) Y FORMULARIO DE ACTUALIZACIÓN
    # ==========================================================
    try:
        res_plano_act = requests.get(f"{API_URL}/zonas/plano/{local_id}")
        if res_plano_act.status_code == 200:
            datos_plano = res_plano_act.json()
            url_plano = datos_plano.get("url")
            if url_plano:
                url_imagen_completa = f"http://localhost:8000{url_plano}"
                cols_img = st.columns([1, 2, 1])
                with cols_img[1]:
                    st.image(
                        url_imagen_completa,
                        use_container_width=True,
                        caption=f"Plano actual de {nombre_local_actual}",
                    )
    except Exception:
        pass

    with st.form("form_plano"):
        foto_distribucion = st.file_uploader(
            "Actualizar o subir imagen del plano (JPG, PNG)",
            type=["jpg", "jpeg", "png"],
        )
        submit_plano = st.form_submit_button("Guardar Plano del Local")

    if submit_plano:
        if foto_distribucion is not None:
            files = {
                "file": (
                    foto_distribucion.name,
                    foto_distribucion.getvalue(),
                    foto_distribucion.type,
                )
            }
            try:
                res_subida = requests.post(
                    f"{API_URL}/zonas/plano/{local_id}", files=files
                )
                if res_subida.status_code in [200, 201]:
                    st.success("¡Plano guardado y actualizado con éxito!")
                    st.rerun()
                else:
                    st.error(f"Error al guardar el plano: {res_subida.text}")
            except Exception as e:
                st.error(f"Error de conexión: {e}")
        else:
            st.warning("Por favor seleccione una imagen antes de guardar.")

    # ==========================================================
    # 2. FORMULARIO DE CREACIÓN DE ZONA (DEBAJO DEL PLANO)
    # ==========================================================
    col_z1, col_z2, col_z3 = st.columns([1, 3, 1])
    with col_z2:
        st.subheader("✨ Crear Nueva Zona")
        
    # Usamos un marcador en session_state para limpiar los inputs al guardar con éxito
    if "form_zona_submitted" not in st.session_state:
        st.session_state["form_zona_submitted"] = False

    with st.form("form_zona", clear_on_submit=True):
        nombre_zona = st.text_input("Nombre de la Zona (ej. Terraza, VIP)")
        descripcion = st.text_area("Descripción (opcional)")
        submit = st.form_submit_button("Guardar Zona")

    if submit:
        payload = {
            "nombre_zona": nombre_zona,
            "descripcion": descripcion if descripcion else "",
            "local_id": int(local_id),
        }
        try:
            res = requests.post(f"{API_URL}/zonas/", json=payload)
            if res.status_code in [200, 201]:
                st.success("¡Zona creada con éxito! Redirigiendo...")
                st.session_state["redirigir_a_agenda_zonas"] = True
                st.rerun()
            else:
                st.error(f"Error al crear: {res.text}")
        except Exception as e:
            st.error(f"Error de conexión: {e}")

    # ==========================================================
    # 3. ZONAS REGISTRADAS, EDICIÓN Y ELIMINACIÓN
    # ==========================================================
    col_r1, col_r2, col_r3 = st.columns([1, 3, 1])
    with col_r2:
        st.subheader("📋 Zonas Registradas")

    try:
        response = requests.get(f"{API_URL}/zonas/", params={"local_id": local_id})
        if response.status_code == 200:
            datos_zonas = response.json()
            zonas = (
                [z for z in datos_zonas if z.get("local_id") == int(local_id)]
                if isinstance(datos_zonas, list)
                else []
            )

            if zonas:
                # Tabla sin la columna local_id y ajustada de manera compacta
                st.dataframe(
                    zonas,
                    hide_index=True,
                    column_order=["nombre_zona", "descripcion", "id"],
                    column_config={
                        "nombre_zona": st.column_config.TextColumn("Nombre de Zona", width="small"),
                        "descripcion": st.column_config.TextColumn("Descripción", width="small"),
                        "id": st.column_config.NumberColumn("ID", width="small")
                    },
                    use_container_width=False
                )

                opciones_zonas = {
                    f"{z['nombre_zona']} (ID: {z['id']})": z for z in zonas
                }

                # SECCIÓN DE MODIFICAR / EDITAR ZONA
                st.markdown("### ✏️ Modificar / Editar Zona")
                zona_a_editar_str = st.selectbox(
                    "Seleccione la zona que desea modificar",
                    list(opciones_zonas.keys()),
                    key="select_editar_zona_id",
                )
                zona_seleccionada = opciones_zonas[zona_a_editar_str]

                with st.form("form_editar_zona"):
                    nuevo_nombre = st.text_input(
                        "Nuevo Nombre de la Zona",
                        value=zona_seleccionada.get("nombre_zona", ""),
                    )
                    nueva_descripcion = st.text_area(
                        "Nueva Descripción",
                        value=zona_seleccionada.get("descripcion", ""),
                    )
                    submit_editar = st.form_submit_button("Guardar Cambios de Zona")

                    if submit_editar:
                        payload_edit = {
                            "nombre_zona": nuevo_nombre,
                            "descripcion": nueva_descripcion if nueva_descripcion else "",
                            "local_id": int(local_id),
                        }
                        try:
                            res_update = requests.put(
                                f"{API_URL}/zonas/{zona_seleccionada.get('id')}",
                                json=payload_edit,
                            )
                            if res_update.status_code in [200, 201]:
                                st.success("¡Zona actualizada exitosamente!")
                                st.rerun()
                            else:
                                st.error(f"Error al actualizar la zona: {res_update.text}")
                        except Exception as e:
                            st.error(f"Error de conexión al actualizar: {e}")

                # SECCIÓN DE ELIMINAR ZONA
                st.markdown("### 🗑️ Eliminar Zona")
                zona_a_borrar_str = st.selectbox(
                    "Seleccione la zona que desea eliminar",
                    list(opciones_zonas.keys()),
                    key="select_borrar_zona_id",
                )

                if st.button("Eliminar Zona Seleccionada", type="primary"):
                    id_zona_eliminar = opciones_zonas[zona_a_borrar_str]["id"]
                    try:
                        res_del = requests.delete(f"{API_URL}/zonas/{id_zona_eliminar}")
                        if res_del.status_code in [200, 204]:
                            st.success(f"Zona ID {id_zona_eliminar} eliminada correctamente.")
                            st.rerun()
                        else:
                            st.error(f"No se pudo eliminar la zona: {res_del.text}")
                    except Exception as e:
                        st.error(f"Error de conexión al eliminar: {e}")
            else:
                st.info("No hay zonas registradas para el establecimiento actual.")
        else:
            st.error("No se pudo cargar el listado de zonas.")
    except Exception as e:
        st.error(f"Error al conectar con el servidor: {e}")