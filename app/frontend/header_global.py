import streamlit as st

def render_header(subtitulo="Soluciones para propietarios"):
    """
    Renderiza la cabecera global de Bookea con logo, subtítulo dinámico
    y menú contextual según el estado de la sesión y el rol del usuario.
    """
    
    st.markdown("""
        <style>
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
            padding: 4px !important; 
            box-shadow: 0 8px 28px rgba(0,0,0,.45) !important; 
            min-width: 190px !important;
        }
        
        [data-testid="stPopoverBody"] [data-testid="stButton"],
        [data-testid="stPopoverBody"] div.stButton,
        [data-testid="stPopoverBody"] div[data-baseweb] {
            background: transparent !important;
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
        }
        
        [data-testid="stPopoverBody"] button,
        [data-testid="stPopoverBody"] [data-testid="stButton"] > button {
            background: transparent !important; 
            background-color: transparent !important;
            color: #e2e8f0 !important; 
            border: none !important; 
            box-shadow: none !important;
            outline: none !important;
            min-height: 30px !important; 
            height: 30px !important; 
            margin: 1px 0 !important; 
            padding: 0 10px !important; 
            border-radius: 6px !important; 
            text-align: left !important;
            font-size: 0.85rem !important;
            font-weight: 500 !important;
            white-space: nowrap !important;
            width: 100% !important;
            display: flex !important;
            align-items: center !important;
            transition: background-color 0.15s ease;
        }
        
        [data-testid="stPopoverBody"] button:hover,
        [data-testid="stPopoverBody"] [data-testid="stButton"] > button:hover { 
            background: rgba(150, 55, 255, 0.15) !important; 
            color: #ffffff !important; 
            border: none !important;
            box-shadow: none !important;
        }

        [data-testid="stPopoverBody"] button p,
        [data-testid="stPopoverBody"] button span,
        [data-testid="stPopoverBody"] [data-testid="stButton"] > button p,
        [data-testid="stPopoverBody"] [data-testid="stButton"] > button span {
            color: inherit !important;
            font-size: 0.85rem !important;
            text-align: left !important;
            white-space: nowrap !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        </style>
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
                    st.markdown(f"<p style='font-size:11px; padding:4px 8px; color:#00cfff; margin:0;'>👤 {st.session_state.get('user_name', 'Cliente')}</p>", unsafe_allow_html=True)
                    if st.button("Mis Reservas", key="menu_cli_reservas", use_container_width=True):
                        st.session_state.vista_actual_publica = "mis_reservas"
                        st.rerun()
                    if st.button("Cerrar Sesión", key="menu_cli_salir", use_container_width=True):
                        st.session_state.clear()
                        st.rerun()

                # --- CONTEXTO 2: PROPIETARIO LOGUEADO O EN PORTAL PROPIETARIO ---
                elif st.session_state.get("logged_in") and st.session_state.get("user_role") == "propietario":
                    st.markdown(f"<p style='font-size:11px; padding:4px 8px; color:#9637ff; margin:0;'>🏢 Menú de Gestión</p>", unsafe_allow_html=True)
                    
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
                    
                    st.markdown("<hr style='margin:4px 0; border-color:rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
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
                        
                        st.markdown("<hr style='margin:4px 0; border-color:rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
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

                        st.markdown("<hr style='margin:4px 0; border-color:rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
                        if st.button("🏛️ Ingreso Propietarios", key="menu_gen_propietario", use_container_width=True):
                            st.session_state.vista_actual_publica = "home_propietario"
                            st.rerun()

                        # --- NUEVAS OPCIONES EN EL MENÚ PRINCIPAL ---
                        if st.button("❓ Ayuda", key="menu_gen_ayuda", use_container_width=True):
                            st.session_state.vista_actual_publica = "ayuda"
                            st.rerun()
                        if st.button("🚪 Cerrar", key="menu_gen_cerrar", use_container_width=True):
                            st.session_state.clear()
                            st.rerun()