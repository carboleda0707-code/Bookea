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

def render_recuperar_contrasena(API_URL):
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
        .rec-title { font-size: 1.1rem; font-weight: 700; text-align: center; margin-bottom: 4px; }
        .rec-subtitle { font-size: 0.85rem; color: #a0a0a0; text-align: center; margin-bottom: 16px; }
        </style>
    """, unsafe_allow_html=True)

    # --- RENDERIZAR CABECERA GLOBAL ---
    render_header(subtitulo="Recuperar Contraseña")

    # Inicializar estado interno de recuperación si no existe[cite: 7]
    if "paso_recuperacion" not in st.session_state:
        st.session_state.paso_recuperacion = "solicitar_correo"
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="rec-title">🔑 Recuperar Contraseña</p>', unsafe_allow_html=True)
    #st.markdown('<p class="rec-subtitle">Sigue los pasos para restablecer el acceso a tu cuenta.</p>', unsafe_allow_html=True)

    with st.container(border=True):
        if st.session_state.paso_recuperacion == "solicitar_correo":
            with st.form("form_recuperar_standalone"):
                rec_email = campo_texto("Correo electrónico", "rec_email_standalone", FUCSIA, placeholder="Correo registrado")
                
                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                col_b1, col_b2 = st.columns(2)
                btn_enviar = col_b1.form_submit_button("Enviar Código OTP", use_container_width=True, type="primary")
                btn_vol = col_b2.form_submit_button("Volver", use_container_width=True)

                if btn_enviar:
                    if rec_email:
                        try:
                            res = requests.post(f"{API_URL}/auth-recuperacion/solicitar-codigo", json={"email": rec_email.strip().lower()}, timeout=5)
                            if res.status_code == 200:
                                st.success("¡Código enviado con éxito!")
                                st.session_state.update({
                                    "email_recuperando": rec_email.strip().lower(),
                                    "paso_recuperacion": "ingresar_codigo"
                                })
                                st.rerun()
                            else:
                                mostrar_error(res, "Error al solicitar el código.")
                        except requests.RequestException as e:
                            st.error(f"Error de conexión: {e}")
                    else:
                        st.warning("Por favor ingresa un correo electrónico.")
                elif btn_vol:
                    st.session_state.vista_actual_publica = "login_cliente"
                    st.rerun()

        elif st.session_state.paso_recuperacion == "ingresar_codigo":
            st.info(f"Código enviado a: **{st.session_state.get('email_recuperando')}**")
            with st.form("form_codigo_standalone"):
                codigo = campo_texto("Código de 6 dígitos", "rec_codigo_standalone", FUCSIA, placeholder="Código OTP")
                nueva_pass = campo_texto("Nueva Contraseña", "rec_nuev_pass_standalone", FUCSIA, tipo="password", placeholder="Nueva contraseña segura")
                
                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                col_1, col_2 = st.columns(2)
                btn_act = col_1.form_submit_button("Actualizar", use_container_width=True, type="primary")
                btn_can = col_2.form_submit_button("Cancelar", use_container_width=True)

                if btn_act:
                    if codigo and nueva_pass:
                        try:
                            payload = {
                                "email": st.session_state.email_recuperando,
                                "codigo": codigo.strip(),
                                "nueva_password": nueva_pass
                            }
                            res2 = requests.post(f"{API_URL}/auth-recuperacion/cambiar-password", json=payload, timeout=5)
                            if res2.status_code == 200:
                                st.success("¡Contraseña actualizada con éxito!")
                                st.session_state.update({
                                    "paso_recuperacion": "solicitar_correo",
                                    "vista_actual_publica": "login_cliente"
                                })
                                st.session_state.pop("email_recuperando", None)
                                st.rerun()
                            else:
                                mostrar_error(res2, "No se pudo actualizar la contraseña.")
                        except requests.RequestException as e:
                            st.error(f"Error de conexión: {e}")
                    else:
                        st.warning("Completa todos los campos.")
                elif btn_can:
                    st.session_state.update({
                        "paso_recuperacion": "solicitar_correo",
                        "vista_actual_publica": "login_cliente"
                    })
                    st.session_state.pop("email_recuperando", None)
                    st.rerun()