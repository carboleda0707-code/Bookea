import requests
import streamlit as st


def render_registro_propietario(api_url):
  """Vista de registro orientada a Propietarios de Bookea.

  Permite dar de alta una nueva cuenta de propietario.
  """
  st.markdown(
      """
    Registro de Propietario
    Crea tu cuenta para gestionar tu establecimiento y reservas
    """,
      unsafe_allow_html=True,
  )

  # Campos de entrada para el registro
  nombre = st.text_input("Nombre y Apellido", key="input_nombre_propietario")
  email = st.text_input("Correo Electrónico", key="input_email_reg_propietario")
  telefono = st.text_input("Teléfono / WhatsApp", key="input_telefono_propietario")
  password = st.text_input(
      "Contraseña", type="password", key="input_pass_reg_propietario"
  )
  confirm_password = st.text_input(
      "Confirmar Contraseña",
      type="password",
      key="input_pass_confirm_propietario",
  )

  st.markdown("", unsafe_allow_html=True)

  # Botón de envío de registro
  if st.button(
      "✨ Crear Cuenta de Propietario",
      key="btn_enviar_registro_propietario",
      use_container_width=True,
  ):
    if not nombre or not email or not password or not confirm_password:
      st.warning("⚠️️ Por favor completa los campos obligatorios.")
    elif password != confirm_password:
      st.error("❌ Las contraseñas no coinciden.")
    else:
      try:
        # Simulación de registro exitoso y redirección al login de propietario
        st.success("¡Cuenta creada con éxito! Redirigiendo al inicio de sesión...")
        st.session_state["vista_actual_publica"] = "login_propietario"
        st.rerun()

      except Exception as e:
        st.error(f"Error al conectar con el servidor: {e}")

  st.markdown("", unsafe_allow_html=True)

  # Enlace para ir al login si ya tiene cuenta
  if st.button(
      "🔐 ¿Ya tienes una cuenta? Inicia sesión",
      key="link_ir_login_desde_reg",
      use_container_width=True,
  ):
    st.session_state["vista_actual_publica"] = "login_propietario"
    st.rerun()

  # Botón para volver al home de propietarios
  if st.button(
      "← Volver a portada", key="btn_volver_home_desde_reg", use_container_width=True
  ):
    st.session_state["vista_actual_publica"] = "home_propietario"
    st.rerun()