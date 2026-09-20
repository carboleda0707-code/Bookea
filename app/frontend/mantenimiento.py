import streamlit as st
import requests

def render_mantenimiento(api_url):
    
    # ============================================================
    # ESTILOS CSS GLOBALES (CAMPOS OSCUROS Y TÍTULOS RESALTADOS)
    # ============================================================
    st.markdown("""
    <style>
    .block-container {
        max-width: 900px !important;
        margin: 0 auto !important;
    }
    div[data-testid="stTextInput"] label p {
        color: #38bdf8 !important;
        font-weight: 600 !important;
        font-size: 15px !important;
    }
    div[data-testid="stTextInput"] input {
        background-color: #141625 !important;
        color: #ffffff !important;
        border: 1px solid rgba(150, 55, 255, 0.4) !important;
        border-radius: 8px !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 5px rgba(56, 189, 248, 0.3) !important;
    }
    div[data-testid="stTextInput"] div[data-baseweb="input"] {
        background-color: #141625 !important;
        border-radius: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("### 🛠️ Gestión y Mantenimiento de Locales")
    st.write("Modifica la información oficial de tu establecimiento registrado en el sistema.")

    # ============================================================
    # RECUPERAR IDENTIFICADORES DINÁMICOS DE LA SESIÓN O URL
    # ============================================================
    query_params = st.query_params
    local_id_url = query_params.get("local_id")
    
    usuario_id = st.session_state.get("usuario_id") or st.session_state.get("user_id")
    empresa_id = st.session_state.get("empresa_id") or st.session_state.get("id_empresa")
    local_id = st.session_state.get("local_id") or local_id_url

    # ============================================================
    # CONSULTAR LOS DATOS REALES DEL LOCAL DESDE LA API
    # ============================================================
    local_data = None
    
    # 1. Intentar buscar directamente por el ID del local actual (si viene en URL o sesión)
    if local_id:
        try:
            resp = requests.get(f"{api_url}/locales/{local_id}", timeout=4)
            if resp.status_code == 200:
                local_data = resp.json()
        except Exception:
            pass

    # 2. Si no se encontró por ID directo, buscar por empresa o propietario logueado
    if not local_data and empresa_id:
        try:
            resp = requests.get(f"{api_url}/locales/empresa/{empresa_id}", timeout=4)
            if resp.status_code == 200:
                lista = resp.json()
                if lista:
                    local_data = lista[0] # Tomar el primer local vinculado a la empresa
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
    # RENDERIZAR FORMULARIO CON DATOS REALES (SIN QUEMAR)
    # ============================================================
    st.markdown("---")
    st.subheader("📍 Información del Local Actual")

    if local_data:
        actual_id = local_data.get("id")
        
        with st.form("form_editar_local_real"):
            col1, col2 = st.columns(2)
            with col1:
                # Usamos los nombres de campos exactos que maneja el backend (models.py / locales.py)
                nombre = st.text_input("Nombre Comercial", value=local_data.get("nombre", local_data.get("nombre_local", "")))
                ruc = st.text_input("RUC / NIT", value=local_data.get("ruc_nit", ""))
                direccion = st.text_input("Dirección Exacta", value=local_data.get("direccion", ""))
            with col2:
                ciudad = st.text_input("Ciudad", value=local_data.get("ciudad", ""))
                tipo = st.text_input("Tipo de Establecimiento", value=local_data.get("tipo_establecimiento", ""))
                email = st.text_input("Correo Electrónico de Contacto", value=local_data.get("email_contacto", ""))
                telefono = st.text_input("Teléfono / WhatsApp", value=local_data.get("telefono_contacto", local_data.get("telefono", "")))
                
            submit_cambios = st.form_submit_button("💾 Guardar Cambios")
            
            if submit_cambios:
                payload = {
                    "nombre": nombre,
                    "nombre_local": nombre,
                    "ruc_nit": ruc,
                    "direccion": direccion,
                    "ciudad": ciudad,
                    "tipo_establecimiento": tipo,
                    "email_contacto": email,
                    "telefono": telefono,
                    "telefono_contacto": telefono
                }
                try:
                    # Endpoint para actualizar el local específico del usuario logueado
                    resp_put = requests.put(f"{api_url}/locales/{actual_id}", json=payload, timeout=5)
                    if resp_put.status_code in [200, 201]:
                        st.success("¡Información del local actualizada correctamente!")
                        st.rerun()
                    else:
                        st.error(f"No se pudo actualizar: {resp_put.text}")
                except Exception as e:
                    st.error(f"Error de conexión con el servidor: {e}")
    else:
        st.warning("⚠️ No se encontró ningún local asociado a tu sesión o cuenta de propietario actual. Verifica tus parámetros de inicio de sesión.")