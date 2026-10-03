import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


def render_local_public_web(slug_o_id, api_url=API_URL):
  """Renderiza la mini-web pública e individual de un local usando su slug o ID.

  Muestra: información, cartelera de eventos, lista de precios, publicidad y
  opción de login/reserva para clientes.
  """
  current_api_url = api_url or API_URL

  # --- 1. CONSULTAR DATOS DEL LOCAL DESDE LA API ---
  local_data = None
  try:
    # Usamos tu ruta flexible de FastAPI que acepta slug o id
    resp = requests.get(f"{current_api_url}/locales/{slug_o_id}", timeout=5)
    if resp.status_code == 200:
      local_data = resp.json()
  except Exception as e:
    st.error(f"Error al conectar con el servidor: {e}")

  if not local_data:
    st.error("❌ No se encontró el establecimiento o la URL no es válida.")
    if st.button("Volver al Inicio"):
      st.session_state.vista_actual_publica = "home"
      st.rerun()
    return

  # --- EXTRACCIÓN DE DATOS DEL LOCAL ---
  venue_id = local_data.get("id")
  nombre = local_data.get("nombre") or local_data.get("nombre_local") or "Local Exclusivo"
  tipo_est = local_data.get("tipo_establecimiento", "Establecimiento")
  descripcion = local_data.get("descripcion", "Bienvenidos a nuestro espacio exclusivo.")
  direccion = local_data.get("direccion") or local_data.get("ubicacion") or "Ubicación principal"
  ciudad = local_data.get("ciudad", "Guayaquil")
  capacidad = local_data.get("capacidad", "Consultar")
  imagen_path = local_data.get("imagen") or local_data.get("foto") or ""
  slug = local_data.get("slug", "")

  # --- CABECERA Y BOTÓN DE RETORNO / LOGIN ---
  col_ret, col_tit, col_log = st.columns([1, 4, 1.5])
  with col_ret:
    if st.button("⬅️ Volver", use_container_width=True):
      st.session_state.vista_actual_publica = "home"
      st.rerun()

  with col_log:
    cliente_logueado = st.session_state.get("logged_in") and st.session_state.get("user_role") == "cliente"
    if cliente_logueado:
      st.success(f"👤 {st.session_state.get('user_name', 'Cliente')}")
    else:
      if st.button("🔑 Iniciar Sesión", use_container_width=True):
        st.session_state.vista_actual_publica = "login_cliente"
        st.rerun()

  st.markdown("---")

  # --- 2. SECCIÓN PRINCIPAL / PORTADA DEL LOCAL (ESTILO WEB HTML) ---
  col_img, col_info = st.columns([1.2, 2])

  with col_img:
    imagen_encontrada = None
    if imagen_path:
      ruta_limpia = imagen_path.lstrip("/")
      if os.path.exists(ruta_limpia) or os.path.exists(imagen_path):
        imagen_encontrada = ruta_limpia if os.path.exists(ruta_limpia) else imagen_path

    if imagen_encontrada:
      st.image(imagen_encontrada, use_container_width=True)
    else:
      st.info("📌 Local sin imagen de portada")

  with col_info:
    st.markdown(f"## {nombre}")
    st.markdown(f"`{tipo_est}`  |  🏙️ {ciudad}")
    
    # Enlace a Google Maps
    query_completa = f"{direccion}, {ciudad}"
    url_maps = f"https://www.google.com/maps/search/?api=1&query={requests.utils.quote(query_completa)}"
    st.markdown(f"📍 **Dirección:** [{direccion}]({url_maps}) (Ver en Mapa)", unsafe_allow_html=True)
    st.markdown(f"👥 **Capacidad:** {capacidad} personas")
    if slug:
      st.caption(f"🌐 Enlace amigable: /local/{slug}")

  st.markdown("### 📖 Acerca de nosotros")
  st.write(descripcion)
  st.markdown("---")

  # --- 3. SECCIÓN DE PUBLICIDAD / OFERTAS ---
  st.markdown("### 📢 Publicidad & Promociones")
  with st.container(border=True):
    st.info("✨ ¡Disfruta de nuestros paquetes especiales para eventos corporativos, cumpleaños y reservas VIP con atención personalizada!")

  # --- 4. LISTA DE PRECIOS ---
  st.markdown("### 📋 Lista de Precios y Servicios")
  # Puedes adaptar esta sección si tu API ya trae un endpoint de precios/menú del local
  col_p1, col_p2, col_p3 = st.columns(3)
  with col_p1:
    with st.container(border=True):
      st.markdown("#### 🎟️ Entrada General")
      st.markdown("**$10.00**")
      st.caption("Acceso al local y áreas comunes.")
  with col_p2:
    with st.container(border=True):
      st.markdown("#### 🍾 Mesa VIP")
      st.markdown("**$50.00**")
      st.caption("Incluye botella de cortesía y atención preferencial.")
  with col_p3:
    with st.container(border=True):
      st.markdown("#### 🌟 Evento Privado")
      st.markdown("**Consultar**")
      st.caption("Alquiler completo del establecimiento.")

  st.markdown("---")

  # --- 5. CARTELERA DE EVENTOS DEL LOCAL ---
  st.markdown(f"### 🗓️ Cartelera de Eventos - {nombre}")
  
  eventos_a_mostrar = []
  try:
    resp_e = requests.get(f"{current_api_url}/locales/{venue_id}/eventos", timeout=5)
    if resp_e.status_code == 200:
      evs = resp_e.json()
      if isinstance(evs, list):
        eventos_a_mostrar = [e for e in evs if str(e.get("estado", "activo")).strip().lower() not in ["pendiente", "rechazado"]]
  except Exception:
    pass

  if not eventos_a_mostrar:
    eventos_a_mostrar = [{
        "id": 999,
        "titulo": "Reserva Personalizada",
        "estado": "plantilla",
        "fecha": "A elegir por el cliente"
    }]

  cols_ev = st.columns(min(len(eventos_a_mostrar), 3) or 1)
  for idx, evento in enumerate(eventos_a_mostrar):
    ev_id = evento.get("id")
    nombre_ev = evento.get("titulo") or evento.get("nombre_evento", "Evento")
    fecha_ev = evento.get("fecha", "Fecha por confirmar")

    with cols_ev[idx % len(cols_ev)]:
      with st.container(border=True):
        st.markdown(f"#### 🎵 {nombre_ev}")
        st.caption(f"📅 Fecha: {fecha_ev}")
        
        if st.button("✨ Reservar este Evento", key=f"btn_res_web_{venue_id}_{ev_id}_{idx}", use_container_width=True, type="primary"):
          if cliente_logueado:
            st.session_state.evento_a_reservar = ev_id
            st.session_state.local_seleccionado_reserva = venue_id
            st.session_state.vista_actual_publica = "reservacion"
            st.rerun()
          else:
            st.session_state.evento_pendiente_reserva = ev_id
            st.session_state.local_pendiente_reserva = venue_id
            st.warning("Debes iniciar sesión para reservar.")
            st.rerun()

  # --- 6. PANEL DE LOGIN RÁPIDO INTEGRADO SI ESTÁ PENDIENTE ---
  if st.session_state.get("evento_pendiente_reserva") and st.session_state.get("local_pendiente_reserva") == venue_id:
    st.markdown("---")
    with st.container(border=True):
      st.markdown("### 🔒 Iniciar Sesión de Cliente para Continuar")
      with st.form(f"form_login_web_{venue_id}"):
        email_ingresado = st.text_input("Correo Electrónico", placeholder="tu_correo@ejemplo.com")
        pass_ingresada = st.text_input("Contraseña", type="password", placeholder="••••••••")
        
        btn_enviar_login = st.form_submit_button("Entrar y Confirmar Reserva", use_container_width=True)
        if btn_enviar_login:
          if email_ingresado and pass_ingresada:
            try:
              r = requests.post(
                  f"{current_api_url}/clientes-auth/login",
                  json={"email": email_ingresado.strip().lower(), "password": pass_ingresada},
                  timeout=5
              )
              if r.status_code == 200:
                data = r.json()
                st.session_state.update({
                    "logged_in": True,
                    "user_role": "cliente",
                    "user_name": data.get("nombre"),
                    "user_id": data.get("id"),
                    "token": data.get("access_token")
                })
                ev_pend = st.session_state.evento_pendiente_reserva
                st.session_state.evento_pendiente_reserva = None
                st.session_state.local_pendiente_reserva = None
                st.session_state.evento_a_reservar = ev_pend
                st.session_state.vista_actual_publica = "reservacion"
                st.success("¡Inicio de sesión exitoso! Redirigiendo...")
                st.rerun()
              else:
                st.error("Credenciales incorrectas. Verifica tus datos.")
            except Exception as ex:
              st.error(f"Error de conexión: {ex}")
          else:
            st.warning("Por favor completa ambos campos.")