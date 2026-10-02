import streamlit as st
import requests
import pandas as pd

def render_admin_panel(API_URL):
    
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
            max-width: 520px !important; /* Controla qué tan angosta se ve la tabla */
        }
        
        div[data-testid="stDataFrame"] > div {
            width: 100% !important;
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
        
    st.markdown("Gestión global de Propietarios (Locales) , Clientes")
    
    tab1, tab2 = st.tabs(["Gestión de Locales", "Clientes"])
    
    with tab1:
        st.subheader("Listado y Edición Global de Locales")
        try:
            res = requests.get(f"{API_URL}/admin/propietarios")
            
            if res.status_code == 200:
                data = res.json()
                
                if not data:
                    st.info("No hay locales registrados en el sistema.")
                else:    
                    
                    locales_dict = {f"ID: {l.get('id')} — Local: {l.get('nombre_local')} (Dueño: {l.get('nombre_propietario')})": l for l in data}
                    local_seleccionado_label = st.selectbox("Selecciona Local a editar:", list(locales_dict.keys()), key="select_local_admin_detallado")
                    
                    if local_seleccionado_label:
                        local_actual = locales_dict[local_seleccionado_label]
                        local_id = local_actual.get("id")
                        
                        st.markdown(f"### ✏️ Editando: {local_actual.get('nombre_local')} (ID: {local_id})")
                        
                        with st.form(f"form_editar_local_admin_{local_id}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                nuevo_nombre_local = st.text_input("Nombre del Local", value=local_actual.get("nombre_local") or local_actual.get("nombre") or "")
                                nuevo_correo = st.text_input("Correo Electrónico / Contacto", value=local_actual.get("correo") or local_actual.get("email_contacto") or "")
                                nuevo_telefono = st.text_input("Teléfono principal", value=local_actual.get("telefono") or "")
                                nuevo_telefono_contacto = st.text_input("Teléfono de Contacto", value=local_actual.get("telefono_contacto") or "")
                                nueva_ciudad = st.text_input("Ciudad", value=local_actual.get("ciudad") or "")
                                
                                nueva_direccion = st.text_input("Dirección", value=local_actual.get("direccion") or "")
                                nuevo_slug = st.text_input("Slug Único", value=local_actual.get("slug") or "")
                                
                            with col2:
                                planes_opciones = ["Normal", "VIP", "Suspendido"]
                                plan_actual = local_actual.get("tipo_plan") if local_actual.get("tipo_plan") in planes_opciones else "Normal"
                                nuevo_tipo_plan = st.selectbox("Tipo de Plan", planes_opciones, index=planes_opciones.index(plan_actual))
                                
                                tipo_est_opciones = ["Salsoteca", "Restaurante", "Discoteca", "Cafetería", "Hotel", "Otro"]
                                est_actual = local_actual.get("tipo_establecimiento") if local_actual.get("tipo_establecimiento") in tipo_est_opciones else "Salsoteca"
                                nuevo_tipo_est = st.selectbox("Tipo de Establecimiento", tipo_est_opciones, index=tipo_est_opciones.index(est_actual))
                                
                                nuevo_correo_envio = st.text_input("Correo Envío (SMTP)", value=local_actual.get("correo_envio") or "")
                                nueva_password_app = st.text_input("Clave App (16 chars)", value=local_actual.get("password_app") or "", type="password")
                                
                                nuevo_pais = st.text_input("País", value=local_actual.get("pais") or "Ecuador")
                                
                                #nuevo_aviso_reserva = st.text_area("Aviso de Reserva (Mensaje SMTP)", value=local_actual.get("aviso_reserva") or "")
                                
                                col_lat, col_lon = st.columns(2)
                                with col_lat:
                                    nueva_latitud = st.text_input("Latitud", value=str(local_actual.get("latitud") or ""))
                                with col_lon:
                                    nueva_longitud = st.text_input("Longitud", value=str(local_actual.get("longitud") or ""))
                                
                                nuevo_activo = st.checkbox("¿Local Activo?", value=bool(local_actual.get("activo", True)))
                            
                            st.info(f"👤 **Propietario Relacionado ):** {local_actual.get('nombre_propietario')} (ID Propietario: {local_actual.get('propietario_id')})")
                            
                            btn_guardar = st.form_submit_button("Guardar Cambios del Local", use_container_width=True)
                            
                            if btn_guardar:
                                # Convertir lat/lon de forma segura a float si se ingresaron
                                try:
                                    lat_val = float(nueva_latitud) if nueva_latitud.strip() else None
                                except ValueError:
                                    lat_val = None

                                try:
                                    lon_val = float(nueva_longitud) if nueva_longitud.strip() else None
                                except ValueError:
                                    lon_val = None

                                payload = {
                                    "nombre_propietario": local_actual.get("nombre_propietario"),
                                    "nombre_local": nuevo_nombre_local,
                                    "nombre": nuevo_nombre_local,
                                    "correo": nuevo_correo,
                                    "email_contacto": nuevo_correo,
                                    "telefono": nuevo_telefono,
                                    "telefono_contacto": nuevo_telefono_contacto,
                                    "direccion": nueva_direccion,
                                    "ciudad": nueva_ciudad,
                                    "pais": nuevo_pais,
                                    "tipo_plan": nuevo_tipo_plan,
                                    "tipo_establecimiento": nuevo_tipo_est,
                                    "pagado": True if nuevo_tipo_plan == "VIP" else local_actual.get("pagado", False),
                                    "slug": nuevo_slug,
                                    "correo_envio": nuevo_correo_envio,
                                    "password_app": nueva_password_app,
                                    #"aviso_reserva": nuevo_aviso_reserva,
                                    "latitud": lat_val,
                                    "longitud": lon_val,
                                    "activo": nuevo_activo
                                }
                                
                                response = requests.put(f"{API_URL}/admin/local/{local_id}", json=payload)
                                if response.status_code == 200:
                                    st.success("¡Local actualizado correctamente con éxito, conservando todos sus datos!")
                                    st.rerun()
                                else:
                                    st.error(f"Error al actualizar: {response.text}")
            else:
                st.error(f"⚠️ Servidor respondió con error HTTP {res.status_code}: {res.text}")
        except Exception as e:
            st.error(f"❌ Excepción crítica de conexión: {e}")

    with tab2:
        st.subheader("Listado de Clientes Finales")
        try:
            res_cli = requests.get(f"{API_URL}/admin/clientes")
            if res_cli.status_code == 200:
                clientes = res_cli.json()
                if not clientes:
                    st.info("No hay clientes registrados.")
                else:
                    df_cli = pd.DataFrame(clientes)
                    st.dataframe(df_cli, use_container_width=True)
            else:
                st.error("No se pudo cargar la lista de clientes.")
        except Exception as e:
            st.error(f"Error de conexión: {e}")