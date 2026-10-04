import configparser
import os
import requests
import streamlit as st
from .registro_clientes import render_registro_clientes
from .recuperar_contrasena import render_recuperar_contrasena

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
  # CSS único de presentación. No modifica lógica ni flujo.
  st.markdown("""
  <style>
    /* ===== BOOKEA HEADER ===== */
    .st-key-bookea_header [data-testid="stHorizontalBlock"] {
      display:flex !important; flex-wrap:nowrap !important; align-items:center !important; gap:0 !important;
    }
    .st-key-bookea_header [data-testid="column"] { min-width:0 !important; padding:0 !important; }
    .bookea-brand { display:flex; flex-direction:column; min-width:0; margin:0 !important; padding:0 !important; }
    .bookea-title { font-size:1.65rem; font-weight:700; line-height:1.05; white-space:nowrap; margin:0 !important; padding:0 !important; }
    .bookea-subtitle { font-size:.85rem; line-height:1.15; opacity:.72; white-space:nowrap; margin:3px 0 0 !important; padding:0 !important; }
    .st-key-bookea_header [data-testid="stPopover"] { display:flex !important; justify-content:flex-end !important; align-items:center !important; width:100% !important; }
    .st-key-bookea_header [data-testid="stPopover"] > button,
    .st-key-bookea_header [data-testid="stPopover"] > button:hover,
    .st-key-bookea_header [data-testid="stPopover"] > button:focus,
    .st-key-bookea_header [data-testid="stPopover"] > button:active {
      background:transparent !important; background-color:transparent !important; border:0 !important; outline:0 !important; box-shadow:none !important;
      color:rgba(255,255,255,.92) !important;
    }
    .st-key-bookea_header [data-testid="stPopover"] > button { width:28px !important; min-width:28px !important; height:28px !important; min-height:28px !important; padding:0 !important; margin:0 !important; }

    /* ===== DESTELLO / RIPPLE DE STREAMLIT ===== */
    /* Se elimina la capa visual que aparece al hacer click o enfocar cualquier botón. */
    button,
    button:hover, button:focus, button:focus-visible, button:active,
    [data-testid="stButton"] button,
    [data-testid="stButton"] button:hover, [data-testid="stButton"] button:focus,
    [data-testid="stButton"] button:focus-visible, [data-testid="stButton"] button:active,
    [data-testid="stFormSubmitButton"] button,
    [data-testid="stFormSubmitButton"] button:hover, [data-testid="stFormSubmitButton"] button:focus,
    [data-testid="stFormSubmitButton"] button:focus-visible, [data-testid="stFormSubmitButton"] button:active {
      outline:none !important; box-shadow:none !important;
      -webkit-tap-highlight-color:transparent !important;
      transition:none !important;
    }
    button::before, button::after,
    [data-testid="stButton"] button::before, [data-testid="stButton"] button::after,
    [data-testid="stFormSubmitButton"] button::before, [data-testid="stFormSubmitButton"] button::after {
      content:none !important; display:none !important; background:transparent !important; box-shadow:none !important;
    }
    /* Evita la animación/ripple de BaseWeb. */
    [data-baseweb="button"]::before, [data-baseweb="button"]::after,
    [data-baseweb="button"] *, [data-baseweb="button"] {
      animation:none !important;
    }

    /* ===== SELECTORES ===== */
    [data-baseweb="select"] > div,
    [data-baseweb="select"] > div:hover,
    [data-baseweb="select"] > div:focus,
    [data-baseweb="select"] > div:focus-within,
    [data-baseweb="select"] > div:active {
      outline:none !important; box-shadow:none !important;
      -webkit-tap-highlight-color:transparent !important;
    }
    [role="option"], [role="option"]:hover, [role="option"]:focus, [role="option"]:focus-visible, [role="option"]:active {
      outline:none !important; box-shadow:none !important;
    }

    /* ===== POPOVER ===== */
    [data-testid="stPopoverBody"] { background:#080914 !important; border:0 !important; border-radius:10px !important; padding:4px !important; box-shadow:0 8px 28px rgba(0,0,0,.45) !important; }
    [data-testid="stPopoverBody"] [data-testid="stVerticalBlock"] { gap:0 !important; row-gap:0 !important; }
    [data-testid="stPopoverBody"] [data-testid="stElementContainer"] { margin:0 !important; padding:0 !important; min-height:0 !important; }
    [data-testid="stPopoverBody"] button,
    [data-testid="stPopoverBody"] button:hover, [data-testid="stPopoverBody"] button:focus,
    [data-testid="stPopoverBody"] button:focus-visible, [data-testid="stPopoverBody"] button:active {
      background:transparent !important; background-color:transparent !important; color:rgba(255,255,255,.92) !important;
      border:0 !important; outline:0 !important; box-shadow:none !important; transition:none !important;
      min-height:32px !important; height:32px !important; margin:0 !important; padding:0 12px !important; border-radius:6px !important;
      text-align:left !important;
    }
    [data-testid="stPopoverBody"] button:hover { background:rgba(255,255,255,.07) !important; color:#fff !important; }

    /* ===== IMÁGENES ===== */
    [data-testid="stImage"] img { width:110px !important; height:140px !important; object-fit:cover !important; border-radius:6px; }

    /* ===== LOGIN INLINE ===== */
    .bookea-login-title { font-size:1rem; font-weight:700; text-align:left; margin-bottom:12px; }
    .bookea-input-label { font-size:.88rem; font-weight:700; color:#fff; margin:6px 0 3px; text-align:left; }

    @media (max-width:600px) {
      .bookea-title { font-size:1.45rem; }
      .bookea-subtitle { font-size:.78rem; }
      .st-key-bookea_header [data-testid="stPopover"] > button { width:26px !important; min-width:26px !important; height:26px !important; min-height:26px !important; }
      [data-testid="stPopoverBody"] button { min-height:30px !important; height:30px !important; padding:0 11px !important; font-size:.84rem !important; }
    }
  </style>
  """, unsafe_allow_html=True)

  # Fila única: Bookea a la izquierda y ⋮ a la derecha.
  # El subtítulo queda debajo del título.
  with st.container(key="bookea_header"):
      col_marca, col_menu = st.columns([9, 1], gap="small", vertical_alignment="center")

      with col_marca:
          st.markdown(
              """<div class="bookea-brand">
                <div class="bookea-title">🎟️ Bookea</div>
                <div class="bookea-subtitle">Reservaciones en segundos.</div>
              </div>""",
              unsafe_allow_html=True
          )

      with col_menu:
          # Menú de cuenta: solo se muestra el icono ⋮
          with st.popover("⠇", use_container_width=False):

              if st.button("Entrar", key="menu_cuenta_entrar", use_container_width=True):
                  st.session_state.origen_login = "menu_general"
                  st.session_state.vista_actual_publica = "login_cliente"
                  st.rerun()

              # 🌟 Aquí llamamos a la vista independiente de registro de clientes
              if st.button("Registrarse", key="menu_cuenta_registrarse", use_container_width=True):
                  st.session_state.vista_actual_publica = "registro_clientes"
                  st.rerun()

              if st.button("Olvidé contraseña", key="menu_cuenta_olvido", use_container_width=True):
                  st.session_state.vista_actual_publica = "recuperar_contrasena"
                  st.rerun()

  st.markdown("", unsafe_allow_html=True)
  
  # --- 3. BUSCADOR PRINCIPAL ---
  col_search, col_space = st.columns([2, 8])
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
  st.markdown("###### 🌟 Filtrar Establecimientos")
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
  st.markdown(f"###### {titulo_seccion}")

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
        
        with st.container(border=True):
          st.markdown(f"###### 🗓️ Cartelera de Eventos - {titulo}")
          st.caption(f" Explora Eventos y Reserva Registrandote.")

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

          cols_eventos = st.columns(5)
          for e_idx, evento in enumerate(eventos_a_mostrar):
            ev_id = evento.get("id")
            nombre_ev = evento.get("titulo") or evento.get("nombre_evento", "Sin nombre")
            estado_ev = str(evento.get("estado", "")).strip().lower()
            es_tu_evento = (estado_ev == "plantilla" or str(nombre_ev).strip().lower() == "tu evento")

            with cols_eventos[e_idx % 5]:
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
                        
            # 🌟 Estilos CSS para reducir la altura de los inputs y botones de este formulario
            # 🌟 Contenedor centrado y más estrecho para reducir el tamaño visual drásticamente
            _, col_form, _ = st.columns([0.8, 2.8, 6.8])
            with col_form:
              with st.container(border=True):
                
                st.markdown("""
                <style>
                  .bookea-login-title {
                    font-size: 1rem;
                    font-weight: 700;
                    text-align: left;
                    margin-bottom: 12px;
                  }
                  .bookea-input-label {
                    font-size: 0.88rem;
                    font-weight: 700;
                    color: #ffffff;
                    margin: 6px 0 3px 0;
                    text-align: left;
                  }
                </style>
                """, unsafe_allow_html=True)
                st.markdown('<div class="bookea-login-title">🔒 Inicia sesión para continuar</div>', unsafe_allow_html=True)            

                with st.form(f"form_login_compact_{i}"):
                  st.markdown('<div class="bookea-input-label">Correo electrónico</div>', unsafe_allow_html=True)
                  email_inline = st.text_input("", placeholder="correo@ejemplo.com", key=f"email_c_{i}", label_visibility="collapsed")
                  st.markdown('<div class="bookea-input-label">Contraseña</div>', unsafe_allow_html=True)
                  pass_inline = st.text_input("", type="password", placeholder="Contraseña", key=f"pass_c_{i}", label_visibility="collapsed")
                  
                  _, col_btn_entrar, col_btn_cerrar, _ = st.columns([0.8, 1.4, 1.4, 0.8])
                  with col_btn_entrar:
                    submitted_inline = st.form_submit_button("Entrar", use_container_width=True)
                  with col_btn_cerrar:
                    cerrar_inline = st.form_submit_button("Cerrar", use_container_width=True)
                  
                  if cerrar_inline:
                    # Solo cierra este login en línea y vuelve al punto donde se solicitó.
                    st.session_state.evento_pendiente_reserva = None
                    st.rerun()
                  
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
      
