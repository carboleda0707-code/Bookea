import streamlit as st
import requests

def render_mantenimiento(api_url):
    
    # ============================================================
    # ESTILOS CSS OPTIMIZADOS (CAMPOS COMPACTOS Y TÍTULOS VISIBLES)
    # ============================================================
    st.markdown("""
    
    """, unsafe_allow_html=True)

    st.markdown("### 🛠️ Gestión y Mantenimiento de Locales")
    st.write("Modifica la información de tu establecimiento o registra nuevas sucursales para revisión del sistema.")

    # ============================================================
    # RECUPERAR IDENTIFICADORES DINÁMICOS DE LA SESIÓN O URL
    # ============================================================
    query_params = st.query_params
    local_id_url = query_params.get("local_id")
    
    usuario_id = st.session_state.get("usuario_id") or st.session_state.get("user_id") or st.session_state.get("propietario_id")
    empresa_id = st.session_state.get("empresa_id") or st.session_state.get("id_empresa")
    local_id = st.session_state.get("local_id") or local_id_url

    # ============================================================
    # CONSULTAR LOS DATOS REALES DEL LOCAL DESDE LA API
    # ============================================================
    local_data = None
    
    if local_id:
        try:
            resp = requests.get(f"{api_url}/locales/{local_id}", timeout=4)
            if resp.status_code == 200:
                local_data = resp.json()
        except Exception:
            pass

    if not local_data and empresa_id:
        try:
            resp = requests.get(f"{api_url}/locales/empresa/{empresa_id}", timeout=4)
            if resp.status_code == 200:
                lista = resp.json()
                if lista:
                    local_data = lista[0]
        except Exception:
            pass

    if not local_data and usuario_id:
        try:
            resp = requests.get(f"{api_url}/locales/?propietario_id={usuario_id}", timeout=4)
            if resp.status_code == 200:
                lista = resp.json()
                if lista:
                    local_data = lista[0]
        except Exception:
            pass

    # ============================================================
    # CREACIÓN DE PESTAÑAS (EDITAR ACTUAL VS. AÑADIR NUEVO)
    # ============================================================
    tab_editar, tab_nuevo = st.tabs(["📝 Editar Local Actual", "➕ Registrar Nuevo Local"])

    # --- PESTAÑA 1: EDITAR LOCAL ACTUAL ---
    with tab_editar:
        st.markdown("---")
        st.subheader("📍 Información del Local Actual")

        if local_data:
            actual_id = local_data.get("id")
            
            with st.form("form_editar_local_real"):
                col1, col2 = st.columns(2)
                with col1:
                    # Campo de nombre comercial actualizado
                    nombre = st.text_input("Nombre Comercial", value=local_data.get("nombre", local_data.get("nombre_local", "")))
                    ruc = st.text_input("RUC / NIT", value=local_data.get("ruc_nit", ""))
                    direccion = st.text_input("Dirección Exacta", value=local_data.get("direccion", ""))
                    ciudad = st.text_input("Ciudad", value=local_data.get("ciudad", ""))
                with col2:
                    pais = st.text_input("País", value=local_data.get("pais", "Ecuador"))
                    tipo = st.text_input("Tipo de Establecimiento", value=local_data.get("tipo_establecimiento", ""))
                    email = st.text_input("Correo Electrónico de Contacto", value=local_data.get("email_contacto", ""))
                    telefono = st.text_input("Teléfono / WhatsApp", value=local_data.get("telefono_contacto", local_data.get("telefono", "")))
                
                # Selector para actualizar la fotografía simultáneamente
                st.markdown("---")
                foto_local_subida = st.file_uploader("Actualizar Fotografía del Local", type=["jpg", "jpeg", "png"], key="edit_foto_local")
                    
                submit_cambios = st.form_submit_button("💾 Guardar Cambios")
                
                if submit_cambios:
                    # 1. Procesar la imagen si se subió una nueva
                    ruta_imagen = local_data.get("imagen")
                    if foto_local_subida is not None:
                        try:
                            from app.utils.fotos_locales import guardar_foto_local
                            ruta_imagen = guardar_foto_local(foto_local_subida, actual_id)
                        except Exception as img_err:
                            st.warning(f"No se pudo guardar la imagen: {img_err}")

                    # 2. Payload completo incluyendo el nuevo nombre y la ruta de imagen
                    payload = {
                        "nombre": nombre,
                        "nombre_local": nombre,
                        "ruc_nit": ruc,
                        "direccion": direccion,
                        "ciudad": ciudad,
                        "pais": pais,
                        "tipo_establecimiento": tipo,
                        "email_contacto": email,
                        "telefono": telefono,
                        "telefono_contacto": telefono,
                        "imagen": ruta_imagen
                    }
                    
                    try:
                        # 3. Llamada PUT a la API para actualizar la base de datos
                        resp_put = requests.put(f"{api_url}/locales/{actual_id}", json=payload, timeout=5)
                        if resp_put.status_code in [200, 201]:
                            st.success("¡Nombre y datos del local actualizados correctamente en la base de datos y archivos!")
                            st.rerun()
                        else:
                            st.error(f"No se pudo actualizar en la API: {resp_put.text}")
                    except Exception as e:
                        st.error(f"Error de conexión con el servidor: {e}")
        else:
            st.warning("⚠️ No se encontró ningún local asociado a tu sesión actual.")

    # --- PESTAÑA 2: REGISTRAR NUEVO LOCAL ---
    with tab_nuevo:
        st.markdown("---")
        st.subheader("🏢 Añadir una Nueva Sucursal")
        st.info("💡 Nota: Al registrar una nueva sucursal, esta quedará en estado pendiente de aprobación y deberá ser **activada por el Superadmin** para formar parte operativa de Bookea.")

        with st.form("form_crear_nuevo_local"):
            col_n1, col_n2 = st.columns(2)
            with col_n1:
                nuevo_nombre = st.text_input("Nombre Comercial del Local", placeholder="Ej. Bar Sucursal Norte")
                nuevo_ruc = st.text_input("RUC / NIT", placeholder="Número de identificación")
                nueva_direccion = st.text_input("Dirección Exacta", placeholder="Calle y Número")
            with col_n2:
                nueva_ciudad = st.text_input("Ciudad", placeholder="Ciudad")
                nuevo_pais = st.text_input("País", value="Ecuador", placeholder="País")
                nuevo_tipo = st.text_input("Tipo de Establecimiento", placeholder="Ej. Discoteca, Restaurante...")
                nuevo_telefono = st.text_input("Teléfono / WhatsApp de Contacto", placeholder="Teléfono")

            submit_crear = st.form_submit_button("🚀 Enviar para Activación")
            
            if submit_crear:
                if nuevo_nombre and nueva_direccion:
                    payload_nuevo = {
                        "nombre": nuevo_nombre,
                        "nombre_local": nuevo_nombre,
                        "ruc_nit": nuevo_ruc,
                        "direccion": nueva_direccion,
                        "ciudad": nueva_ciudad,
                        "pais": nuevo_pais,
                        "tipo_establecimiento": nuevo_tipo,
                        "telefono_contacto": nuevo_telefono,
                        "propietario_id": usuario_id,
                        "usuario_id": usuario_id,
                        "activo": False,          
                        "estado": "pendiente"     
                    }
                    try:
                        resp_post = requests.post(f"{api_url}/locales/", json=payload_nuevo, timeout=5)
                        if resp_post.status_code in [200, 201]:
                            st.success("¡Nuevo local registrado con éxito! Pendiente de activación por el Superadmin.")
                        else:
                            st.error(f"Error al registrar el local: {resp_post.text}")
                    except Exception as e:
                        st.error(f"Error de conexión con el servidor: {e}")
                else:
                    st.warning("⚠️ Por favor completa al menos el Nombre Comercial y la Dirección.")