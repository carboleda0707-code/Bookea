import streamlit as st
import requests

FUCSIA, AZUL = "#ff1493", "#2196f3"

def mostrar_error(r, default):
    try: st.error(r.json().get("detail", default))
    except: st.error(default)

def etiqueta(t, c):
    st.markdown(f'<div class="campo-label" style="color:{c};">{t}</div>', unsafe_allow_html=True)

def campo_texto(t, key, color, tipo=None, placeholder=None):
    etiqueta(t, color)
    return st.text_input(t, key=key, type=tipo or "default", placeholder=placeholder, label_visibility="collapsed")

def render_bienvenida(API_URL):
    st.markdown(f"""
        <style>
        .block-container {{ max-width: 950px; padding: 1rem 0 2rem 0; font-family: "Segoe UI", Arial, sans-serif; }}
        .block-container, p, label, span, div, button[data-baseweb="tab"], button[data-baseweb="tab"] * {{ text-shadow: none !important; }}
        .bookea-titulo {{ text-align: center; font-size: 2rem; font-weight: 500; margin: 0.3rem 0 0.15rem 0; }}
        .bookea-subtitulo {{ text-align: center; font-size: 1rem; margin-bottom: 1rem; opacity: 0.9; }}
        .campo-label {{ font-size: 0.90rem; margin: 0.65rem 0 0.25rem 0; }}
        div[data-testid="stTextInput"] input {{ border-radius: 8px; min-height: 42px; }}
        
        /* --- FOCOS DINÁMICOS INDEPENDIENTES POR SECCIÓN --- */
        .tab-cliente div[data-testid="stTextInput"] input:focus {{ box-shadow: 0 0 0 1px {FUCSIA} !important; border-color: {FUCSIA} !important; }}
        .tab-propietario div[data-testid="stTextInput"] input:focus {{ box-shadow: 0 0 0 1px {AZUL} !important; border-color: {AZUL} !important; }}

        /* --- CORRECCIÓN DE BOTONES Y FORMULARIOS --- */
        div.stButton > button, div[data-testid="stFormSubmitButton"] button {{ 
            background-color: #141625 !important; 
            color: #ffffff !important;
            border: 1px solid rgba(150, 55, 255, 0.35) !important;
            border-radius: 8px; 
            font-weight: 700; 
            min-height: 42px; 
            box-shadow: none !important; 
        }}
        
        /* --- ESTADOS HOVER / FOCUS / ACTIVE --- */
        div.stButton > button:hover, div.stButton > button:focus, div.stButton > button:active,
        div[data-testid="stFormSubmitButton"] button:hover, div[data-testid="stFormSubmitButton"] button:focus, div[data-testid="stFormSubmitButton"] button:active {{
            background-color: #1f2238 !important;
            color: #ffffff !important;
            border-color: #00cfff !important;
            box-shadow: none !important;
        }}

        div[data-testid="stSelectbox"] > div > div {{ border-radius: 8px; }}
        button[data-baseweb="tab"] {{ font-size: 1rem; font-weight: 500; }}
        div[data-baseweb="tab-list"] > button:nth-child(1), div[data-baseweb="tab-list"] > button:nth-child(1) * {{ color: {FUCSIA} !important; }}
        div[data-baseweb="tab-list"] > button:nth-child(2), div[data-baseweb="tab-list"] > button:nth-child(2) * {{ color: {AZUL} !important; }}
        div[data-testid="stSelectbox"] [data-baseweb="select"] > div, div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"], li[role="option"] {{ background-color: #080912 !important; color: #ffffff !important; }}
        div[data-testid="stSelectbox"] [data-baseweb="select"] > div {{ border: 1px solid #252936 !important; }}
        div[data-testid="stSelectbox"] [data-baseweb="select"] *, div[data-testid="stSelectbox"] [data-baseweb="select"] svg {{ color: #ffffff !important; fill: #ffffff !important; }}
        ul[role="listbox"] {{ border: 1px solid #252936 !important; }}
        li[role="option"]:hover, li[role="option"][aria-selected="true"] {{ background-color: #20232d !important; }}
        .titulo-cliente, .titulo-propietario {{ font-size: 1.35rem; font-weight: 500; text-align: center; margin: 0.5rem 0 1rem 0; }}
        .titulo-cliente {{ color: {FUCSIA}; }} .titulo-propietario {{ color: {AZUL}; }}
        </style>
    """, unsafe_allow_html=True)

    _, col_center, _ = st.columns([1, 2.5, 1], vertical_alignment="top")
    with col_center:
        st.markdown('<div class="bookea-titulo">⭐ ¡Bienvenido a Bookea!</div>', unsafe_allow_html=True)
        st.markdown('<div class="bookea-subtitulo">Crea tus eventos y reserva al instante.</div>', unsafe_allow_html=True)

        tab_cli, tab_prop = st.tabs(["👤 Cliente", "🏢 Propietario"])

        # ================= CLIENTE =================
        with tab_cli:
            st.markdown('<div class="tab-cliente">', unsafe_allow_html=True)
            accion_cli = st.selectbox("Acción Cliente", ["Iniciar Sesión", "Registrarse", "Olvide Contraseña"], key="menu_cli", label_visibility="collapsed")
            
            if accion_cli == "Iniciar Sesión":
                st.markdown('<div class="titulo-cliente">🔐 Iniciar Sesión - Cliente</div>', unsafe_allow_html=True)
                with st.form("form_login_cliente"):
                    _, c_in, _ = st.columns([0.2, 2.6, 0.2])
                    with c_in:
                        email = campo_texto("Correo electrónico", "l_cli_email", FUCSIA, placeholder="Correo electrónico")
                        password = campo_texto("Contraseña", "l_cli_pass", FUCSIA, tipo="password", placeholder="Contraseña")
                        submit = st.form_submit_button("Ingresar como Cliente", use_container_width=True)
                    if submit:
                        if email and password:
                            try:
                                r = requests.post(f"{API_URL}/clientes-auth/login", json={"email": email.strip().lower(), "password": password}, timeout=5)
                                if r.status_code == 200:
                                    data = r.json()
                                    st.session_state.update({"logged_in": True, "user_role": "cliente", "user_name": data.get("nombre"), "user_id": data.get("id"), "token": data.get("access_token")})
                                    st.success(f"¡Bienvenido, {data.get('nombre')}!")
                                    st.rerun()
                                else: mostrar_error(r, "Credenciales incorrectas.")
                            except requests.RequestException as e: st.error(f"Error de conexión: {e}")
                        else: st.warning("Completa todos los campos.")

            elif accion_cli == "Registrarse":
                st.markdown('<div class="titulo-cliente">📝 ⭐ Registrate Sin Costo ⭐ </div>', unsafe_allow_html=True)
                with st.form("form_registro_cliente"):
                    _, c_in, _ = st.columns([0.2, 2.6, 0.2])
                    with c_in:
                        nombre = campo_texto("Nombre completo", "r_cli_nom", FUCSIA, placeholder="Nombre completo")
                        email = campo_texto("Correo electrónico", "r_cli_mail", FUCSIA, placeholder="Correo electrónico")
                        telefono = campo_texto("Teléfono", "r_cli_tel", FUCSIA, placeholder="Teléfono o celular")
                        password = campo_texto("Contraseña", "r_cli_pass", FUCSIA, tipo="password", placeholder="Contraseña")
                        submit_reg = st.form_submit_button("Registrarse como Cliente", use_container_width=True)
                    if submit_reg:
                        if nombre and email and password:
                            try:
                                r = requests.post(f"{API_URL}/clientes-auth/registro", json={"nombre": nombre, "email": email.strip().lower(), "telefono": telefono, "password": password}, timeout=5)
                                if r.status_code == 200: st.success("¡Registro exitoso! Ya puedes iniciar sesión.")
                                else: mostrar_error(r, "Error en el registro.")
                            except requests.RequestException as e: st.error(f"Error de conexión: {e}")
                        else: st.warning("Completa los campos obligatorios.")

            elif accion_cli == "Olvide Contraseña":
                st.markdown('<div class="titulo-cliente">🔄 Recuperar Acceso - Cliente</div>', unsafe_allow_html=True)
                if "paso_rec_cli" not in st.session_state: st.session_state.paso_rec_cli = "correo"

                if st.session_state.paso_rec_cli == "correo":
                    with st.form("form_rec_cli"):
                        _, c_in, _ = st.columns([0.2, 2.6, 0.2])
                        with c_in:
                            rec_email = campo_texto("Correo electrónico", "rec_e_cli", FUCSIA, placeholder="Correo registrado")
                            btn_enviar = st.form_submit_button("Enviar Código OTP", use_container_width=True)
                        if btn_enviar:
                            if rec_email:
                                try:
                                    res = requests.post(f"{API_URL}/auth-recuperacion/solicitar-codigo", json={"email": rec_email.strip().lower()}, timeout=5)
                                    if res.status_code == 200:
                                        st.success("¡Código enviado!")
                                        st.session_state.update({"mail_cli": rec_email.strip().lower(), "paso_rec_cli": "codigo"})
                                        st.rerun()
                                    else: mostrar_error(res, "Error al solicitar el código.")
                                except requests.RequestException as e: st.error(f"Error de conexión: {e}")
                            else: st.warning("Ingresa un correo.")

                elif st.session_state.paso_rec_cli == "codigo":
                    st.info(f"Código enviado a: **{st.session_state.get('mail_cli')}**")
                    with st.form("form_code_cli"):
                        _, c_in, _ = st.columns([0.2, 2.6, 0.2])
                        with c_in:
                            codigo = campo_texto("Código de 6 dígitos", "cod_c", FUCSIA, placeholder="Código OTP")
                            nueva_pass = campo_texto("Nueva Contraseña", "np_c", FUCSIA, tipo="password", placeholder="Nueva contraseña")
                            col_1, col_2 = st.columns(2)
                            btn_act = col_1.form_submit_button("Actualizar", use_container_width=True)
                            btn_can = col_2.form_submit_button("Cancelar", use_container_width=True)
                        if btn_act:
                            if codigo and nueva_pass:
                                try:
                                    res2 = requests.post(f"{API_URL}/auth-recuperacion/cambiar-password", json={"email": st.session_state.mail_cli, "codigo": codigo.strip(), "nueva_password": nueva_pass}, timeout=5)
                                    if res2.status_code == 200:
                                        st.success("¡Contraseña actualizada!")
                                        st.session_state.update({"paso_rec_cli": "correo"})
                                        st.session_state.pop("mail_cli", None)
                                        st.rerun()
                                    else: mostrar_error(res2, "No se pudo actualizar.")
                                except requests.RequestException as e: st.error(f"Error de conexión: {e}")
                            else: st.warning("Completa todos los campos.")
                        if btn_can:
                            st.session_state.update({"paso_rec_cli": "correo"})
                            st.session_state.pop("mail_cli", None)
                            st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # ================= PROPIETARIO =================
        with tab_prop:
            st.markdown('<div class="tab-propietario">', unsafe_allow_html=True)
            accion_prop = st.selectbox("Acción Propietario", ["Iniciar Sesión", "Registrarse", "Olvide Contraseña"], key="menu_prop", label_visibility="collapsed")
            
            if accion_prop == "Iniciar Sesión":
                st.markdown('<div class="titulo-propietario">🔐 Iniciar Sesión - Propietario</div>', unsafe_allow_html=True)
                with st.form("form_login_prop"):
                    _, c_in, _ = st.columns([0.2, 2.6, 0.2])
                    with c_in:
                        email_prop = campo_texto("Correo electrónico", "login_prop_email", AZUL, placeholder="Correo electrónico")
                        password_prop = campo_texto("Contraseña", "login_prop_pass", AZUL, tipo="password", placeholder="Contraseña")
                        submit_prop = st.form_submit_button("Ingresar como Propietario", use_container_width=True)
                    if submit_prop:
                        if email_prop and password_prop:
                            try:
                                r = requests.post(f"{API_URL}/auth/login", json={"correo": email_prop.strip().lower(), "contrasena": password_prop}, timeout=5)
                                if r.status_code == 200:
                                    data = r.json()
                                    id_enc = data.get("propietario_id") or data.get("id") or data.get("usuario_id")
                                    st.session_state.update({
                                        "logged_in": True, "user_id": id_enc, "propietario_id": id_enc,
                                        "user_role": "superadmin" if data.get("rol") in ["super_admin", "superadmin"] else "propietario",
                                        "user_name": data.get("nombre"), "user_negocio": data.get("nombre_comercial") or "Mi Establecimiento",
                                        "tipo_negocio": data.get("tipo_negocio", "Salsoteca"), "token": data.get("access_token")
                                    })
                                    st.success(f"¡Bienvenido, {data.get('nombre')}!")
                                    st.rerun()
                                else: mostrar_error(r, "Credenciales incorrectas.")
                            except requests.RequestException as e: st.error(f"Error de conexión: {e}")
                        else: st.warning("Completa todos los campos.")

            elif accion_prop == "Registrarse":
                st.markdown('<div class="titulo-propietario">📝 Registrate - 30 Dias Sin Costo ⭐</div>', unsafe_allow_html=True)
                with st.form("form_registro_propietario"):
                    _, c_in, _ = st.columns([0.2, 2.6, 0.2])
                    with c_in:
                        reg_negocio = campo_texto("Nombre del Local", "reg_prop_negocio", AZUL, placeholder="Nombre comercial")
                        etiqueta("Tipo de Establecimiento", AZUL)
                      
                        reg_tipo_negocio = st.selectbox("Tipo de Establecimiento", ["Salsoteca", "Discoteca", "Restaurante", "Resto Bar", "Beach club", "Karaoke", "Lounge"], key="reg_prop_tipo", label_visibility="collapsed")
                       
                        nombre_prop = campo_texto("Nombre del Propietario", "reg_prop_nombre", AZUL, placeholder="Nombre completo")
                        
                        reg_ruc_prop = campo_texto("RUC", "reg_prop_ruc", AZUL, placeholder="RUC o identificación")
                       
                        telefono_prop = campo_texto("Teléfono", "reg_prop_tel", AZUL, placeholder="Teléfono")
                       
                        email_prop = campo_texto("Correo electrónico", "reg_prop_email", AZUL, placeholder="Correo electrónico")
                                                
                        password_prop = campo_texto("Contraseña", "reg_prop_pass", AZUL, tipo="password", placeholder="Contraseña")
                                                
                        submit_reg_prop = st.form_submit_button("Registrarse como Propietario", use_container_width=True)
                    
                    if submit_reg_prop:
                        if nombre_prop and email_prop and password_prop and reg_negocio:
                            try:
                                payload = {"nombre_comercial": reg_negocio, "tipo_negocio": reg_tipo_negocio, "nombre": nombre_prop, "correo": email_prop.strip().lower(), "contrasena": password_prop, "telefono": telefono_prop, "ruc": reg_ruc_prop}
                                r = requests.post(f"{API_URL}/auth/registro", json=payload, timeout=5)
                                if r.status_code == 200: st.success("¡Negocio registrado con éxito! Ya puedes iniciar sesión.")
                                else: mostrar_error(r, "Error en el registro.")
                            except requests.RequestException as e: st.error(f"Error de conexión: {e}")
                        else: st.warning("Por favor completa los campos obligatorios.")

            elif accion_prop == "Olvide Contraseña":
                st.markdown('<div class="titulo-propietario">🔄 Recuperar Acceso - Propietario</div>', unsafe_allow_html=True)
                if "paso_recuperacion_prop" not in st.session_state: st.session_state.paso_recuperacion_prop = "solicitar_correo"

                if st.session_state.paso_recuperacion_prop == "solicitar_correo":
                    with st.form("form_rec_prop"):
                        _, c_in, _ = st.columns([0.2, 2.6, 0.2])
                        with c_in:
                            rec_email_p = campo_texto("Correo electrónico", "rec_email_prop_input", AZUL, placeholder="Correo registrado")
                            btn_enviar_p = st.form_submit_button("Enviar Código OTP", use_container_width=True)
                        if btn_enviar_p:
                            if rec_email_p:
                                try:
                                    res = requests.post(f"{API_URL}/auth-recuperacion/solicitar-codigo", json={"email": rec_email_p.strip().lower()}, timeout=5)
                                    if res.status_code == 200:
                                        st.success("¡Código enviado!")
                                        st.session_state.update({"email_recuperando_prop": rec_email_p.strip().lower(), "paso_recuperacion_prop": "ingresar_codigo"})
                                        st.rerun()
                                    else: mostrar_error(res, "Error al solicitar código.")
                                except requests.RequestException as e: st.error(f"Error de conexión: {e}")
                            else: st.warning("Ingresa un correo.")

                elif st.session_state.paso_recuperacion_prop == "ingresar_codigo":
                    st.info(f"Código enviado a: **{st.session_state.get('email_recuperando_prop')}**")
                    with st.form("form_code_prop"):
                        _, c_in, _ = st.columns([0.2, 2.6, 0.2])
                        with c_in:
                            codigo_p = campo_texto("Código de 6 dígitos", "rec_cod_prop", AZUL, placeholder="Código OTP")
                            nueva_pass_p = campo_texto("Nueva Contraseña", "rec_np_prop", AZUL, tipo="password", placeholder="Nueva contraseña")
                            col1, col2 = st.columns(2)
                            btn_act_p = col1.form_submit_button("Actualizar", use_container_width=True)
                            btn_can_p = col2.form_submit_button("Cancelar", use_container_width=True)
                        if btn_act_p:
                            if codigo_p and nueva_pass_p:
                                try:
                                    payload = {"email": st.session_state.email_recuperando_prop, "codigo": codigo_p.strip(), "nueva_password": nueva_pass_p}
                                    res2 = requests.post(f"{API_URL}/auth-recuperacion/cambiar-password", json=payload, timeout=5)
                                    if res2.status_code == 200:
                                        st.success("¡Contraseña actualizada con éxito!")
                                        st.session_state.update({"paso_recuperacion_prop": "solicitar_correo"})
                                        st.session_state.pop("email_recuperando_prop", None)
                                        st.rerun()
                                    else: mostrar_error(res2, "No se pudo actualizar.")
                                except requests.RequestException as e: st.error(f"Error de conexión: {e}")
                            else: st.warning("Completa todos los campos.")
                        if btn_can_p:
                            st.session_state.update({"paso_recuperacion_prop": "solicitar_correo"})
                            st.session_state.pop("email_recuperando_prop", None)
                            st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)