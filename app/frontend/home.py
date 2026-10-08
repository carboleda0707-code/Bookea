import configparser
import os
import requests
import streamlit as st
from .registro_clientes import render_registro_clientes
from .recuperar_contrasena import render_recuperar_contrasena
from sesion_local import inicializar_gestion_local, obtener_local_actual, fijar_local_actual
from header_global import render_header


API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


def render_home(api_url=API_URL):
  inicializar_gestion_local()
  """Renderiza la Landing Page principal de Bookea (Vista Pública)."""
  
  # ============================================================
  # ESTILOS OPTIMIZADOS: SELECTORES GRANDES, MENÚ LIMPIO Y MÓVIL
  # ============================================================
  st.markdown("""
    <style>
    .block-container {
        padding-top: 3.25rem !important;
        padding-bottom: 1.5rem !important;
        max-width: 1180px !important;
    }

    /* Botones generales (excluyendo el formulario de login para que no se expandan feo en PC) */
    div.stButton > button:not([data-testid="baseButton-secondary"]), div.stFormSubmitButton > button {
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        padding: 0.6rem 0.8rem !important;
        border-radius: 8px !important;
        min-height: 44px !important;
    }

    /* Forzar que los botones dentro de formularios tengan un ancho automático o controlado en PC */
    div[data-testid="stForm"] div.stButton > button, 
    div[data-testid="stForm"] div.stFormSubmitButton > button {
        width: 100% !important;
    }

    button,
    button:hover, button:focus, button:focus-visible, button:active,
    [data-testid="stButton"] button {
      outline: none !important; box-shadow: none !important;
      -webkit-tap-highlight-color: transparent !important;
      transition: none !important;
    }

    /* Selectores (Categoría y Ubicación) */
    [data-baseweb="select"] {
      width: 100% !important;
      min-width: 170px !important;
    }
    [data-baseweb="select"] > div {
      outline: none !important; 
      box-shadow: none !important;
      background-color: #141625 !important;
      border: 1px solid rgba(255, 255, 255, 0.2) !important;
      border-radius: 10px !important;
      min-height: 48px !important;
      font-size: 1rem !important;
    }

    /* Imagen controlada para que no se estire demasiado en PC */
    [data-testid="stImage"] img { 
        width: 100% !important; 
        max-height: 150px !important; 
        object-fit: cover !important; 
        border-radius: 8px; 
    }

    .bookea-login-title { font-size: 1rem; font-weight: 700; text-align: left; margin-bottom: 12px; }
    .bookea-input-label { font-size: .88rem; font-weight: 700; color: #fff; margin: 6px 0 3px; text-align: left; }
    </style>
    """, unsafe_allow_html=True)
    
  current_api_url = api_url or API_URL

  if "id_local_expandido" not in st.session_state:
    st.session_state.id_local_expandido = None

  if "evento_pendiente_reserva" not in st.session_state:
    st.session_state.evento_pendiente_reserva = None

  # --- RENDERIZAR CABECERA GLOBAL ---
  render_header(subtitulo="Reservaciones en segundos.")
  
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
          ubi = loc.get("ciudad") or loc.get("direccion") or loc.get("ubicacion")
          if ubi:
            ubicaciones_disponibles.add(str(ubi).strip())
  except Exception:
    locales_data = []

  # --- 6. FILTROS AMPLIADOS Y VISIBLES ---
  st.markdown("###### 🌟 Filtrar Establecimientos")
  col_cat_filt, col_ubi_filt, col_espacio = st.columns([1.8, 1.8, 1.4])

  with col_cat_filt:
    cat_seleccionada_label = st.selectbox(
        "Categoría", options=list(categorias_agrupadas.keys()), label_visibility="collapsed"
    )
    subcategorias_activas = categorias_agrupadas.get(cat_seleccionada_label, [])
    filtro_categoria_activo = "" if "Todas" in cat_seleccionada_label else cat_seleccionada_label

  with col_ubi_filt:
    lista_ubis = ["🌐 Todas las ubicaciones"] + sorted(list(ubicaciones_disponibles))
    ubi_seleccionada = st.selectbox(
        "Ubicación", options=lista_ubis, label_visibility="collapsed"
    )
    filtro_ubicacion_activo = "" if ubi_seleccionada == "🌐 Todas las ubicaciones" else ubi_seleccionada
 
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
        
      if filtro_ubicacion_activo:
        coincide_ubicacion = (
            filtro_ubicacion_activo.lower() in ciudad_loc.lower() or
            filtro_ubicacion_activo.lower() in direccion_loc.lower()
        )
        if not coincide_ubicacion:
          continue
        
      if tipo_plan == "VIP" or loc.get("es_vip", False):
        destacados.append(loc)

  # --- 8. RENDERIZADO VERTICAL CON IMAGEN Y ESPACIADO LIMPIO ---
  if destacados:
    for i, venue in enumerate(destacados):
      venue_id = venue.get("id")
      titulo = venue.get("nombre") or venue.get("nombre_local") or venue.get("titulo") or "Local VIP"
      tipo_est = venue.get("tipo_establecimiento", "")
      ubicacion = venue.get("direccion") or venue.get("ubicacion") or "Ubicación"
      
      # Validación flexible de WhatsApp (comprueba múltiples campos)
      telefono_crudo = venue.get("telefono_contacto") or venue.get("telefono") or venue.get("celular") or ""
      telefono_str = str(telefono_crudo).strip()
      
      slug_local = venue.get("slug") or venue.get("local_slug") or venue.get("id")

      with st.container(border=True):
        col_img_mini, col_txt_mini = st.columns([1.5, 2.5], gap="small")
        
        with col_img_mini:
          imagen_path = venue.get("imagen") or venue.get("foto") or venue.get("url_imagen")
          imagen_encontrada = None
          if imagen_path:
            ruta_limpia = imagen_path.lstrip("/")
            if os.path.exists(ruta_limpia) or os.path.exists(imagen_path):
              imagen_encontrada = ruta_limpia if os.path.exists(ruta_limpia) else imagen_path

          if imagen_encontrada:
            st.image(imagen_encontrada, use_container_width=True)
          else:
            st.info("📌 Sin foto")

        with col_txt_mini:
          st.markdown(f"**{titulo}** &nbsp;&nbsp;`{tipo_est}`", unsafe_allow_html=True)
          st.markdown(f"<p style='font-size:11px; margin-bottom:6px;'>📍 {ubicacion}</p>", unsafe_allow_html=True)
          
          # Validación robusta de WhatsApp
          telefono_valido = telefono_str and telefono_str.lower() not in ["none", "null", "", "undefined", "nan"] and any(c.isdigit() for c in telefono_str)

          if telefono_valido:
              num_limpio = ''.join(filter(str.isdigit, telefono_str))
              if len(num_limpio) >= 7:
                  num_whatsapp = f"593{num_limpio.lstrip('0')}" if not num_limpio.startswith("593") else num_limpio
              else:
                  num_whatsapp = num_limpio
              st.markdown(f"📱 [WhatsApp](https://wa.me/{num_whatsapp})", unsafe_allow_html=True)
          else:
              st.markdown("📱 *Sin WhatsApp*", unsafe_allow_html=True)
              
          if slug_local:
              st.markdown(f"🌐 [Ver Mini Web](?local={slug_local})", unsafe_allow_html=True)
              
          st.markdown("<div style='margin-bottom: 6px;'></div>", unsafe_allow_html=True)
                  
          esta_expandido = (str(st.session_state.id_local_expandido) == str(venue_id))  
          texto_boton = "Ocultar Cartelera" if esta_expandido else "Ver Cartelera"
          tipo_btn = "secondary" if esta_expandido else "primary"
          
          if st.button(texto_boton, key=f"btn_vip_compacto_{venue_id}_{i}", type=tipo_btn):
            if esta_expandido:
              st.session_state.id_local_expandido = None
            else:
              st.session_state.id_local_expandido = venue_id
              fijar_local_actual(venue_id)
            st.rerun()

      # --- 9. SI ESTE LOCAL ESTÁ EXPANDIDO ---
      if str(st.session_state.get("id_local_expandido")) == str(venue_id):
        with st.container(border=True):
          st.markdown(f"###### 🗓️ Cartelera de - {titulo}")
          st.caption("Explora Eventos y Reserva Registrandote.")

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

          for e_idx, evento in enumerate(eventos_a_mostrar):
            ev_id = evento.get("id")
            nombre_ev = evento.get("titulo") or evento.get("nombre_evento", "Sin nombre")
            estado_ev = str(evento.get("estado", "")).strip().lower()
            es_tu_evento = (estado_ev == "plantilla" or str(nombre_ev).strip().lower() == "tu evento")
            fecha_raw = evento.get("fecha_hora") or evento.get("fecha", "N/A")
            fecha_corta = fecha_raw.split("T")[0] if "T" in fecha_raw else fecha_raw
            artista = evento.get("artista_orquesta", "A tu elección")

            with st.container(border=True):
              col_ev_img, col_ev_txt = st.columns([1.5, 2.5], gap="small")
              
              with col_ev_img:
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
                  st.markdown(
                      """
                      <div style="background: #141625; padding: 10px; text-align: center; border-radius: 6px; border: 1px dashed rgba(255,255,255,0.15); height: 150px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                          <span style="font-size: 18px;">🎧</span>
                          <b style="color: #ffffff; font-size: 10px; margin-top: 2px;">Bookea</b>
                      </div>
                      """,
                      unsafe_allow_html=True,
                  )

              with col_ev_txt:
                st.markdown(f"**{nombre_ev}**", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size:11px; margin-bottom:2px;'>📅 {fecha_corta}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size:11px; margin-bottom:6px;'>🎤 {artista}</p>", unsafe_allow_html=True)
                
                texto_boton_accion = "✨ Crear" if es_tu_evento else "Reservar"
                if st.button(texto_boton_accion, key=f"compact_ev_{ev_id}_{i}_{e_idx}", use_container_width=False, type="primary"):
                  cliente_logueado = st.session_state.get("logged_in") and st.session_state.get("user_role") == "cliente"
                  if cliente_logueado:
                    st.session_state.evento_a_reservar = ev_id
                    st.session_state.vista_actual_publica = "reservacion"
                    st.rerun()
                  else:
                    st.session_state.evento_pendiente_reserva = ev_id
                    st.rerun()
                    
          if st.session_state.get("evento_pendiente_reserva"):
            with st.container(border=True):
              st.markdown('<div class="bookea-login-title">🔒 Inicia sesión para continuar</div>', unsafe_allow_html=True)            

              email_inline = ""
              pass_inline = ""
              submitted_inline = False
              cerrar_inline = False

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
                      st.session_state.paso_reserva = "seleccionar_mesa"
                      st.rerun()
                    else:
                      st.error("Correo o contraseña incorrectos.")
                  except Exception as e:
                    st.error(f"Error de conexión: {e}")
                else:
                  st.warning("Completa ambos campos.")

        break