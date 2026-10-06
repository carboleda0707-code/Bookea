import streamlit as st


def render_home_propietario(api_url):
    """
    Landing pública para propietarios de Bookea.
    No modifica la lógica de reservas ni la agenda existente.

    Flujo:
    - Inicio de sesión -> vista pública login
    - Registrarse -> vista pública de registro
    - Olvidé mi contraseña -> recuperación
    """

    # ============================================================
    # BOOKEA PROPIETARIOS — LANDING RESPONSIVE
    # ============================================================
    st.markdown("""
    <style>
    /* ---------- CONTENEDOR GENERAL ---------- */
    .block-container {
        padding-top: 3.25rem !important;
        padding-bottom: 1.5rem !important;
        max-width: 1180px !important;
    }

    .bp-page {
        width: 100%;
        max-width: 980px;
        margin: 0 auto;
        color: #f7f7ff;
        font-family: Inter, "Segoe UI", Arial, sans-serif;
    }

    /* ---------- BARRA SUPERIOR ---------- */
    .bp-topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        width: 100%;
        min-height: 48px;
        margin-bottom: 8px;
        padding: 4px 2px;
    }

    .bp-brand {
        display: flex;
        align-items: center;
        gap: 9px;
        font-weight: 800;
        font-size: 20px;
        letter-spacing: -0.4px;
    }

    .bp-logo {
        width: 34px;
        height: 34px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #00cfff, #9637ff);
        color: #ffffff;
        font-size: 17px;
        box-shadow: 0 5px 18px rgba(0, 207, 255, 0.18);
    }

    .bp-brand-text span {
        color: #00cfff;
    }

    .bp-owner-label {
        color: #9ea2b5;
        font-size: 11px;
        font-weight: 500;
        margin-top: 1px;
    }

    /* ---------- HERO ---------- */
    .bp-hero {
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(0, 207, 255, 0.15);
        border-radius: 22px;
        padding: 42px 28px 34px;
        background:
            radial-gradient(circle at 80% 10%, rgba(150,55,255,.18), transparent 35%),
            radial-gradient(circle at 10% 90%, rgba(0,207,255,.12), transparent 35%),
            linear-gradient(145deg, #0b0d1a, #101326 55%, #0a0b15);
        box-shadow: 0 18px 55px rgba(0,0,0,.28);
        text-align: center;
    }

    .bp-kicker {
        display: inline-block;
        padding: 6px 11px;
        border-radius: 999px;
        border: 1px solid rgba(0,207,255,.25);
        background: rgba(0,207,255,.07);
        color: #67ddff;
        font-size: 11px;
        font-weight: 700;
        margin-bottom: 15px;
    }

    .bp-hero h1 {
        margin: 0 auto 12px;
        max-width: 760px;
        color: #ffffff;
        font-size: clamp(28px, 5vw, 48px);
        line-height: 1.08;
        letter-spacing: -1.4px;
    }

    .bp-hero h1 span {
        background: linear-gradient(90deg, #00cfff, #a66bff);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }

    .bp-hero p {
        max-width: 680px;
        margin: 0 auto;
        color: #b9bdcc;
        font-size: 15px;
        line-height: 1.6;
    }

    /* ---------- BLOQUE DE VALOR ---------- */
    .bp-section-title {
        text-align: center;
        margin: 27px 0 14px;
    }

    .bp-section-title h2 {
        margin: 0 0 5px;
        color: #ffffff;
        font-size: 21px;
    }

    .bp-section-title p {
        margin: 0;
        color: #85899d;
        font-size: 12px;
    }

    .bp-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
    }

    .bp-card {
        min-height: 145px;
        padding: 18px 15px;
        border-radius: 15px;
        border: 1px solid rgba(150,55,255,.17);
        background: rgba(18, 20, 34, .82);
    }

    .bp-card-icon {
        font-size: 23px;
        margin-bottom: 9px;
    }

    .bp-card h3 {
        margin: 0 0 6px;
        color: #ffffff;
        font-size: 14px;
    }

    .bp-card p {
        margin: 0;
        color: #9297aa;
        font-size: 11.5px;
        line-height: 1.55;
    }

    /* ---------- COMO FUNCIONA ---------- */
    .bp-steps {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        margin-top: 12px;
    }

    .bp-step {
        display: flex;
        gap: 10px;
        align-items: flex-start;
        padding: 14px;
        border-radius: 13px;
        background: rgba(255,255,255,.025);
        border: 1px solid rgba(255,255,255,.06);
    }

    .bp-number {
        flex: 0 0 25px;
        width: 25px;
        height: 25px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(0,207,255,.12);
        border: 1px solid rgba(0,207,255,.28);
        color: #00cfff;
        font-size: 11px;
        font-weight: 800;
    }

    .bp-step strong {
        display: block;
        color: #ffffff;
        font-size: 12px;
        margin-bottom: 3px;
    }

    .bp-step span {
        color: #85899d;
        font-size: 10.5px;
        line-height: 1.45;
    }

    /* ---------- CTA ---------- */
    .bp-cta {
        margin-top: 26px;
        padding: 23px 18px;
        text-align: center;
        border-radius: 18px;
        border: 1px solid rgba(0,207,255,.18);
        background: linear-gradient(135deg, rgba(0,207,255,.07), rgba(150,55,255,.09));
    }

    .bp-cta h2 {
        margin: 0 0 6px;
        font-size: 20px;
        color: #ffffff;
    }

    .bp-cta p {
        margin: 0 auto 13px;
        max-width: 580px;
        color: #a7abbb;
        font-size: 12px;
        line-height: 1.5;
    }

    /* ---------- PIE ---------- */
    .bp-footer {
        text-align: center;
        padding: 22px 5px 5px;
        color: #666b7e;
        font-size: 10px;
    }

    .bp-footer b {
        color: #00cfff;
    }

    /* ---------- BOTONES STREAMLIT ---------- */
    .bp-menu-button [data-testid="stPopover"] > button {
        width: 42px !important;
        height: 42px !important;
        min-height: 42px !important;
        border-radius: 50% !important;
        padding: 0 !important;
        background: #111321 !important;
        border: 1px solid rgba(255,255,255,.08) !important;
        color: #ffffff !important;
        box-shadow: none !important;
    }

    .bp-menu-button [data-testid="stPopover"] > button:hover,
    .bp-menu-button [data-testid="stPopover"] > button:focus,
    .bp-menu-button [data-testid="stPopover"] > button:active {
        background: #111321 !important;
        border-color: rgba(0,207,255,.35) !important;
        box-shadow: none !important;
    }

    .bp-menu-button [data-testid="stPopover"] > button p,
    .bp-menu-button [data-testid="stPopover"] > button span {
        color: #ffffff !important;
        font-size: 19px !important;
    }

    .bp-menu-option button {
        width: 100% !important;
        min-height: 38px !important;
        background: #141625 !important;
        color: #ffffff !important;
        border: 1px solid rgba(150,55,255,.20) !important;
        box-shadow: none !important;
    }

    .bp-menu-option button:hover,
    .bp-menu-option button:focus,
    .bp-menu-option button:active {
        background: #1b1e31 !important;
        color: #ffffff !important;
        border-color: rgba(0,207,255,.35) !important;
        box-shadow: none !important;
    }

    .bp-menu-option button p {
        color: #ffffff !important;
        font-size: 12px !important;
    }

    .bp-main-action button {
        width: 100% !important;
        min-height: 42px !important;
        border-radius: 11px !important;
        background: linear-gradient(90deg, #00bfe8, #7c4dff) !important;
        border: none !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        box-shadow: none !important;
    }

    .bp-main-action button:hover,
    .bp-main-action button:focus,
    .bp-main-action button:active {
        background: linear-gradient(90deg, #00bfe8, #7c4dff) !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* ---------- MÓVIL ---------- */
    @media (max-width: 700px) {
        .block-container {
            padding-left: 11px !important;
            padding-right: 11px !important;
            padding-top: 0.15rem !important;
        }

        .bp-topbar {
            min-height: 44px;
            margin-bottom: 5px;
        }

        .bp-brand {
            font-size: 18px;
        }

        .bp-logo {
            width: 31px;
            height: 31px;
            font-size: 15px;
            border-radius: 9px;
        }

        .bp-owner-label {
            font-size: 9px;
        }

        .bp-hero {
            padding: 29px 17px 25px;
            border-radius: 17px;
        }

        .bp-kicker {
            font-size: 9px;
            padding: 5px 9px;
            margin-bottom: 12px;
        }

        .bp-hero h1 {
            font-size: 29px;
            line-height: 1.08;
            letter-spacing: -0.8px;
        }

        .bp-hero p {
            font-size: 12px;
            line-height: 1.55;
        }

        .bp-section-title {
            margin-top: 22px;
        }

        .bp-section-title h2 {
            font-size: 18px;
        }

        .bp-section-title p {
            font-size: 10px;
        }

        .bp-grid {
            grid-template-columns: 1fr;
            gap: 8px;
        }

        .bp-card {
            min-height: auto;
            padding: 14px;
            display: grid;
            grid-template-columns: 34px 1fr;
            column-gap: 8px;
        }

        .bp-card-icon {
            grid-row: 1 / span 2;
            margin: 0;
            font-size: 21px;
        }

        .bp-card h3 {
            font-size: 12.5px;
            margin-bottom: 3px;
        }

        .bp-card p {
            font-size: 10.5px;
        }

        .bp-steps {
            grid-template-columns: 1fr;
            gap: 7px;
        }

        .bp-step {
            padding: 11px;
        }

        .bp-cta {
            margin-top: 20px;
            padding: 19px 14px;
            border-radius: 15px;
        }

        .bp-cta h2 {
            font-size: 17px;
        }

        .bp-cta p {
            font-size: 10.5px;
        }

        .bp-footer {
            font-size: 9px;
            padding-top: 18px;
        }

        .bp-menu-button [data-testid="stPopover"] > button {
            width: 38px !important;
            height: 38px !important;
            min-height: 38px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # ============================================================
    # BARRA SUPERIOR + MENÚ DE 3 PUNTOS
    # ============================================================
    col_brand, col_menu = st.columns([7, 1], vertical_alignment="center")

    with col_brand:
        st.markdown("""
        <div class="bp-topbar">
            <div class="bp-brand">
                <div class="bp-logo">B</div>
                <div>
                    <div class="bp-brand-text">Boo<span>kea</span></div>
                    <div class="bp-owner-label">Soluciones para propietarios</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_menu:
        st.markdown('<div class="bp-menu-button">', unsafe_allow_html=True)
        with st.popover("⋮", use_container_width=True):
            st.markdown(
                "<div style='color:#00cfff;font-size:11px;font-weight:800;"
                "margin-bottom:8px;'>MI CUENTA</div>",
                unsafe_allow_html=True,
            )

            st.markdown('<div class="bp-menu-option">', unsafe_allow_html=True)
            if st.button("🔐 Iniciar sesión", key="bp_menu_login", use_container_width=True):
                st.session_state["vista_actual_publica"] = "login_cliente"
                st.session_state["origen_login"] = "menu_general"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="bp-menu-option">', unsafe_allow_html=True)
            if st.button("✨ Registrarse", key="bp_menu_registro", use_container_width=True):
                st.session_state["vista_actual_publica"] = "registro_clientes"
                st.session_state["origen_bienvenida"] = "Acceso Propietario"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="bp-menu-option">', unsafe_allow_html=True)
            if st.button("🔑 Olvidé mi contraseña", key="bp_menu_recuperar", use_container_width=True):
                st.session_state["vista_actual_publica"] = "recuperar_contrasena"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ============================================================
    # HERO
    # ============================================================
    st.markdown("""
    <div class="bp-page">
        <section class="bp-hero">
            <div class="bp-kicker">BOOKEA PARA PROPIETARIOS</div>
            <h1>Convierte tus reservas en una experiencia <span>más simple.</span></h1>
            <p>
                Gestiona tu establecimiento, eventos, mesas y reservas desde un solo lugar.
                Bookea conecta tu negocio con tus clientes y te ayuda a organizar cada jornada.
            </p>
        </section>

        <div class="bp-section-title">
            <h2>Todo lo que tu negocio necesita</h2>
            <p>Una plataforma pensada para restaurantes, bares, discotecas y establecimientos de entretenimiento.</p>
        </div>

        <section class="bp-grid">
            <article class="bp-card">
                <div class="bp-card-icon">📅</div>
                <h3>Agenda de eventos</h3>
                <p>Organiza tu cartelera y consulta tus eventos de forma rápida y ordenada.</p>
            </article>

            <article class="bp-card">
                <div class="bp-card-icon">🪑</div>
                <h3>Mesas y zonas</h3>
                <p>Administra zonas, mesas y la distribución de tu establecimiento.</p>
            </article>

            <article class="bp-card">
                <div class="bp-card-icon">🎟️</div>
                <h3>Reservaciones</h3>
                <p>Recibe y controla las reservas de tus clientes desde una sola plataforma.</p>
            </article>

            <article class="bp-card">
                <div class="bp-card-icon">🚪</div>
                <h3>Control de acceso</h3>
                <p>Consulta y gestiona la asistencia de tus clientes durante tus eventos.</p>
            </article>

            <article class="bp-card">
                <div class="bp-card-icon">📊</div>
                <h3>Control de tu negocio</h3>
                <p>Ten una visión organizada de tus operaciones y de la actividad de tus reservas.</p>
            </article>

            <article class="bp-card">
                <div class="bp-card-icon">📱</div>
                <h3>Desde cualquier dispositivo</h3>
                <p>Administra tu establecimiento desde PC, tablet o teléfono con una interfaz adaptable.</p>
            </article>
        </section>

        <div class="bp-section-title">
            <h2>¿Cómo funciona?</h2>
            <p>Empieza a gestionar tu negocio en pocos pasos.</p>
        </div>

        <section class="bp-steps">
            <div class="bp-step">
                <div class="bp-number">1</div>
                <div>
                    <strong>Crea tu cuenta</strong>
                    <span>Regístrate como propietario y prepara tu establecimiento.</span>
                </div>
            </div>

            <div class="bp-step">
                <div class="bp-number">2</div>
                <div>
                    <strong>Configura tu negocio</strong>
                    <span>Define eventos, zonas, mesas y la información que verán tus clientes.</span>
                </div>
            </div>

            <div class="bp-step">
                <div class="bp-number">3</div>
                <div>
                    <strong>Empieza a recibir reservas</strong>
                    <span>Consulta y administra la actividad de tus clientes desde Bookea.</span>
                </div>
            </div>
        </section>

        <section class="bp-cta">
            <h2>Tu negocio. Tus reservas. Todo en Bookea.</h2>
            <p>
                Empieza a organizar tu establecimiento con una herramienta diseñada para facilitar
                la gestión diaria y mejorar la experiencia de tus clientes.
            </p>
        </section>

        <div class="bp-footer">
            <b>Bookea</b> · Gestión de reservas para establecimientos
        </div>
    </div>
    """, unsafe_allow_html=True)

    
