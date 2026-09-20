import streamlit as st
import requests

from cartelera import render_cartelera as render_catalogo_clientes
from reserva_mesa import render_seleccion_mesas

def render_mis_reservas_activas(api_url, cliente_id, evento_id=None):
    """Muestra las reservas activas del cliente para recordar cuántas mesas lleva."""
    try:
        url = f"{api_url}/reservas/cliente/{cliente_id}"
        if evento_id:
            url += f"/evento/{evento_id}"
            
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            reservas = res.json()
            if reservas:
                st.markdown("### 🎟️ Tus Reservas Activas para este Evento")
                
                total_mesas = len(reservas)
                total_personas = sum(r.get("cantidad_personas", 0) for r in reservas)
                total_valor = sum(r.get("valor_reserva", 0.0) for r in reservas)
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Mesas Apartadas", total_mesas)
                col2.metric("Total Personas", total_personas)
                col3.metric("Valor Acumulado", f"${total_valor:.2f}")
                
                with st.expander("Ver detalles de tus mesas reservadas"):
                    for r in reservas:
                        st.markdown(f"- **Mesa #{r.get('numero_mesa', 'N/A')}** | Personas: {r.get('cantidad_personas', 0)} | Estado: 🟢 {r.get('estado', 'Confirmada')}")
                st.markdown("---")
    except Exception:
        pass


