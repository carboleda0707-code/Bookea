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

    if "ultimo_local_id_zonas" not in st.session_state:
        st.session_state["ultimo_local_id_zonas"] = local_id

    if st.session_state["ultimo_local_id_zonas"] != local_id:
        st.session_state["ultimo_local_id_zonas"] = local_id
        st.session_state["menu_gestion"] = "Agenda de Eventos"
        st.rerun()

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
    # 1. MOSTRAR PLANO Y FORMULARIO DE ACTUALIZACIÓN DEL PLANO
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
    # 2. VERIFICAR Y COMPLETAR HASTA 10 ZONAS POR DEFECTO
    # ==========================================================
    try:
        response = requests.get(f"{API_URL}/zonas/", params={"local_id": local_id})
        if response.status_code == 200:
            datos_zonas = response.json()
            zonas = (
                [z for z in datos_zonas if z.get("local_id") == int(local_id)]
                if isinstance(datos_zonas, list)
                else []
            )

            if len(zonas) < 10:
                nombres_existentes = [z.get("nombre_zona", "").lower() for z in zonas]
                for i in range(1, 11):
                    nombre_default = f"Zona {i}"
                    if not any(nombre_default.lower() in n for n in nombres_existentes):
                        payload_def = {
                            "nombre_zona": nombre_default,
                            "descripcion": f"Descripción de la {nombre_default}",
                            "local_id": int(local_id),
                        }
                        try:
                            requests.post(f"{API_URL}/zonas/", json=payload_def)
                        except Exception:
                            pass
                st.rerun()
        else:
            zonas = []
    except Exception:
        zonas = []

    # ==========================================================
    # 3. ZONAS REGISTRADAS Y SELECTOR PARA MODIFICAR UNA ZONA
    # ==========================================================
    col_r1, col_r2, col_r3 = st.columns([1, 3, 1])
    with col_r2:
        st.subheader("📋 Zonas Registradas y Modificación")

    if zonas:
        zonas_tabla = [
            {
                "Nombre de Zona": z.get("nombre_zona"),
                "Descripción": z.get("descripcion"),
                "ID": z.get("id")
            }
            for z in zonas
        ]

        # Tabla con ancho controlado y sin espacios muertos
        st.dataframe(
            zonas_tabla,
            hide_index=True,
            use_container_width=False,
            column_config={
                "Nombre de Zona": st.column_config.TextColumn("Nombre de Zona", width="medium"),
                "Descripción": st.column_config.TextColumn("Descripción", width="large"),
                "ID": st.column_config.NumberColumn("ID", width="small")
            }
        )

        st.markdown("### ✏️ Modificar Zona Individual")
        
        zonas_ordenadas = sorted(zonas, key=lambda x: x.get("id", 0))[:10]
        
        opciones_zonas = {f"ID {z.get('id')}: {z.get('nombre_zona')}": z for z in zonas_ordenadas}
        
        zona_seleccionada_label = st.selectbox(
            "Seleccione la zona a modificar",
            options=list(opciones_zonas.keys()),
            key="select_zona_modificar"
        )
        
        if zona_seleccionada_label:
            z_activa = opciones_zonas[zona_seleccionada_label]
            z_id = z_activa.get("id")
            
            with st.form(f"form_editar_zona_{z_id}"):
                nuevo_nombre = st.text_input(
                    "Nombre de la Zona",
                    value=z_activa.get("nombre_zona", ""),
                    key=f"nombre_z_{z_id}"
                )
                nueva_desc = st.text_input(
                    "Descripción",
                    value=z_activa.get("descripcion", ""),
                    key=f"desc_z_{z_id}"
                )
                
                submit_una = st.form_submit_button("Guardar Cambios de la Zona")

                if submit_una:
                    payload_edit = {
                        "nombre_zona": nuevo_nombre,
                        "descripcion": nueva_desc if nueva_desc else "",
                        "local_id": int(local_id),
                    }
                    try:
                        res_update = requests.put(
                            f"{API_URL}/zonas/{z_id}",
                            json=payload_edit,
                        )
                        if res_update.status_code in [200, 201]:
                            st.success(f"¡Zona ID {z_id} actualizada exitosamente!")
                            st.rerun()
                        else:
                            st.error(f"Error al actualizar la zona: {res_update.text}")
                    except Exception as e:
                        st.error(f"Error de conexión: {e}")
    else:
        st.warning("No se pudieron cargar las zonas.")