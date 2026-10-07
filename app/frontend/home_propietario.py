import streamlit as st
from header_global import render_header


def cambiar_vista(nueva_vista):
  """Función callback con chivato integrado."""
  st.session_state["vista_actual_publica"] = nueva_vista
  # Chivato visual flotante en Streamlit antes del rerun
  st.toast(
      f"🚨 [CHIVATO CALLBACK] Estado cambiado a: {nueva_vista}", icon="🎯"
  )


def render_home_propietario(api_url):
  """BOOKEA PROPIETARIOS — Landing responsiva, limpia y minimalista."""

  # Indicar que estamos en el portal de propietarios para el menú global
  st.session_state["tipo_portal"] = "propietario"

  # --- RENDERIZAR CABECERA GLOBAL ---
  render_header(subtitulo="Soluciones para propietarios")

  st.markdown("", unsafe_allow_html=True)

  # ============================================================
  # TÍTULO, SUBTÍTULO Y HERO MINIMALISTA
  # ============================================================
  st.markdown(
      """
    Gestiona tu negocio de forma simple y directa. Controla tus reservas, mesas y eventos desde una interfaz ligera optimizada para móvil.
    """,
      unsafe_allow_html=True,
  )

  # ============================================================
  # PIE DE PÁGINA COMPACTO
  # ============================================================
  st.markdown(
      """Bookea · Panel de Gestión para Establecimientos""", unsafe_allow_html=True
  )