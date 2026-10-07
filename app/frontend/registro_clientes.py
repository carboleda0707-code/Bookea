import streamlit as st
import requests
from header_global import render_header

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
    # Definir portal de cliente para la cabecera global
    st.session_state["tipo_portal"] = "cliente"

    # --- CSS OPTIMIZADO PARA MÓVIL ---
    st.markdown("""
        <style>
        .block-container {
            padding-top: 3.25rem !important;
            padding-bottom: 1.5rem !important;
            max-width: 480px !important;
        }
        .bookea-title { font-size: 1.1rem; font-weight: 700; text-align: center; margin-bottom: 4px; }
        .bookea-subtitle { font-size: 0.85rem; color: #a0a0a0; text-align: center; margin-bottom: 16px; }
        .bookea-input-label { font-size: .85rem; font-weight: 600; color: #fff; margin: 6px 0 2px; }
        </style>
    """, unsafe_allow_html=True)

    # --- RENDERIZAR CABECERA GLOBAL ---
    render_header(subtitulo="Registro de Clientes")
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="bookea-title">⭐ ¡Regístrate en Bookea!</p>', unsafe_allow_html=True)
    st.markdown('<p class="bookea-subtitle">Siempre Gratis.</p>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("###### 📝 Registro - Cliente ⭐")
        with st.form("form_registro_cliente_mobile"):
            nombre = campo_texto("Nombre completo", "r_cli_nom_s", FUCSIA, placeholder="Nombre completo")
            email = campo_texto("Correo electrónico", "r_cli_mail_s", FUCSIA, placeholder="correo@ejemplo.com")
            telefono = campo_texto("Teléfono", "r_cli_tel_s", FUCSIA, placeholder="Número de celular")
            password = campo_texto("Contraseña", "r_cli_pass_reg_s", FUCSIA, tipo="password", placeholder="Contraseña segura")

            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
            col_r1, col_r2 = st.columns(2)
            submit_reg = col_r1.form_submit_button("Registrarse", use_container_width=True, type="primary")
            volver_btn = col_r2.form_submit_button("Volver", use_container_width=True)

            if submit_reg:
                if nombre and email and password:
                    try:
                        r = requests.post(f"{API_URL}/clientes-auth/registro", json={"nombre": nombre, "email": email.strip().lower(), "telefono": telefono, "password": password}, timeout=5)
                        if r.status_code == 200: 
                            st.success("¡Registro exitoso!")
                        else: 
                            mostrar_error(r, "Error en el registro.")
                    except requests.RequestException as e: 
                        st.error(f"Error de conexión: {e}")
                else: 
                    st.warning("Completa los campos obligatorios.")
            elif volver_btn:
                st.session_state.vista_actual_publica = "login_cliente"
                st.rerun()