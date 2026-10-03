import configparser
import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


def render_home(api_url=API_URL):
  """Renderiza la Landing Page principal de Bookea (Vista Pública).

  Incluye selectores de filtros y un sistema de expansión en línea (accordion)
  para consultar la cartelera de eventos de cada local VIP sin salir de la
  página.
  """
  current_api_url = api_url or API_URL

  # --- INICIALIZAR ESTADO DE LOCAL EXPANDIDO ---
  if "id_local_expandido" not in st.session_state:
    st.session_state.id_local_expandido = None

  # 🆕 Variable para rastrear qué evento está esperando login en línea
  if "evento_pendiente_reserva" not in st.session_state:
    st.session_state.evento_pendiente_reserva = None


  # --- CABECERA / INICIO DE SECCIÓN ---
  # Título y subtítulo en una misma línea, con el menú de cuenta a la derecha.
  col_titulo, col_cuenta = st.columns([6, 1])

  with col_titulo:
      st.markdown(
          """
          <div style="display:flex; align-items:baseline; gap:14px; flex-wrap:wrap; margin-bottom:8px;">
              <span style="font-size:1.65rem; font-weight:700;">🎟️ Bookea</span>
              <span style="font-size:1rem; opacity:0.72;">Selecciona Local - Crea Tu Evento - Reserva en segundos.</span>
          </div>
          """,
          unsafe_allow_html=True
      )

  with col_cuenta:
      # Menú de cuenta: Entrar / Registrarse / Olvidé contraseña
      with st.popover("⋮", use_container_width=True):
          st.markdown("**Mi cuenta**")
              
          #st.session_state.vista_actual_publica = "login"
                            
          if st.button("Entrar", key="menu_cuenta_entrar", use_container_width=True):
              st.session_state.origen_login = "menu_general"
              st.session_state.vista_actual_publica = "login_cliente"
              st.rerun()

          if st.button("Registrarse", key="menu_cuenta_registrarse", use_container_width=True):
              st.session_state.vista_actual_publica = "registro"
              st.rerun()

          if st.button("Olvidé contraseña", key="menu_cuenta_olvido", use_container_width=True):
              st.session_state.vista_actual_publica = "recuperar_password"
              st.rerun()

  # --- 3. BUSCADOR PRINCIPAL ---
  col_search, col_space = st.columns([2, 3])
  with col_search:
    busqueda_query = st.text_input(
        "🔍 Buscar",
        placeholder="🔍 Ej. Locales con Música en Vivo...",
        label_visibility="collapsed",
    )
  
  # --- 4. CARGAR MEGACATEGORÍAS DESDE tipo_establecimiento.ini ---
  base_dir = os.path.dirname(os.path.abspath(__file__))
  config_path = os.path.join(base_dir, "tipo_establecimiento.ini")
  
  config = configparser.ConfigParser()
  categorias_agrupadas = {"🌐 Todas las categorías": []}
  
  if os.path.exists(config_path):
    config.read(config_path, encoding="utf-8")
    for section in config.sections():
      nombre = config.get(section, "nombre", fallback=section)
      icono = config.get(section, "icono", fallback="📌")
      
      # 💡 Soportamos tanto 'filtros' como 'filtro' para evitar que falle
      filtros_str = config.get(section, "filtros", fallback="")
      if not filtros_str:
        filtros_str = config.get(section, "filtro", fallback="")
      
      lista_filtros = [f.strip() for f in filtros_str.split(",") if f.strip()]
      label_key = f"{icono} {nombre}".strip()
      categorias_agrupadas[label_key] = lista_filtros

  # --- 5. OBTENER DATOS DE LA API PARA FILTROS DINÁMICOS ---
  locales_data = []
  ubicaciones_disponibles = set()
  try:
    response = requests.get(f"{current_api_url}/locales/", timeout=5)
    if response.status_code == 200:
      locales_data = response.json()
      if isinstance(locales_data, list):
        for loc in locales_data:
          # Extraemos la ubicación (ciudad o dirección principal)
          ubi = loc.get("ciudad") or loc.get("direccion") or loc.get("ubicacion")
          if ubi:
            ubicaciones_disponibles.add(str(ubi).strip())
  except Exception:
    locales_data = []

  # --- 6. FILTROS MINIMALISTAS (CATEGORÍA Y UBICACIÓN) ---
  st.markdown("#### 🌟 Filtrar Establecimientos")
  col_cat_filt, col_ubi_filt, col_espacio = st.columns([1, 1, 3])

  with col_cat_filt:
    cat_seleccionada_label = st.selectbox(
        "Categoría", options=list(categorias_agrupadas.keys()), label_visibility="collapsed"
    )
    subcategorias_activas = categorias_agrupadas.get(cat_seleccionada_label, [])
    filtro_categoria_activo = "" if "Todas" in cat_seleccionada_label else cat_seleccionada_label

  with col_ubi_filt:
    # 📍 Lista desplegable dinámica de ubicaciones extraídas de la API
    lista_ubis = ["🌐 Todas las ubicaciones"] + sorted(list(ubicaciones_disponibles))
    ubi_seleccionada = st.selectbox(
        "Ubicación", options=lista_ubis, label_visibility="collapsed"
    )
    filtro_ubicacion_activo = "" if ubi_seleccionada == "🌐 Todas las ubicaciones" else ubi_seleccionada
 
  # Título dinámico adaptado con la ubicación seleccionada
  titulo_seccion = "🔥 Lugares Destacados (VIP)"
  if filtro_categoria_activo:
    titulo_seccion += f" - {filtro_categoria_activo}"
  if filtro_ubicacion_activo:
    titulo_seccion += f" en {filtro_ubicacion_activo}"
  st.markdown(f"##### {titulo_seccion}")

  # --- 7. APLICAR FILTROS A LOS LOCALES VIP ---
  destacados = []
  if isinstance(locales_data, list):
    for loc in locales_data:
      tipo_plan = str(
          loc.get("tipo_plan", loc.get("plan", loc.get("propietario_plan", "")))
      ).strip().upper()
      
      tipo_est = str(loc.get("tipo_establecimiento", "")).strip().lower()
      
      # Obtenemos los campos de ubicación del local actual
      ciudad_loc = str(loc.get("ciudad", "")).strip()
      direccion_loc = str(loc.get("direccion") or loc.get("ubicacion", "")).strip()
      
      cumple_categoria = True
      if subcategorias_activas:
        subcategorias_normalizadas = [s.strip().lower() for s in subcategorias_activas]
        cumple_categoria = any(
            sub in tipo_est or tipo_est in sub 
            for sub in subcategorias_normalizadas
        )

      if not cumple_categoria:
        continue
        
      # 📍 Validación estricta del filtro de ubicación seleccionado
      if filtro_ubicacion_activo:
        coincide_ubicacion = (
            filtro_ubicacion_activo.lower() in ciudad_loc.lower() or
            filtro_ubicacion_activo.lower() in direccion_loc.lower()
        )
        if not coincide_ubicacion:
          continue
        
      if tipo_plan == "VIP" or loc.get("es_vip", False):
        destacados.append(loc)


