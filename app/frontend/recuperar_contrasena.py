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

def render_recuperar_contrasena(API_URL):
    # Inicializar estado interno de recuperación si no existe
    if "paso_recuperacion" not in st.session_state:
        st.session_state.paso_recuperacion = "solicitar_correo"

    _, col_center, _ = st.columns([1, 2.5, 1], vertical_alignment="top")
    with col_center:
        st.markdown('🔑 Recuperar Contraseña', unsafe_allow_html=True)
        st.markdown('Sigue los pasos para restablecer el acceso a tu cuenta.', unsafe_allow_html=True)

        if st.session_state.paso_recuperacion == "solicitar_correo":
            with st.form("form_recuperar_standalone"):
                _, c_in, _ = st.columns([0.2, 2.6, 0.2])
                with c_in:
                    rec_email = campo_texto("Correo electrónico", "rec_email_standalone", FUCSIA, placeholder="Correo registrado")
                    col_b1, col_b2 = st.columns(2)
                    btn_enviar = col_b1.form_submit_button("Enviar Código OTP", use_container_width=True)
                    btn_vol = col_b2.form_submit_button("Volver al Login", use_container_width=True)

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
                _, c_in, _ = st.columns([0.2, 2.6, 0.2])
                with c_in:
                    codigo = campo_texto("Código de 6 dígitos", "rec_codigo_standalone", FUCSIA, placeholder="Código OTP")
                    nueva_pass = campo_texto("Nueva Contraseña", "rec_nuev_pass_standalone", FUCSIA, tipo="password", placeholder="Nueva contraseña")
                    
                    col_1, col_2 = st.columns(2)
                    btn_act = col_1.form_submit_button("Actualizar", use_container_width=True)
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
                                    st.success("¡Contraseña actualizada con éxito! Ya puedes iniciar sesión.")
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