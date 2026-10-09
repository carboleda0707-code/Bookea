import streamlit as st

def render_header(subtitulo="Soluciones para propietarios"):
    """
    Renderiza la cabecera global de Bookea, incluyendo estilos CSS unificados,
    script de control y menú contextual según el estado de la sesión.
    """
    
    st.markdown("""
        <style>
        /* ============================================================
           BOOKEA — ESTILOS GLOBALES Y DE CABECERA UNIFICADOS
           ============================================================ */

        /* Cabecera nativa de Streamlit */
        header[data-testid="stHeader"] {
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
            visibility: hidden !important;
        }

        /* Ocultar pie de página nativo */
        footer {
            display: none !important;
            visibility: hidden !important;
        }

        /* Contenedor principal */
        [data-testid="stAppViewContainer"],
        [data-testid="stAppViewContainer"] > .main,
        [data-testid="stMain"],
        [data-testid="stMainBlockContainer"],
        .block-container {
            padding-top: 3rem !important;
            max-width: 100% !important;
            margin-top: -60px !important;
        }

        html, body, [data-testid="stAppViewContainer"],
        [data-testid="stApp"], .stApp {
            margin: 0 !important;
            padding-top: 0 !important;
            background-color: #050612 !important;
            color: #f7f7ff !important;
            font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
        }

        [data-testid="stToolbar"] {
            display: none !important;
        }

        /* Botones y selectores globales */
        [data-testid="stButton"] > button,
        [data-testid="stPopover"] > button,
        button[data-baseweb="button"] {
            background-color: #141625 !important;
            background-image: none !important;
            color: #ffffff !important;
            border: 1px solid rgba(150, 55, 255, 0.35) !important;
        }

        [data-testid="stButton"] > button:hover,
        [data-testid="stButton"] > button:focus,
        [data-testid="stButton"] > button:active,
        [data-testid="stPopover"] > button:hover,
        [data-testid="stPopover"] > button:focus,
        [data-testid="stPopover"] > button:active,
        button[data-baseweb="button"]:hover {
            background-color: #1f2238 !important;
            color: #ffffff !important;
            border-color: #00cfff !important;
        }

        [data-testid="stButton"] > button p,
        [data-testid="stPopover"] > button p,
        [data-testid="stPopover"] > button span {
            color: #ffffff !important;
        }

        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            background-color: #141625 !important;
            color: #ffffff !important;
            border: 1px solid rgba(150, 55, 255, 0.35) !important;
        }

        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover {
            background-color: #1f2238 !important;
            border-color: #00cfff !important;
        }

        div[role="listbox"] li[role="option"] {
            background-color: #141625 !important;
            color: #ffffff !important;
        }

        div[role="listbox"] li[role="option"]:hover,
        div[role="listbox"] li[role="option"]:focus,
        div[role="listbox"] li[role="option"][aria-selected="true"] {
          background-color: #20232d !important;
          color: #ffffff !important;
        }

        /* Estilos específicos de la marca y cabecera */
        .bp-brand-container {
            display: flex;
            align-items: center;
            gap: 12px;
            margin: 0 !important;
            padding: 0 !important;
        }
        .bp-logo-box {
            width: 38px;
            height: 38px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #00cfff, #9637ff);
            color: #ffffff;
            font-size: 20px;
            font-weight: 800;
            box-shadow: 0 5px 18px rgba(0, 207, 255, 0.18);
            flex-shrink: 0;
        }
        .bp-brand-text-wrap {
            display: flex;
            flex-direction: column;
            justify-content: center;
            min-width: 0;
        }
        .bp-brand-title {
            font-size: 1.65rem;
            font-weight: 800;
            line-height: 1.05;
            white-space: nowrap;
            margin: 0 !important;
            padding: 0 !important;
            color: #ffffff;
            letter-spacing: -0.5px;
        }
        .bp-brand-title span {
            color: #00cfff;
        }
        .bp-brand-subtitle {
            font-size: 0.82rem;
            line-height: 1.15;
            color: #9ea2b5;
            font-weight: 500;
            white-space: nowrap;
            margin: 2px 0 0 !important;
            padding: 0 !important;
        }
        
        .st-key-bookea_header [data-testid="stHorizontalBlock"] {
          display: flex !important; flex-wrap: nowrap !important; align-items: center !important; gap: 0 !important;
        }
        .st-key-bookea_header [data-testid="column"] { min-width: 0 !important; padding: 0 !important; }
        .st-key-bookea_header [data-testid="stPopover"] { display: flex !important; justify-content: flex-end !important; align-items: center !important; width: 100% !important; }
        .st-key-bookea_header [data-testid="stPopover"] > button {
          background: transparent !important; background-color: transparent !important; border: 0 !important; outline: 0 !important; box-shadow: none !important;
          color: rgba(255,255,255,.92) !important; width: 32px !important; min-width: 32px !important; height: 32px !important; min-height: 32px !important; padding: 0 !important; margin: 0 !important;
        }
        
        [data-testid="stPopoverBody"] { 
            background: #0d0f1a !important; 
            border: 1px solid rgba(150, 55, 255, 0.25) !important; 
            border-radius: 10px !important; 
            padding: 6px 4px !important; 
            box-shadow: 0 8px 28px rgba(0,0,0,.45) !important; 
            min-width: 190px !important;
        }
        
        [data-testid="stPopoverBody"] [data-testid="stVerticalBlock"] {
            gap: 2px !important;
        }
        
        [data-testid="stPopoverBody"] [data-testid="stButton"],
        [data-testid="stPopoverBody"] div.stButton {
            background: transparent !important;
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
            text-align: right !important;
        }
        
        [data-testid="stPopoverBody"] button,
        [data-testid="stPopoverBody"] [data-testid="stButton"] > button,
        [data-testid="stPopoverBody"] button div,
        [data-testid="stPopoverBody"] button p,
        [data-testid="stPopoverBody"] button span {
            background: transparent !important; 
            background-color: transparent !important;
            color: #cbd5e1 !important; 
            border: none !important; 
            box-shadow: none !important;
            outline: none !important;
            min-height: 24px !important; 
            height: 24px !important; 
            margin: 0 !important; 
            padding: 0 8px !important; 
            border-radius: 4px !important; 
            text-align: right !important;
            font-size: 0.82rem !important;
            font-weight: 300 !important;
            white-space: nowrap !important;
            width: 100% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: flex-end !important;
        }
        
        [data-testid="stPopoverBody"] button:hover,
        [data-testid="stPopoverBody"] [data-testid="stButton"] > button:hover { 
            background: rgba(150, 55, 255, 0.15) !important; 
            color: #ffffff !important; 
            border: none !important;
            box-shadow: none !important;
        }
        </style>
        
        <script>
            // Script para cerrar automáticamente el popover al hacer clic en sus opciones
            document.addEventListener("click", function(e) {
                if (e.target.closest('[data-testid="stPopoverBody"] button')) {
                    setTimeout(() => {
                        document.body.click();
                        const overlays = document.querySelectorAll('[data-testid="stPopoverOverlay"]');
                        overlays.forEach(o => o.click());
                    }, 20);
                }
            });
        </script>
    """, unsafe_allow_html=True)

    with st.container(key="bookea_header"):
        col_marca, col_menu = st.columns([9, 1], gap="small", vertical_alignment="center")

        with col_marca:
            st.markdown(
                f"""<div class="bp-brand-container">
                  <div class="bp-logo-box">B</div>
                  <div class="bp-brand-text-wrap">
                    <div class="bp-brand-title">Boo<span>kea</span></div>
                    <div class="bp-brand-subtitle">{subtitulo}</div>
                  </div>
                </div>""",
                unsafe_allow_html=True
            )

        with col_menu:
            with st.popover("⠇", use_container_width=False):
                
                # --- CONTEXTO 1: CLIENTE LOGUEADO ---
                if st.session_state.get("logged_in") and st.session_state.get("user_role") == "cliente":
                    st.markdown(f"<p style='font-size:11px; font-weight:300; padding:2px 6px; color:#00cfff; text-align:right; margin:0 0 2px 0;'>👤 {st.session_state.get('user_name', 'Cliente')}</p>", unsafe_allow_html=True)
                    if st.button("Mis Reservas", key="menu_cli_reservas", use_container_width=True):
                        st.session_state.vista_actual_publica = "mis_reservas"
                        st.rerun()
                    if st.button("Cerrar Sesión", key="menu_cli_salir", use_container_width=True):
                        st.session_state.clear()
                        st.rerun()

                # --- CONTEXTO 2: PROPIETARIO LOGUEADO O EN PORTAL PROPIETARIO ---
                elif st.session_state.get("logged_in") and st.session_state.get("user_role") == "propietario":
                    st.markdown(f"<p style='font-size:11px; font-weight:300; padding:2px 6px; color:#9637ff; text-align:right; margin:0 0 2px 0;'>🏢 Menú de Gestión</p>", unsafe_allow_html=True)
                    
                    if st.button("📅 Agenda de Eventos", key="m_ges_agenda", use_container_width=True):
                        st.session_state.vista_actual = "agenda_propietario"
                        st.rerun()
                    if st.button("🎉 Crear Eventos", key="m_ges_crear_ev", use_container_width=True):
                        st.session_state.vista_actual = "crear_eventos"
                        st.rerun()
                    if st.button("🗺️ Crear Zonas", key="m_ges_zonas", use_container_width=True):
                        st.session_state.vista_actual = "crear_zonas"
                        st.rerun()
                    if st.button("🪑 Crear Mesas", key="m_ges_mesas", use_container_width=True):
                        st.session_state.vista_actual = "crear_mesas"
                        st.rerun()
                    if st.button("🔗 Asignar Mesas", key="m_ges_asignar", use_container_width=True):
                        st.session_state.vista_actual = "asignar_mesas"
                        st.rerun()
                    if st.button("📋 Control de Reservas", key="m_ges_ctrl_res", use_container_width=True):
                        st.session_state.vista_actual = "control_reservas"
                        st.rerun()
                    if st.button("🚪 Control de Puerta", key="m_ges_puerta", use_container_width=True):
                        st.session_state.vista_actual = "control_puerta"
                        st.rerun()
                    
                    st.markdown("<hr style='margin:3px 0; border-color:rgba(255,255,255,0.08);'>", unsafe_allow_html=True)
                    if st.button("🚪 Cerrar Sesión", key="menu_prop_salir", use_container_width=True):
                        st.session_state.clear()
                        st.rerun()

                # --- CONTEXTO 3: VISTA PÚBLICA / GENERAL ---
                else:
                    if st.session_state.get("tipo_portal") == "propietario":
                        if st.button("Iniciar sesión", key="menu_prop_login", use_container_width=True):
                            st.session_state.vista_actual_publica = "login_propietario"
                            st.rerun()
                        if st.button("Registrarse", key="menu_prop_reg", use_container_width=True):
                            st.session_state.vista_actual_publica = "registro_propietario"
                            st.rerun()
                        if st.button("Olvidé contraseña", key="menu_prop_rec", use_container_width=True):
                            st.session_state.vista_actual_publica = "recuperar_contrasena_propietario"
                            st.rerun()
                        
                        st.markdown("<hr style='margin:3px 0; border-color:rgba(255,255,255,0.08);'>", unsafe_allow_html=True)
                        if st.button("❓ Ayuda", key="menu_prop_ayuda", use_container_width=True):
                            st.session_state.vista_actual_publica = "ayuda_propietario"
                            st.rerun()
                        if st.button("🚪 Cerrar", key="menu_prop_cerrar_portal", use_container_width=True):
                            st.session_state.tipo_portal = None
                            st.session_state.vista_actual_publica = "home"
                            st.rerun()
                    else:
                        if st.button("Entrar", key="menu_gen_entrar", use_container_width=True):
                            st.session_state.origen_login = "menu_general"
                            if st.session_state.get("id_local_expandido"):
                                try:
                                    from sesion_local import fijar_local_actual
                                    fijar_local_actual(st.session_state.id_local_expandido)
                                except ImportError:
                                    pass
                            st.session_state.vista_actual_publica = "login_cliente"
                            st.rerun()

                        if st.button("Registrarse", key="menu_gen_registro", use_container_width=True):
                            if st.session_state.get("id_local_expandido"):
                                try:
                                    from sesion_local import fijar_local_actual
                                    fijar_local_actual(st.session_state.id_local_expandido)
                                except ImportError:
                                    pass
                            st.session_state.vista_actual_publica = "registro_clientes"
                            st.rerun()

                        if st.button("Olvidé contraseña", key="menu_gen_olvido", use_container_width=True):
                            if st.session_state.get("id_local_expandido"):
                                try:
                                    from sesion_local import fijar_local_actual
                                    fijar_local_actual(st.session_state.id_local_expandido)
                                except ImportError:
                                    pass
                            st.session_state.vista_actual_publica = "recuperar_contrasena"
                            st.rerun()

                        st.markdown("<hr style='margin:3px 0; border-color:rgba(255,255,255,0.08);'>", unsafe_allow_html=True)
                        if st.button("🏛️ Ingreso Propietarios", key="menu_gen_propietario", use_container_width=True):
                            st.session_state.vista_actual_publica = "home_propietario"
                            st.rerun()
                        if st.button("❓ Ayuda", key="menu_gen_ayuda", use_container_width=True):
                            st.session_state.vista_actual_publica = "ayuda"
                            st.rerun()
                        if st.button("🚪 Cerrar", key="menu_gen_cerrar", use_container_width=True):
                            st.session_state.clear()
                            st.query_params.clear()
                            st.session_state.vista_actual_publica = "home"
                            st.rerun()