import requests
import streamlit as st
from header_global import render_header

AZUL = "#2196f3"

def render_registro_propietario(api_url):
  """Vista de registro orientada a Propietarios optimizada para móvil."""
  st.session_state["tipo_portal"] = "propietario"

  # --- CSS OPTIMIZADO PARA MÓVIL ---
  st.markdown("""
      <style>
      .block-container {
          padding-top: 3.25rem !important;
          padding-bottom: 1.5rem !important;
          max-width: 480px !important;
      }
      .prop-title { font-size: 1.1rem; font-weight: 700; text-align: center; margin-bottom: 4px; }
      .prop-subtitle { font-size: 0.85rem; color: #a0a0a0; text-align: center; margin-bottom: 16px; }
      </style>
  """, unsafe_allow_html=True)

  # --- RENDERIZAR CABECERA GLOBAL ---
  render_header(subtitulo="Portal de Propietarios")

  st.markdown('<p class="prop-title">🏢 Registro de Propietario</p>', unsafe_allow_html=True)
  st.markdown('<p class="prop-subtitle">Crea tu cuenta para gestionar tu establecimiento.</p>', unsafe_allow_html=True)

  with st.container(border=True):
    nombre = st.text_input("Nombre y Apellido", key="input_nombre_propietario", placeholder="Tu nombre completo")
    email = st.text_input("Correo Electrónico", key="input_email_reg_propietario", placeholder="correo@negocio.com")
    telefono = st.text_input("Teléfono / WhatsApp", key="input_telefono_propietario", placeholder="Ej. 0991234567")
    password = st.text_input("Contraseña", type="password", key="input_pass_reg_propietario", placeholder="Mínimo 6 caracteres")
    confirm_password = st.text_input("Confirmar Contraseña", type="password", key="input_pass_confirm_propietario", placeholder="Repite tu contraseña")

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

    if st.button("✨ Crear Cuenta", key="btn_enviar_registro_propietario", use_container_width=True, type="primary"):
      if not nombre or not email or not password or not confirm_password:
        st.warning("⚠ Completa los campos obligatorios.")
      elif password != confirm_password:
        st.error("❌ Las contraseñas no coinciden.")
      else:
        try:
          st.success("¡Cuenta creada con éxito! Redirigiendo...")
          st.session_state["vista_actual_publica"] = "login_propietario"
          st.rerun()
        except Exception as e:
          st.error(f"Error al conectar con el servidor: {e}")

  st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

  if st.button("🔐 ¿Ya tienes cuenta? Inicia sesión", key="link_ir_login_desde_reg", use_container_width=True):
    st.session_state["vista_actual_publica"] = "login_propietario"
    st.rerun()

  if st.button("← Volver a portada", key="btn_volver_home_desde_reg", use_container_width=True):
    st.session_state["vista_actual_publica"] = "home_propietario"
    st.rerun()