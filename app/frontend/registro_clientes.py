import streamlit as st
import requests

FUCSIA = "#ff1493"

def mostrar_error(r, default):
    try:
        detalle = r.json().get("detail", default)
        st.error(f"Error [{r.status_code}]: {detalle}")
    except Exception:
        st.error(f"Error [{r.status_code}]: {default}")

def etiqueta(t, c):
    st.markdown(f'{t}', unsafe_allow_html=True)

def campo_texto(t, key, color, tipo=None, placeholder=None):
    etiqueta(t, color)
    return st.text_input(t, key=key, type=tipo or "default", placeholder=placeholder, label_visibility="collapsed")

def render_registro_clientes(API_URL):
    # Estilos CSS específicos para la vista de registro de clientes
    st.markdown(f"""
        
    """, unsafe_allow_html=True)  

    _, col_center, _ = st.columns([1, 2.5, 1], vertical_alignment="top")
    with col_center:
        st.markdown('⭐ ¡Regístrate en Bookea!', unsafe_allow_html=True)
        st.markdown('Crea tu cuenta de cliente para reservar al instante.', unsafe_allow_html=True)

        st.markdown('📝 Registro - Cliente', unsafe_allow_html=True)
        with st.form("form_registro_cliente_standalone"):
            _, c_in, _ = st.columns([0.2, 2.6, 0.2])
            with c_in:
                nombre = campo_texto("Nombre completo", "r_cli_nom_s", FUCSIA, placeholder="Nombre completo")
                email = campo_texto("Correo electrónico", "r_cli_mail_s", FUCSIA, placeholder="Correo electrónico")
                telefono = campo_texto("Teléfono", "r_cli_tel_s", FUCSIA, placeholder="Teléfono o celular")
                password = campo_texto("Contraseña", "r_cli_pass_reg_s", FUCSIA, tipo="password", placeholder="Contraseña")

                col_r1, col_r2 = st.columns(2)
                submit_reg = col_r1.form_submit_button("Registrarse", use_container_width=True)
                volver_btn = col_r2.form_submit_button("Volver al Login", use_container_width=True)

            if submit_reg:
                if nombre and email and password:
                    try:
                        r = requests.post(f"{API_URL}/clientes-auth/registro", json={"nombre": nombre, "email": email.strip().lower(), "telefono": telefono, "password": password}, timeout=5)
                        if r.status_code == 200: 
                            st.success("¡Registro exitoso! Ya puedes iniciar sesión.")
                        else: 
                            mostrar_error(r, "Error en el registro.")
                    except requests.RequestException as e: 
                        st.error(f"Error de conexión: {e}")
                else: 
                    st.warning("Completa los campos obligatorios.")
            elif volver_btn:
                st.session_state.vista_actual_publica = "bienvenida"
                st.rerun()