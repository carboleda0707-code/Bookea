import streamlit as st
import requests

def render_configuracion_notificaciones(api_url):
    st.header("⚙️ Configuración de Notificaciones")
    st.write("Configura el correo y el número de celular/WhatsApp que el sistema usará como remitente para enviar los códigos QR a tus clientes.")

    # 1. Cargar configuración actual desde la API (con el prefijo /auth correcto)
    try:
        response = requests.get(f"{api_url}/auth/configuracion/notificaciones", timeout=5)
        datos = response.json() if response.status_code == 200 else {}
    except:
        datos = {"correo_remitente": "", "celular_remitente": "", "password_correo": ""}

    # 2. Formulario en Streamlit
    with st.form("form_config_notif"):
        st.subheader("✉️ Correo de Remitente (SMTP)")
        correo = st.text_input("Correo electrónico de salida", value=datos.get("correo_remitente", ""))
        password = st.text_input("Contraseña de aplicación del correo", type="password", value=datos.get("password_correo", ""), help="Usa una contraseña de aplicación si es Gmail para evitar bloqueos de seguridad.")
        
        st.markdown("---")
        st.subheader("📱 Celular / WhatsApp de Remitente")
        celular = st.text_input("Número de celular (con código de país, ej: +5939XXXXXXXX)", value=datos.get("celular_remitente", ""))

        submitted = st.form_submit_button("💾 Guardar Configuración")

        if submitted:
            try:
                payload = {
                    "correo_remitente": correo,
                    "password_correo": password,
                    "celular_remitente": celular
                }
                # Petición POST apuntando al endpoint dentro de auth.py
                res = requests.post(f"{api_url}/auth/configuracion/notificaciones", data=payload, timeout=5)
                if res.status_code == 200:
                    st.success("¡Configuración actualizada correctamente!")
                else:
                    st.error("Error al guardar en el servidor.")
            except Exception as e:
                st.error(f"Error de conexión con la API: {e}")