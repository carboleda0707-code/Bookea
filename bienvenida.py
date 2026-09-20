import streamlit as st
import requests


# ============================================================
# BOOKEA - PANTALLA DE BIENVENIDA / AUTENTICACIÓN
# ============================================================

# Colores principales
FUCSIA = "#ff1493"
AZUL = "#2196f3"


def mostrar_error(respuesta, mensaje_default):
    """Muestra el detalle del error devuelto por la API."""
    try:
        detalle = respuesta.json().get("detail", mensaje_default)
    except Exception:
        detalle = mensaje_default

    st.error(detalle)


def etiqueta(texto, color):
    """Etiqueta personalizada para los campos de entrada."""
    st.markdown(
        f'<div class="campo-label" style="color:{color};">{texto}</div>',
        unsafe_allow_html=True,
    )


def campo_texto(texto, key, color, tipo=None, placeholder=None):
    """Crea una etiqueta coloreada y un input Streamlit sin etiqueta nativa."""
    etiqueta(texto, color)

    return st.text_input(
        texto,
        key=key,
        type=tipo if tipo else "default",
        placeholder=placeholder,
        label_visibility="collapsed",
    )


def render_bienvenida(API_URL):
    # ========================================================
    # CSS GENERAL
    # ========================================================
    st.markdown(
        f"""
        <style>

        /* ==================================================
           CONTENEDOR PRINCIPAL
           ================================================== */
        .block-container {{
            max-width: 950px;
            padding-top: 1rem;
            padding-bottom: 2rem;
            font-family: "Segoe UI", Arial, sans-serif;
            font-weight: 400;
        }}

        /* Tipografía general más limpia y ligera */
        .block-container,
        .block-container p,
        .block-container label,
        .block-container span,
        .block-container div {{
            text-shadow: none !important;
        }}

        .block-container label {{
            font-weight: 400;
        }}

        /* ==================================================
           TÍTULO Y SUBTÍTULO
           ================================================== */
        .bookea-titulo {{
            text-align: center;
            font-size: 2rem;
            font-weight: 500;
            margin-top: 0.3rem;
            margin-bottom: 0.15rem;
        }}

        .bookea-subtitulo {{
            text-align: center;
            font-size: 1rem;
            margin-top: 0;
            margin-bottom: 1rem;
            opacity: 0.9;
        }}

        /* ==================================================
           ETIQUETAS DE LOS INPUTS
           ================================================== */
        .campo-label {{
            font-family: "Segoe UI", Arial, sans-serif;
            font-size: 0.90rem;
            font-weight: 400;
            text-shadow: none !important;
            margin-top: 0.65rem;
            margin-bottom: 0.25rem;
        }}

        /* ==================================================
           INPUTS
           ================================================== */
        div[data-testid="stTextInput"] input {{
            border-radius: 8px;
            min-height: 42px;
        }}

        div[data-testid="stTextInput"] input:focus {{
            box-shadow: 0 0 0 1px {FUCSIA};
        }}

        /* ==================================================
           BOTONES GENERALES
           ================================================== */
        div.stButton > button,
        div[data-testid="stFormSubmitButton"] button {{
            border-radius: 8px;
            font-weight: 700;
            min-height: 42px;
            transition: none !important;
            box-shadow: none !important;
            outline: none !important;
        }}

        /* ==================================================
           SELECTORES
           ================================================== */
        div[data-testid="stSelectbox"] > div > div {{
            border-radius: 8px;
        }}

        /* ==================================================
           TABS - CLIENTE / PROPIETARIO
           ================================================== */
        button[data-baseweb="tab"] {{
            font-size: 1rem;
            font-weight: 500;
            text-shadow: none !important;
        }}

        /* Cliente = FUCSIA */
        div[data-baseweb="tab-list"] > button:nth-child(1) {{
            color: {FUCSIA} !important;
        }}

        div[data-baseweb="tab-list"] > button:nth-child(1) * {{
            color: {FUCSIA} !important;
        }}

        /* Propietario = AZUL */
        div[data-baseweb="tab-list"] > button:nth-child(2) {{
            color: {AZUL} !important;
        }}

        div[data-baseweb="tab-list"] > button:nth-child(2) * {{
            color: {AZUL} !important;
        }}

        /* Sin sombra en ningún texto de los tabs */
        button[data-baseweb="tab"],
        button[data-baseweb="tab"] * {{
            text-shadow: none !important;
        }}

        /* ==================================================
           MENÚS DE ACCIÓN: FONDO OSCURO + LETRAS BLANCAS
           ================================================== */

        div[data-testid="stSelectbox"] [data-baseweb="select"] > div {{
            background-color: #080912 !important;
            color: #ffffff !important;
            border: 1px solid #252936 !important;
            box-shadow: none !important;
        }}

        div[data-testid="stSelectbox"] [data-baseweb="select"] > div:hover {{
            background-color: #080912 !important;
            color: #ffffff !important;
            border-color: #3a3f50 !important;
            box-shadow: none !important;
        }}

        div[data-testid="stSelectbox"] [data-baseweb="select"] *,
        div[data-testid="stSelectbox"] [data-baseweb="select"] svg {{
            color: #ffffff !important;
            fill: #ffffff !important;
        }}

        div[data-baseweb="popover"],
        div[data-baseweb="menu"],
        ul[role="listbox"] {{
            background-color: #080912 !important;
            color: #ffffff !important;
        }}

        ul[role="listbox"] {{
            border: 1px solid #252936 !important;
            box-shadow: none !important;
        }}

        li[role="option"] {{
            background-color: #080912 !important;
            color: #ffffff !important;
            font-family: "Segoe UI", Arial, sans-serif !important;
            font-weight: 400 !important;
            text-shadow: none !important;
        }}

        li[role="option"]:hover {{
            background-color: #20232d !important;
            color: #ffffff !important;
        }}

        li[role="option"][aria-selected="true"] {{
            background-color: #20232d !important;
            color: #ffffff !important;
        }}

        li[role="option"][aria-selected="true"]:hover {{
            background-color: #2a2e3a !important;
            color: #ffffff !important;
        }}

        /* ==================================================
           ENCABEZADOS
           ================================================== */
        .titulo-cliente {{
            color: {FUCSIA};
            font-size: 1.35rem;
            font-weight: 500;
            text-align: center;
            margin-top: 0.5rem;
            margin-bottom: 1rem;
        }}

        .titulo-propietario {{
            color: {AZUL};
            font-size: 1.35rem;
            font-weight: 500;
            text-align: center;
            margin-top: 0.5rem;
            margin-bottom: 1rem;
        }}

        .subtitulo-cliente {{
            color: {FUCSIA};
            font-weight: 700;
            margin-top: 0.5rem;
            margin-bottom: 0.5rem;
        }}

        .subtitulo-propietario {{
            color: {AZUL};
            font-weight: 700;
            margin-top: 0.5rem;
            margin-bottom: 0.5rem;
        }}

        /* ==================================================
           CAJAS DE FORMULARIOS
           ================================================== */
        .formulario-cliente {{
            border: 1px solid rgba(255, 20, 147, 0.25);
            border-radius: 12px;
            padding: 1rem 1.2rem 0.7rem 1.2rem;
        }}

        .formulario-propietario {{
            border: 1px solid rgba(33, 150, 243, 0.25);
            border-radius: 12px;
            padding: 1rem 1.2rem 0.7rem 1.2rem;
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )

    # ========================================================
    # TÍTULO PRINCIPAL
    # ========================================================
    col_l, col_center, col_r = st.columns([1, 2.5, 1])

    with col_center:
        st.markdown(
            '<div class="bookea-titulo">⭐ ¡Bienvenido a Bookea!</div>',
            unsafe_allow_html=True,
        )

        # El subtítulo queda centrado exactamente respecto al título
        st.markdown(
            '<div class="bookea-subtitulo">Crea tus eventos y reserva al instante.</div>',
            unsafe_allow_html=True,
        )

        # ====================================================
        # TABS PRINCIPALES
        # ====================================================
        tab_cliente, tab_propietario = st.tabs(
            ["👤 Cliente", "🏢 Propietario"]
        )

        # ====================================================
        # CLIENTE
        # ====================================================
        with tab_cliente:
            accion_cliente = st.selectbox(
                "Acción Cliente",
                [
                    "Iniciar Sesión",
                    "Registrarse",
                    "Olvide Contraseña",
                ],
                key="menu_cli",
                label_visibility="collapsed",
            )

            # ------------------------------------------------
            # CLIENTE - INICIAR SESIÓN
            # ------------------------------------------------
            if accion_cliente == "Iniciar Sesión":
                st.markdown(
                    '<div class="titulo-cliente">🔐 Iniciar Sesión - Cliente</div>',
                    unsafe_allow_html=True,
                )

                with st.form("form_login_cliente"):
                    _, c_in, _ = st.columns([0.2, 2.6, 0.2])

                    with c_in:
                        email = campo_texto(
                            "Correo electrónico",
                            "l_cli_email",
                            FUCSIA,
                            placeholder="Ingrese su correo electrónico",
                        )

                        password = campo_texto(
                            "Contraseña",
                            "l_cli_pass",
                            FUCSIA,
                            tipo="password",
                            placeholder="Ingrese su contraseña",
                        )

                        submit = st.form_submit_button(
                            "Ingresar como Cliente",
                            use_container_width=True,
                        )

                    if submit:
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

                                    st.session_state.update(
                                        {
                                            "logged_in": True,
                                            "user_role": "cliente",
                                            "user_name": data.get("nombre"),
                                            "user_id": data.get("id"),
                                            "token": data.get("access_token"),
                                        }
                                    )

                                    st.success(
                                        f"¡Bienvenido, {data.get('nombre')}!"
                                    )
                                    st.rerun()
                                else:
                                    mostrar_error(
                                        r,
                                        "Credenciales incorrectas.",
                                    )

                            except requests.RequestException as e:
                                st.error(f"Error de conexión: {e}")
                        else:
                            st.warning("Completa todos los campos.")

            # ------------------------------------------------
            # CLIENTE - REGISTRO
            # ------------------------------------------------
            elif accion_cliente == "Registrarse":
                st.markdown(
                    '<div class="titulo-cliente">📝 Registro - Nuevo Cliente</div>',
                    unsafe_allow_html=True,
                )

                with st.form("form_registro_cliente"):
                    _, c_in, _ = st.columns([0.2, 2.6, 0.2])

                    with c_in:
                        nombre = campo_texto(
                            "Nombre completo",
                            "r_cli_nom",
                            FUCSIA,
                            placeholder="Ingrese su nombre completo",
                        )

                        email = campo_texto(
                            "Correo electrónico",
                            "r_cli_mail",
                            FUCSIA,
                            placeholder="Ingrese su correo electrónico",
                        )

                        telefono = campo_texto(
                            "Teléfono / Celular",
                            "r_cli_tel",
                            FUCSIA,
                            placeholder="Ingrese su teléfono o celular",
                        )

                        password = campo_texto(
                            "Contraseña",
                            "r_cli_pass",
                            FUCSIA,
                            tipo="password",
                            placeholder="Cree una contraseña",
                        )

                        submit_reg = st.form_submit_button(
                            "Registrarse como Cliente",
                            use_container_width=True,
                        )

                    if submit_reg:
                        if nombre and email and password:
                            try:
                                r = requests.post(
                                    f"{API_URL}/clientes-auth/registro",
                                    json={
                                        "nombre": nombre,
                                        "email": email.strip().lower(),
                                        "telefono": telefono,
                                        "password": password,
                                    },
                                    timeout=5,
                                )

                                if r.status_code == 200:
                                    st.success(
                                        "¡Registro exitoso! Ya puedes iniciar sesión."
                                    )
                                else:
                                    mostrar_error(
                                        r,
                                        "Error en el registro.",
                                    )

                            except requests.RequestException as e:
                                st.error(f"Error de conexión: {e}")
                        else:
                            st.warning(
                                "Completa los campos obligatorios."
                            )

            # ------------------------------------------------
            # CLIENTE - RECUPERAR CONTRASEÑA
            # ------------------------------------------------
            elif accion_cliente == "Olvide Contraseña":
                st.markdown(
                    '<div class="titulo-cliente">🔄 Recuperar Acceso - Cliente</div>',
                    unsafe_allow_html=True,
                )

                if "paso_rec_cli" not in st.session_state:
                    st.session_state.paso_rec_cli = "correo"

                if st.session_state.paso_rec_cli == "correo":
                    with st.form("form_rec_cli"):
                        _, c_in, _ = st.columns([0.2, 2.6, 0.2])

                        with c_in:
                            rec_email = campo_texto(
                                "Correo electrónico",
                                "rec_e_cli",
                                FUCSIA,
                                placeholder="Correo registrado",
                            )

                            btn_enviar = st.form_submit_button(
                                "Enviar Código OTP",
                                use_container_width=True,
                            )

                        if btn_enviar:
                            if rec_email:
                                try:
                                    res = requests.post(
                                        f"{API_URL}/auth-recuperacion/solicitar-codigo",
                                        json={
                                            "email": rec_email.strip().lower()
                                        },
                                        timeout=5,
                                    )

                                    if res.status_code == 200:
                                        st.success("¡Código enviado!")

                                        st.session_state.mail_cli = (
                                            rec_email.strip().lower()
                                        )
                                        st.session_state.paso_rec_cli = (
                                            "codigo"
                                        )
                                        st.rerun()
                                    else:
                                        mostrar_error(
                                            res,
                                            "Error al solicitar el código.",
                                        )

                                except requests.RequestException as e:
                                    st.error(f"Error de conexión: {e}")
                            else:
                                st.warning("Ingresa un correo.")

                elif st.session_state.paso_rec_cli == "codigo":
                    st.info(
                        f"Código enviado a: "
                        f"**{st.session_state.get('mail_cli')}**"
                    )

                    with st.form("form_code_cli"):
                        _, c_in, _ = st.columns([0.2, 2.6, 0.2])

                        with c_in:
                            codigo = campo_texto(
                                "Código de 6 dígitos",
                                "cod_c",
                                FUCSIA,
                                placeholder="Ingrese el código OTP",
                            )

                            nueva_pass = campo_texto(
                                "Nueva Contraseña",
                                "np_c",
                                FUCSIA,
                                tipo="password",
                                placeholder="Ingrese su nueva contraseña",
                            )

                            col_1, col_2 = st.columns(2)

                            btn_act = col_1.form_submit_button(
                                "Actualizar",
                                use_container_width=True,
                            )

                            btn_can = col_2.form_submit_button(
                                "Cancelar",
                                use_container_width=True,
                            )

                        if btn_act:
                            if codigo and nueva_pass:
                                try:
                                    res2 = requests.post(
                                        f"{API_URL}/auth-recuperacion/cambiar-password",
                                        json={
                                            "email": st.session_state.mail_cli,
                                            "codigo": codigo.strip(),
                                            "nueva_password": nueva_pass,
                                        },
                                        timeout=5,
                                    )

                                    if res2.status_code == 200:
                                        st.success(
                                            "¡Contraseña actualizada!"
                                        )

                                        st.session_state.paso_rec_cli = (
                                            "correo"
                                        )
                                        st.session_state.pop(
                                            "mail_cli",
                                            None,
                                        )
                                        st.rerun()
                                    else:
                                        mostrar_error(
                                            res2,
                                            "No se pudo actualizar la contraseña.",
                                        )

                                except requests.RequestException as e:
                                    st.error(f"Error de conexión: {e}")
                            else:
                                st.warning(
                                    "Completa todos los campos."
                                )

                        if btn_can:
                            st.session_state.paso_rec_cli = "correo"
                            st.session_state.pop("mail_cli", None)
                            st.rerun()

        # ========================================================
        # PROPIETARIO
        # ========================================================
        with tab_propietario:
            accion_propietario = st.selectbox(
                "Acción Propietario",
                [
                    "Iniciar Sesión",
                    "Registrarse",
                    "Olvide Contraseña",
                ],
                key="menu_prop",
                label_visibility="collapsed",
            )

            # ------------------------------------------------
            # PROPIETARIO - INICIAR SESIÓN
            # ------------------------------------------------
            if accion_propietario == "Iniciar Sesión":
                st.markdown(
                    '<div class="titulo-propietario">🔐 Iniciar Sesión - Propietario</div>',
                    unsafe_allow_html=True,
                )

                with st.form("form_login_prop"):
                    _, col_input, _ = st.columns([0.2, 2.6, 0.2])

                    with col_input:
                        email_prop = campo_texto(
                            "Correo electrónico",
                            "login_prop_email",
                            AZUL,
                            placeholder="Ingrese su correo electrónico",
                        )

                        password_prop = campo_texto(
                            "Contraseña",
                            "login_prop_pass",
                            AZUL,
                            tipo="password",
                            placeholder="Ingrese su contraseña",
                        )

                        submit_prop = st.form_submit_button(
                            "Ingresar como Propietario",
                            use_container_width=True,
                        )

                    if submit_prop:
                        if email_prop and password_prop:
                            try:
                                payload_login_prop = {
                                    "correo": email_prop.strip().lower(),
                                    "contrasena": password_prop,
                                }

                                r = requests.post(
                                    f"{API_URL}/auth/login",
                                    json=payload_login_prop,
                                    timeout=5,
                                )

                                if r.status_code == 200:
                                    data = r.json()

                                    st.session_state.logged_in = True

                                    id_encontrado = (
                                        data.get("propietario_id")
                                        or data.get("id")
                                        or data.get("usuario_id")
                                    )

                                    st.session_state.user_id = id_encontrado
                                    st.session_state.propietario_id = (
                                        id_encontrado
                                    )

                                    rol_recibido = data.get("rol")

                                    if rol_recibido in [
                                        "super_admin",
                                        "superadmin",
                                    ]:
                                        st.session_state.user_role = (
                                            "superadmin"
                                        )
                                    else:
                                        st.session_state.user_role = (
                                            "propietario"
                                        )

                                    st.session_state.user_name = data.get(
                                        "nombre"
                                    )

                                    st.session_state.user_negocio = (
                                        data.get("nombre_comercial")
                                        or "Mi Establecimiento"
                                    )

                                    st.session_state.tipo_negocio = data.get(
                                        "tipo_negocio",
                                        "Salsoteca",
                                    )

                                    st.session_state.token = data.get(
                                        "access_token"
                                    )

                                    st.success(
                                        f"¡Bienvenido, {data.get('nombre')}!"
                                    )
                                    st.rerun()

                                else:
                                    mostrar_error(
                                        r,
                                        "Credenciales incorrectas.",
                                    )

                            except requests.RequestException as e:
                                st.error(
                                    f"Error de conexión: {e}"
                                )
                        else:
                            st.warning("Completa todos los campos.")

            # ------------------------------------------------
            # PROPIETARIO - REGISTRO
            # ------------------------------------------------
            elif accion_propietario == "Registrarse":
                st.markdown(
                    '<div class="titulo-propietario">📝 Registro - Nuevo Propietario</div>',
                    unsafe_allow_html=True,
                )

                with st.form("form_registro_propietario"):
                    _, col_input, _ = st.columns([0.2, 2.6, 0.2])

                    with col_input:
                        reg_negocio = campo_texto(
                            "Nombre del Local / Negocio",
                            "reg_prop_negocio",
                            AZUL,
                            placeholder="Nombre comercial del negocio",
                        )

                        etiqueta(
                            "Tipo de Establecimiento",
                            AZUL,
                        )

                        reg_tipo_negocio = st.selectbox(
                            "Tipo de Establecimiento",
                            [
                                "Salsoteca",
                                "Discoteca",
                                "Restaurante",
                                "Resto Bar",
                                "Bar",
                                "Karaoke",
                                "Lounge",
                            ],
                            key="reg_prop_tipo",
                            label_visibility="collapsed",
                        )

                        nombre_prop = campo_texto(
                            "Nombre del Propietario",
                            "reg_prop_nombre",
                            AZUL,
                            placeholder="Nombre completo",
                        )

                        email_prop = campo_texto(
                            "Correo electrónico",
                            "reg_prop_email",
                            AZUL,
                            placeholder="Correo electrónico",
                        )

                        telefono_prop = campo_texto(
                            "Teléfono / Celular",
                            "reg_prop_tel",
                            AZUL,
                            placeholder="Teléfono o celular",
                        )

                        password_prop = campo_texto(
                            "Contraseña",
                            "reg_prop_pass",
                            AZUL,
                            tipo="password",
                            placeholder="Cree una contraseña",
                        )

                        reg_ruc_prop = campo_texto(
                            "RUC / Identificación Fiscal",
                            "reg_prop_ruc",
                            AZUL,
                            placeholder="RUC o identificación fiscal",
                        )

                        submit_reg_prop = st.form_submit_button(
                            "Registrarse como Propietario",
                            use_container_width=True,
                        )

                    if submit_reg_prop:
                        if (
                            nombre_prop
                            and email_prop
                            and password_prop
                            and reg_negocio
                        ):
                            try:
                                payload = {
                                    "nombre_comercial": reg_negocio,
                                    "tipo_negocio": reg_tipo_negocio,
                                    "nombre": nombre_prop,
                                    "correo": email_prop.strip().lower(),
                                    "contrasena": password_prop,
                                    "telefono": telefono_prop,
                                    "ruc": reg_ruc_prop,
                                }

                                r = requests.post(
                                    f"{API_URL}/auth/registro",
                                    json=payload,
                                    timeout=5,
                                )

                                if r.status_code == 200:
                                    st.success(
                                        "¡Negocio registrado con éxito! "
                                        "Ya puedes iniciar sesión."
                                    )
                                else:
                                    mostrar_error(
                                        r,
                                        "Error en el registro.",
                                    )

                            except requests.RequestException as e:
                                st.error(
                                    f"Error de conexión: {e}"
                                )
                        else:
                            st.warning(
                                "Por favor completa los campos obligatorios."
                            )

            # ------------------------------------------------
            # PROPIETARIO - RECUPERAR CONTRASEÑA
            # ------------------------------------------------
            elif accion_propietario == "Olvide Contraseña":
                st.markdown(
                    '<div class="titulo-propietario">🔄 Recuperar Acceso - Propietario</div>',
                    unsafe_allow_html=True,
                )

                if "paso_recuperacion_prop" not in st.session_state:
                    st.session_state.paso_recuperacion_prop = (
                        "solicitar_correo"
                    )

                if (
                    st.session_state.paso_recuperacion_prop
                    == "solicitar_correo"
                ):
                    with st.form("form_rec_prop"):
                        _, col_input, _ = st.columns(
                            [0.2, 2.6, 0.2]
                        )

                        with col_input:
                            rec_email_p = campo_texto(
                                "Correo electrónico registrado",
                                "rec_email_prop_input",
                                AZUL,
                                placeholder="Correo registrado",
                            )

                            btn_enviar_p = st.form_submit_button(
                                "Enviar Código OTP",
                                use_container_width=True,
                            )

                        if btn_enviar_p:
                            if rec_email_p:
                                try:
                                    res = requests.post(
                                        f"{API_URL}/auth-recuperacion/solicitar-codigo",
                                        json={
                                            "email": rec_email_p.strip().lower()
                                        },
                                        timeout=5,
                                    )

                                    if res.status_code == 200:
                                        st.success(
                                            "¡Código enviado! "
                                            "Revisa tu correo o consola."
                                        )

                                        st.session_state.email_recuperando_prop = (
                                            rec_email_p.strip().lower()
                                        )

                                        st.session_state.paso_recuperacion_prop = (
                                            "ingresar_codigo"
                                        )

                                        st.rerun()

                                    else:
                                        mostrar_error(
                                            res,
                                            "Error al solicitar código.",
                                        )

                                except requests.RequestException as e:
                                    st.error(
                                        f"Error de conexión: {e}"
                                    )
                            else:
                                st.warning("Ingresa un correo.")

                elif (
                    st.session_state.paso_recuperacion_prop
                    == "ingresar_codigo"
                ):
                    st.info(
                        "Código enviado a: "
                        f"**{st.session_state.get('email_recuperando_prop')}**"
                    )

                    with st.form("form_code_prop"):
                        _, col_input, _ = st.columns(
                            [0.2, 2.6, 0.2]
                        )

                        with col_input:
                            codigo_p = campo_texto(
                                "Código de 6 dígitos",
                                "rec_cod_prop",
                                AZUL,
                                placeholder="Ingrese el código OTP",
                            )

                            nueva_pass_p = campo_texto(
                                "Nueva Contraseña",
                                "rec_np_prop",
                                AZUL,
                                tipo="password",
                                placeholder="Ingrese su nueva contraseña",
                            )

                            col1, col2 = st.columns(2)

                            with col1:
                                btn_act_p = st.form_submit_button(
                                    "Actualizar",
                                    use_container_width=True,
                                )

                            with col2:
                                btn_can_p = st.form_submit_button(
                                    "Cancelar",
                                    use_container_width=True,
                                )

                        if btn_act_p:
                            if codigo_p and nueva_pass_p:
                                try:
                                    payload = {
                                        "email": st.session_state.email_recuperando_prop,
                                        "codigo": codigo_p.strip(),
                                        "nueva_password": nueva_pass_p,
                                    }

                                    res2 = requests.post(
                                        f"{API_URL}/auth-recuperacion/cambiar-password",
                                        json=payload,
                                        timeout=5,
                                    )

                                    if res2.status_code == 200:
                                        st.success(
                                            "¡Contraseña actualizada con éxito!"
                                        )

                                        st.session_state.paso_recuperacion_prop = (
                                            "solicitar_correo"
                                        )

                                        st.session_state.pop(
                                            "email_recuperando_prop",
                                            None,
                                        )

                                        st.rerun()

                                    else:
                                        mostrar_error(
                                            res2,
                                            "No se pudo actualizar la contraseña.",
                                        )

                                except requests.RequestException as e:
                                    st.error(
                                        f"Error de conexión: {e}"
                                    )
                            else:
                                st.warning(
                                    "Completa todos los campos."
                                )

                        if btn_can_p:
                            st.session_state.paso_recuperacion_prop = (
                                "solicitar_correo"
                            )

                            st.session_state.pop(
                                "email_recuperando_prop",
                                None,
                            )

                            st.rerun()
