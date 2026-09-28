import streamlit as st
import requests
import pandas as pd

def render_admin_panel(API_URL):
    st.markdown("## Panel de Control SuperAdmin")
    st.markdown("Gestión global de Locales, Propietarios y Sucursales.")
    
    # Estilos CSS personalizados para inputs compactos, títulos resaltados y eliminación de halos blancos
    st.markdown("""
        
    """, unsafe_allow_html=True)
    
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
                    st.markdown("Selecciona un local para modificar su información detallada y mantener su vínculo con el propietario:")
                    
                    locales_dict = {f"ID: {l.get('id')} — Local: {l.get('nombre_local')} (Dueño: {l.get('nombre_propietario')})": l for l in data}
                    local_seleccionado_label = st.selectbox("Local a editar:", list(locales_dict.keys()), key="select_local_admin_detallado")
                    
                    if local_seleccionado_label:
                        local_actual = locales_dict[local_seleccionado_label]
                        local_id = local_actual.get("id")
                        
                        st.markdown("---")
                        st.markdown(f"### ✏️ Editando: {local_actual.get('nombre_local')} (ID: {local_id})")
                        
                        with st.form(f"form_editar_local_admin_{local_id}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                nuevo_nombre_local = st.text_input("Nombre del Local", value=local_actual.get("nombre_local") or "")
                                nuevo_correo = st.text_input("Correo Electrónico", value=local_actual.get("correo") or "")
                                nuevo_telefono = st.text_input("Teléfono", value=local_actual.get("telefono") or "")
                                nueva_direccion = st.text_input("Dirección", value=local_actual.get("direccion") or "")
                                nueva_ciudad = st.text_input("Ciudad", value=local_actual.get("ciudad") or "")
                                nuevo_pais = st.text_input("País", value=local_actual.get("pais") or "")
                                nuevo_slug = st.text_input("Slug Único", value=local_actual.get("slug") or "")
                                
                            with col2:
                                planes_opciones = ["Normal", "VIP", "Suspendido"]
                                plan_actual = local_actual.get("tipo_plan") if local_actual.get("tipo_plan") in planes_opciones else "Normal"
                                nuevo_tipo_plan = st.selectbox("Tipo de Plan", planes_opciones, index=planes_opciones.index(plan_actual))
                                
                                nuevo_correo_envio = st.text_input("Correo Envío (SMTP)", value=local_actual.get("correo_envio") or "")
                                nueva_password_app = st.text_input("Clave App (16 chars)", value=local_actual.get("password_app") or "", type="password")
                                nuevo_activo = st.checkbox("¿Local Activo?", value=bool(local_actual.get("activo", True)))
                            
                            st.info(f"👤 **Propietario Relacionado (No modificable para conservar relación):** {local_actual.get('nombre_propietario')} (ID Propietario: {local_actual.get('propietario_id')})")
                            
                            btn_guardar = st.form_submit_button("Guardar Cambios del Local", use_container_width=True)
                            
                            if btn_guardar:
                                payload = {
                                    "nombre_propietario": local_actual.get("nombre_propietario"),
                                    "nombre_local": nuevo_nombre_local,
                                    "correo": nuevo_correo,
                                    "email_contacto": nuevo_correo,
                                    "telefono": nuevo_telefono,
                                    "telefono_contacto": nuevo_telefono,
                                    "direccion": nueva_direccion,
                                    "ciudad": nueva_ciudad,
                                    "pais": nuevo_pais,
                                    "tipo_plan": nuevo_tipo_plan,
                                    "pagado": True if nuevo_tipo_plan == "VIP" else local_actual.get("pagado", False),
                                    "slug": nuevo_slug,
                                    "correo_envio": nuevo_correo_envio,
                                    "password_app": nueva_password_app,
                                    "activo": nuevo_activo
                                }
                                
                                response = requests.put(f"{API_URL}/admin/local/{local_id}", json=payload)
                                if response.status_code == 200:
                                    st.success("¡Local actualizado correctamente con éxito!")
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