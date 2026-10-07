import requests
import streamlit as st
from header_global import render_header

AZUL = "#2196f3"


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


def render_login_propietario(API_URL):
  # Indicar el tipo de portal para el menú global de propietarios
  st.session_state["tipo_portal"] = "propietario"

  # --- RENDERIZAR CABECERA GLOBAL ---
  render_header(subtitulo="Portal de Propietarios")

  # Contenedor del formulario más estrecho
  _, c_form, _ = st.columns([2, 1.5, 2])
  with c_form:
    st.markdown("🔐 Iniciar Sesión - Propietario", unsafe_allow_html=True)

    email_prop = campo_texto(
        "Correo electrónico",
        "login_prop_email",
        AZUL,
        placeholder="Correo electrónico",
    )
    password_prop = campo_texto(
        "Contraseña",
        "login_prop_pass",
        AZUL,
        tipo="password",
        placeholder="Contraseña",
    )

    st.markdown("  ", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
      btn_retornar = st.button("⬅️ Retornar", key="btn_ret_prop", use_container_width=True)
    with col2:
      btn_entrar = st.button("Entrar 🚪", key="btn_ent_prop", use_container_width=True)

    if btn_retornar:
      st.session_state["vista_actual_publica"] = "home"
      st.rerun()

    if btn_entrar:
      if email_prop and password_prop:
        try:
          r = requests.post(
              f"{API_URL}/auth/login",
              json={
                  "correo": email_prop.strip().lower(),
                  "contrasena": password_prop,
              },
              timeout=5,
          )
          if r.status_code == 200:
            data = r.json()
            id_enc = (
                data.get("propietario_id")
                or data.get("id")
                or data.get("usuario_id")
            )

            rol_api = data.get("rol", "").strip().lower()
            rol_asignado = (
                "superadmin"
                if rol_api in ["super_admin", "superadmin"]
                else "propietario"
            )

            st.session_state.update({
                "logged_in": True,
                "user_id": id_enc,
                "propietario_id": id_enc,
                "user_role": rol_asignado,
                "user_name": data.get("nombre"),
                "user_negocio": data.get("nombre_comercial")
                or "Mi Establecimiento",
                "tipo_negocio": data.get("tipo_negocio", "Salsoteca"),
                "token": data.get("access_token"),
                "menu_propietario_activo": "Agenda de Eventos",
            })

            st.query_params["logged"] = "true"
            st.query_params["role"] = rol_asignado
            if data.get("local_id"):
              st.query_params["local_id"] = str(data.get("local_id"))

            st.success(f"¡Bienvenido, {data.get('nombre')}!")
            st.session_state["vista_actual_publica"] = "agenda_propietario"
            st.rerun()
          else:
            mostrar_error(r, "Credenciales incorrectas.")
        except requests.RequestException as e:
          st.error(f"Error de conexión: {e}")
      else:
        st.warning("Completa todos los campos.")