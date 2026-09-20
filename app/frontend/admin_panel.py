import streamlit as st
import requests
import pandas as pd

def render_admin_panel(API_URL):
    st.markdown("## Panel de Control SuperAdmin")
    st.markdown("Gestión global de Locales, Propietarios y Sucursales.")
    
    tab1, tab2 = st.tabs(["Gestión de Locales", "Clientes"])
    
    with tab1:
        st.subheader("Listado Completo de Locales y Propietarios")
        try:
            res = requests.get(f"{API_URL}/admin/propietarios")
            
            if res.status_code == 200:
                data = res.json()
                
                if not data:
                    st.info("No hay locales registrados en el sistema.")
                else:
                    df = pd.DataFrame(data)
                    
                    edited_df = st.data_editor(
        df,
        column_config={
            "id": st.column_config.NumberColumn("ID Local", disabled=True),
            "propietario_id": None,
            "nombre_propietario": st.column_config.TextColumn("Propietario"),
            "nombre_local": st.column_config.TextColumn("Nombre del Local"),
            "correo": st.column_config.TextColumn("Correo"),
            "telefono": st.column_config.TextColumn("Teléfono"),
            "direccion": st.column_config.TextColumn("Dirección"),
            "tipo_plan": st.column_config.SelectboxColumn(
                "Tipo de Plan", options=["Normal", "VIP", "Suspendido"], required=True
            ),
            "slug": st.column_config.TextColumn("Slug Único"),
            "correo_envio": st.column_config.TextColumn("Correo Envío (SMTP)"),
            "password_app": st.column_config.TextColumn("Clave App (16 chars)"),
            "activo": st.column_config.CheckboxColumn("¿Activo?"),
        },
        hide_index=True,
        column_order=[
            "id", "nombre_propietario", "nombre_local", "correo",
            "telefono", "direccion", "tipo_plan", "slug", 
            "correo_envio", "password_app", "activo"
        ],
        use_container_width=True,
        key="editor_locales_completos"  # 👈 La coma va aquí arriba, y el paréntesis cierra aquí abajo
    )
                    if st.button("Guardar Cambios de Locales", use_container_width=True):
                        exito = True
                        # Usamos el dataframe que devuelve el data_editor directamente
                        for index, row in edited_df.iterrows():
                            local_id = row.get("id")
                            
                            if local_id:
                                payload = {
                                    "nombre_propietario": row.get("nombre_propietario"),
                                    "nombre_local": row.get("nombre_local"),
                                    "correo": row.get("correo"),
                                    "email_contacto": row.get("email_contacto"),
                                    "telefono": row.get("telefono"),
                                    "telefono_contacto": row.get("telefono_contacto"),
                                    "direccion": row.get("direccion"),
                                    "tipo_plan": row.get("tipo_plan"),
                                    "pagado": True if row.get("tipo_plan") == "VIP" else row.get("pagado"),
                                    "slug": row.get("slug"),
                                    "correo_envio": row.get("correo_envio"),
                                    "password_app": row.get("password_app"),
                                    "activo": row.get("activo")
                                }
                                
                                response = requests.put(f"{API_URL}/admin/local/{local_id}", json=payload)
                                if response.status_code != 200:
                                    exito = False
                                    st.error(f"Error en Local ID {local_id}: {response.text}")
                                    
                        if exito:
                            st.toast("¡Cambios guardados correctamente!", icon="🚀")
                            st.rerun()
                        else:
                            st.error("Hubo un error al actualizar algunos registros.")

                    st.markdown("---")
                    st.markdown("### 🗑️ Zona de Eliminación de Locales")
                    opciones_locales = {f"Local ID {l.get('id')} - Local: {l.get('nombre_local')} (Dueño: {l.get('nombre_propietario')})": l.get('id') for l in data}
                    local_a_eliminar_str = st.selectbox("Seleccione el local específico a eliminar", list(opciones_locales.keys()))
                    
                    if st.button("⚠️ Eliminar Local Seleccionado", type="primary"):
                        id_local_seleccionado = opciones_locales[local_a_eliminar_str]
                        del_res = requests.delete(f"{API_URL}/admin/local/{id_local_seleccionado}")
                        if del_res.status_code == 200:
                            st.success("¡Local eliminado con éxito!")
                            st.rerun()
                        else:
                            error_detalle = del_res.json().get("detail", "Error desconocido")
                            st.error(f"No se pudo eliminar: {error_detalle}")
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