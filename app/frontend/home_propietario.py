import streamlit as st


def cambiar_vista(nueva_vista):
  """Función callback con chivato integrado."""
  st.session_state["vista_actual_publica"] = nueva_vista
  # Chivato visual flotante en Streamlit antes del rerun
  st.toast(
      f"🚨 [CHIVATO CALLBACK] Estado cambiado a: {nueva_vista}", icon="🎯"
  )


def render_home_propietario(api_url):
  """BOOKEA PROPIETARIOS — Landing responsiva, limpia y minimalista."""

  # ============================================================
  # BARRA SUPERIOR + MENÚ DE 3 PUNTOS (MISMA LÍNEA)
  # ============================================================
  col_brand, col_menu = st.columns([6, 1], vertical_alignment="center")

  with col_brand:
    st.markdown("""B Bookea Propietarios """, unsafe_allow_html=True)

  with col_menu:
    with st.popover("⋮"):
      st.markdown("ACCESO PROPIETARIOS", unsafe_allow_html=True)

      if st.button("🔐 Iniciar Sesión", key="min_menu_login_prop", use_container_width=True):
        st.session_state["vista_actual_publica"] = "login_propietario"
        st.rerun()

      if st.button("✨ Registrarse", key="min_menu_reg_prop", use_container_width=True):
        st.session_state["vista_actual_publica"] = "registro_propietario"
        st.rerun()

      if st.button("🔑 Olvidé mi clave", key="min_menu_rec_prop", use_container_width=True):
        st.session_state["vista_actual_publica"] = "recuperar_contrasena_propietario"
        st.rerun()

      
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