def render_mini_web_vip(api_url, slug_vip):
    """Controla y renderiza toda la mini web VIP del establecimiento según su slug."""
    try:
        res = requests.get(f"{api_url}/auth/vip/por-slug/{slug_vip}")
        if res.status_code == 200:
            vip_data = res.json()
            
            # --- ESTILOS CSS PERSONALIZADOS ---
            st.markdown("""
                <style>
                .vip-hero {
                    background: linear-gradient(135deg, #1e1e2f 0%, #3a3a5a 100%);
                    color: white;
                    padding: 35px 20px;
                    border-radius: 16px;
                    text-align: center;
                    margin-bottom: 25px;
                    box-shadow: 0px 8px 20px rgba(0,0,0,0.2);
                }
                .vip-hero h1 {
                    color: #ffffff !important;
                    font-size: 2.4rem;
                    font-weight: 700;
                    margin-bottom: 5px;
                }
                .vip-badge {
                    background-color: #ff4b4b;
                    color: white;
                    font-size: 12px;
                    padding: 4px 12px;
                    border-radius: 12px;
                    font-weight: bold;
                    display: inline-block;
                    margin-bottom: 10px;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }
                .vip-subtitle {
                    color: #d0d0e0;
                    font-size: 1.1rem;
                }
                </style>
            """, unsafe_allow_html=True)

            # --- MENÚ SUPERIOR DINÁMICO (DERECHA) ---
            col_vacio, col_info_cli = st.columns([0.6, 0.4])
            with col_info_cli:
                if st.session_state.get("logged_in", False) and st.session_state.get("user_role") == "cliente":
                    nombre_cliente = st.session_state.get("user_name", "Cliente")
                    st.markdown(f"👋 Hola, **{nombre_cliente}**")
                    if st.button("🚪 Cerrar Sesión", use_container_width=True):
                        st.session_state.logged_in = False
                        st.session_state.user_role = None
                        st.session_state.user_name = None
                        st.session_state.user_id = None
                        st.rerun()
                else:
                    if st.button("👥 Acceso Cliente", use_container_width=True):
                        st.session_state.temp_vista_vip = "Acceso Cliente"
                        st.rerun()
            
            st.markdown("---")
            
            # --- CONTROLADOR DE VISTAS DE LA MINI WEB ---
            vista_actual = st.session_state.get("temp_vista_vip", "Vista Principal / Eventos")
            
            # 1. VISTA PRINCIPAL (CARTELERA VIP)
            if vista_actual == "Vista Principal / Eventos":
                st.markdown(f"""
                    <div class="vip-hero">
                        <span class="vip-badge">⭐ ESTABLECIMIENTO VIP</span>
                        <h1>{vip_data['nombre']}</h1>
                        <p class="vip-subtitle">Tipo de local: <b>{vip_data.get('tipo_negocio', 'Entretenimiento & Eventos')}</b> | Reservas en Línea</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # --- MÉTRICAS DE COMUNIDAD ---
                col_m1, col_m2, col_m3 = st.columns(3)
                
                total_clientes_local = vip_data.get('total_clientes_registrados', 124)
                likes_count = vip_data.get('likes', 48)
                dislikes_count = vip_data.get('dislikes', 2)
                
                col_m1.metric("👥 Clientes Registrados", total_clientes_local)
                
                with col_m2:
                    st.markdown("**¿Te gusta este local?**")
                    c_like, c_dislike = st.columns(2)
                    if c_like.button(f"👍 {likes_count}", key="btn_like_vip"):
                        st.success("¡Gracias por tu recomendación!")
                    if c_dislike.button(f"👎 {dislikes_count}", key="btn_dislike_vip"):
                        st.toast("Gracias por tus comentarios de mejora.")

                col_m3.metric("⭐ Valoración", "4.9 / 5.0")
                st.markdown("---")
                
                st.subheader("📅 Próximos Eventos")
                
                if st.session_state.get("logged_in", False) and st.session_state.get("user_role") == "cliente":
                    cliente_id = st.session_state.get("user_id")
                    
                    if "paso_reserva" not in st.session_state:
                        st.session_state.paso_reserva = "catalogo"

                    if st.session_state.paso_reserva == "catalogo":
                        evento_activo_id = st.session_state.get("evento_a_reservar")
                        if evento_activo_id:
                            render_mis_reservas_activas(api_url, cliente_id, evento_activo_id)
                        render_catalogo_clientes(api_url)
                        
                    elif st.session_state.paso_reserva == "seleccionar_mesa":
                        if st.button("⬅️ Volver a la cartelera"):
                            st.session_state.paso_reserva = "catalogo"
                            st.rerun()
                            
                        evento_id = st.session_state.evento_a_reservar
                        render_mis_reservas_activas(api_url, cliente_id, evento_id)
                        render_seleccion_mesas(api_url, evento_id, cliente_id)
                else:
                    st.info("💡 Inicia sesión en **Acceso Cliente** (arriba a la derecha) para poder reservar tus mesas.")
                    render_catalogo_clientes(api_url)

            # 2. ACCESO CLIENTES DENTRO DE LA MINI WEB
            elif vista_actual == "Acceso Cliente":
                col_title, col_back = st.columns([0.8, 0.2])
                with col_title:
                    st.markdown("### 🎟️ Acceso / Registro de Clientes")
                with col_back:
                    if st.button("⬅️ Volver", key="back_cli"):
                        st.session_state.temp_vista_vip = "Vista Principal / Eventos"
                        st.rerun()

                tab_login, tab_registro = st.tabs(["Iniciar Sesión", "Registrarse"])
                
                with tab_login:
                    with st.form("form_login_vip_cli"):
                        cli_email = st.text_input("Correo Electrónico")
                        cli_pass = st.text_input("Contraseña", type="password")
                        cli_submit = st.form_submit_button("Ingresar")
                        
                        if cli_submit:
                            try:
                                res = requests.post(f"{api_url}/clientes-auth/login", json={"email": cli_email, "password": cli_pass})
                                if res.status_code == 200:
                                    data_cli = res.json()
                                    st.session_state.logged_in = True
                                    st.session_state.user_role = "cliente"
                                    st.session_state.user_name = data_cli.get("nombre")
                                    st.session_state.user_id = data_cli.get("id")
                                    st.session_state.temp_vista_vip = "Vista Principal / Eventos"
                                    st.success(f"¡Bienvenido, {data_cli.get('nombre')}!")
                                    st.rerun()
                                else:
                                    st.error("Correo o contraseña incorrectos.")
                            except Exception as e:
                                st.error(f"Error de conexión: {e}")
                                
                with tab_registro:
                    with st.form("form_reg_vip_cli"):
                        reg_nombre = st.text_input("Nombre Completo")
                        reg_email = st.text_input("Correo Electrónico")
                        reg_pass = st.text_input("Contraseña", type="password")
                        reg_tel = st.text_input("Teléfono / WhatsApp")
                        reg_submit = st.form_submit_button("Crear Cuenta")

                    if reg_submit:
                        if reg_nombre and reg_email and reg_pass and reg_tel:
                            try:
                                payload = {
                                    "nombre": reg_nombre,
                                    "email": reg_email,
                                    "password": reg_pass,
                                    "telefono": reg_tel
                                }
                                res = requests.post(f"{api_url}/clientes-auth/registro", json=payload, timeout=5)
                                if res.status_code == 200:
                                    st.success("¡Cuenta creada con éxito! Ya puedes iniciar sesión.")
                                else:
                                    try:
                                        error_detalle = res.json().get("detail", "Error desconocido")
                                    except Exception:
                                        error_detalle = res.text
                                    st.error(f"No se pudo registrar: {error_detalle}")
                            except Exception as e:
                                st.error(f"Ocurrió un error: {e}")
                        else:
                            st.warning("Por favor completa todos los campos.")

            return True
        else:
            return False
    except Exception as e:
        st.error(f"Error al conectar con el servidor para cargar el local VIP: {e}")
        return False