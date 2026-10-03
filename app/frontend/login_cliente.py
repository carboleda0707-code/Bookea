import requests
import streamlit as st

FUCSIA = "#ff1493"


def mostrar_error(r, default):
  try:
    detalle = r.json().get("detail", default)
    st.error(f"Error [{r.status_code}]: {detalle}")
  except Exception:
    st.error(f"Error [{r.status_code}]: {default}")


def etiqueta(t, c):
  st.markdown(f"{t}", unsafe_allow_html=True)


def campo_texto(t, key, color, tipo=None, placeholder=None):
  etiqueta(t, color)
  return st.text_input(
      t,
      key=key,
      type=tipo or "default",
      placeholder=placeholder,
      label_visibility="collapsed",
  )


def render_login_cliente(API_URL):
  # --- CSS PARA REDUCIR TAMAÑO DE INPUTS Y BOTONES ---
  st.markdown(
      """
    
    """,
      unsafe_allow_html=True,
  )

  if "accion_cli" not in st.session_state:
    st.session_state.accion_cli = "Iniciar Sesión"

  _, col_center, _ = st.columns([1, 2.5, 1], vertical_alignment="top")
  with col_center:
    st.markdown("⭐ ¡Bienvenido a Bookea!", unsafe_allow_html=True)
    st.markdown(
        "Registrate - Crea tus eventos y reserva al instante.",
        unsafe_allow_html=True,
    )

  st.markdown("---")

  # --- CONTENEDOR MÁS ESTRECHO ---
  _, c_form, _ = st.columns([2, 1.5, 2])
  with c_form:
    st.markdown("🔐 Iniciar Sesión - Cliente", unsafe_allow_html=True)

    email = campo_texto(
        "Correo electrónico",
        "l_cli_email",
        FUCSIA,
        placeholder="Correo electrónico",
    )
    password = campo_texto(
        "Contraseña",
        "l_cli_pass",
        FUCSIA,
        tipo="password",
        placeholder="Contraseña",
    )

    st.markdown("  ", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
      btn_retornar = st.button("⬅️ Retornar", use_container_width=True)
    with col2:
      btn_entrar = st.button("Entrar 🚪", use_container_width=True)

    if btn_retornar:
      # Si venía del menú general, limpiamos la bandera y volvemos al home
      st.session_state.pop("origen_login", None)
      st.session_state.vista_actual_publica = "home"
      st.rerun()

    if btn_entrar:
      if email and password:
        try:
          r = requests.post(
              f"{API_URL}/clientes-auth/login",
              json={
                  "email": email.strip().lower(),
                  "password": password,
              },
              timeout=5,
          )
          if r.status_code == 200:
            data = r.json()
            st.session_state.update({
                "logged_in": True,
                "user_role": "cliente",
                "user_name": data.get("nombre"),
                "user_id": data.get("id"),
                "token": data.get("access_token"),
            })
            st.success(f"¡Bienvenido, {data.get('nombre')}!")

            # Verificamos si entró por el menú general o si hay un local previo guardado
            origen = st.session_state.get("origen_login")
            local_previo = st.session_state.get("vista_previa_login")

            if origen == "menu_general":
              # Limpiamos la bandera y lo mandamos al home limpio ya logueado
              st.session_state.pop("origen_login", None)
              st.session_state.vista_actual_publica = "home"
            elif local_previo:
              # Si estaba explorando un local específico, lo restauramos
              st.session_state.id_local_expandido = local_previo
              st.session_state.vista_actual_publica = "home"
            else:
              # Por defecto al home
              st.session_state.vista_actual_publica = "home"

            st.rerun()
          else:
            mostrar_error(r, "Credenciales incorrectas.")
        except requests.RequestException as e:
          st.error(f"Error de conexión: {e}")
      else:
        st.warning("Completa todos los campos.")