# --- 8. RENDERIZADO VERTICAL ADAPTADO PARA MÓVILES Y ESCRITORIO ---
  if destacados:
    
    # CSS para garantizar que en pantallas móviles la foto y los textos quepan lado a lado sin estorbar
    st.markdown("""
      <style>
        [data-testid="stImage"] img {
        width: 110px !important;
        height: 140px !important;
        object-fit: cover !important;
        border-radius: 6px;
        }
      </style>
        
    """, unsafe_allow_html=True)

    for i, venue in enumerate(destacados):
      venue_id = venue.get("id")
      titulo = venue.get("nombre") or venue.get("nombre_local") or venue.get("titulo") or "Local VIP"
      tipo_est = venue.get("tipo_establecimiento", "")
      ubicacion = venue.get("direccion") or venue.get("ubicacion") or "Ubicación"
      capacidad = venue.get("capacidad", "Consultar")
      descripcion = venue.get("descripcion", "Espacio exclusivo para tus eventos.")

      # Tarjeta optimizada para flujo compacto lado a lado
      with st.container(border=True):
        col_img_mini, col_txt_mini = st.columns([0.5, 4])
        
        with col_img_mini:
          imagen_path = venue.get("imagen") or venue.get("foto") or venue.get("url_imagen")
          imagen_encontrada = None
          if imagen_path:
            ruta_limpia = imagen_path.lstrip("/")
            if os.path.exists(ruta_limpia) or os.path.exists(imagen_path):
              imagen_encontrada = ruta_limpia if os.path.exists(ruta_limpia) else imagen_path

          if imagen_encontrada:
            st.image(imagen_encontrada, use_container_width=False)
          else:
            st.info("📌 Sin foto")

        with col_txt_mini:
          st.markdown(f"**{titulo}**   `{tipo_est}`", unsafe_allow_html=True)
          st.caption(f"📍 {ubicacion} | 👥 {capacidad}")
          st.write(descripcion)
                  
          esta_expandido = (str(st.session_state.id_local_expandido) == str(venue_id))  
          texto_boton = "Ocultar Cartelera" if esta_expandido else "Consultar Cartelera"
          tipo_btn = "secondary" if esta_expandido else "primary"
          
          # Botón pequeño alineado a la izquierda dentro de la columna de texto
          if st.button(texto_boton, key=f"btn_vip_compacto_{venue_id}_{i}", type=tipo_btn):
            if esta_expandido:
              st.session_state.id_local_expandido = None
            else:
              st.session_state.id_local_expandido = venue_id
            st.rerun()

      # --- 9. SI ESTE LOCAL ESTÁ EXPANDIDO, INSERTAR SU CARTELERA EXACTAMENTE AQUÍ ---
      if str(st.session_state.get("id_local_expandido")) == str(venue_id):
        st.markdown("---")
        with st.container(border=True):
          st.markdown(f"### 🗓️ Cartelera de Eventos - {titulo}")
          st.caption(f"📍 Ubicación: {ubicacion} | Tipo: {tipo_est} | Explora los eventos disponibles y reserva.")

          eventos_a_mostrar = []
          try:
            resp_l = requests.get(f"{current_api_url}/locales/{venue_id}/eventos", timeout=5)
            if resp_l.status_code == 200:
              evs_l = resp_l.json()
              if isinstance(evs_l, list):
                eventos_a_mostrar = [e for e in evs_l if str(e.get("estado", "activo")).strip().lower() not in ["pendiente", "rechazado"]]
          except Exception:
            pass

          if not eventos_a_mostrar:
            eventos_a_mostrar = [{
                "id": 999,
                "titulo": "Tu Evento",
                "estado": "plantilla",
                "fecha": "Personalizada",
                "artista_orquesta": "A tu elección"
            }]

          cols_eventos = st.columns(4)
          for e_idx, evento in enumerate(eventos_a_mostrar):
            ev_id = evento.get("id")
            nombre_ev = evento.get("titulo") or evento.get("nombre_evento", "Sin nombre")
            estado_ev = str(evento.get("estado", "")).strip().lower()
            es_tu_evento = (estado_ev == "plantilla" or str(nombre_ev).strip().lower() == "tu evento")

            with cols_eventos[e_idx % 4]:
              with st.container(border=True):
                nombre_imagen = evento.get("imagen")
                imagen_encontrada_ev = None
                posibles_nombres = []
                
                if nombre_imagen:
                  posibles_nombres.append(str(nombre_imagen))
                posibles_nombres.append(f"eventos_{ev_id}.jpg")
                posibles_nombres.append(f"eventos_{ev_id}.png")
                
                if es_tu_evento:
                  posibles_nombres.append("Tu Evento.png")
                  posibles_nombres.append("Tu Evento.jpg")

                for nom in posibles_nombres:
                  limpio = os.path.basename(nom)
                  rutas_prueba = [
                      os.path.join("static", "uploads", limpio),
                      os.path.join("app", "static", "uploads", limpio),
                      os.path.join("static", "uploads", "diseño", limpio),
                      os.path.join("app", "static", "uploads", "diseño", limpio),
                  ]
                  for r in rutas_prueba:
                    if os.path.exists(r):
                      imagen_encontrada_ev = r
                      break
                  if imagen_encontrada_ev:
                    break

                if imagen_encontrada_ev:
                  st.image(imagen_encontrada_ev, use_container_width=True)
                else:
                  st.markdown("🎧 **Bookea**")
                
                st.markdown(f"**{nombre_ev}**")
                texto_boton_accion = "✨ Reservar / Crear" if es_tu_evento else "Reservar"
                
                if st.button(texto_boton_accion, key=f"compact_ev_{ev_id}_{i}_{e_idx}", use_container_width=True, type="primary"):
                  cliente_logueado = st.session_state.get("logged_in") and st.session_state.get("user_role") == "cliente"
                  if cliente_logueado:
                    st.session_state.evento_a_reservar = ev_id
                    st.session_state.vista_actual_publica = "reservacion"
                    st.rerun()
                  else:
                    st.session_state.evento_pendiente_reserva = ev_id
                    st.rerun()
                    
          if st.session_state.get("evento_pendiente_reserva"):
            st.markdown("---")
            
            # 🌟 Contenedor centrado y más estrecho para reducir el tamaño visual drásticamente
            _, col_form, _ = st.columns([2, 1.5, 2])
            with col_form:
              with st.container(border=True):
                st.markdown("🔒 Inicia sesión para continuar", unsafe_allow_html=True)             

            with st.form(f"form_login_compact_{i}"):
              email_inline = st.text_input("Correo electrónico", placeholder="correo@ejemplo.com", key=f"email_c_{i}")
              pass_inline = st.text_input("Contraseña", type="password", placeholder="Contraseña", key=f"pass_c_{i}")
              
              _, col_btn_centro, _ = st.columns([1, 2, 1])
              with col_btn_centro:
                submitted_inline = st.form_submit_button("Entrar", use_container_width=True)
              
              if submitted_inline:
                if email_inline and pass_inline:
                  try:
                    r = requests.post(f"{current_api_url}/clientes-auth/login", json={"email": email_inline.strip().lower(), "password": pass_inline}, timeout=5)
                    if r.status_code == 200:
                      data = r.json()
                      st.session_state.update({
                          "logged_in": True, 
                          "user_role": "cliente", 
                          "user_name": data.get("nombre"), 
                          "user_id": data.get("id"), 
                          "token": data.get("access_token")
                      })
                      
                      st.session_state.id_local_expandido = venue_id
                      ev_pendiente = st.session_state.evento_pendiente_reserva
                      st.session_state.evento_pendiente_reserva = None
                      st.session_state.evento_a_reservar = ev_pendiente
                      st.session_state.vista_actual_publica = "reservacion"
                      
                      st.rerun()
                    else:
                      st.error("Correo o contraseña incorrectos.")
                  except Exception as e:
                    st.error(f"Error de conexión: {e}")
                else:
                  st.warning("Completa ambos campos.")

        break
      