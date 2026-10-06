import configparser
import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)
import requests
import streamlit as st


from app.frontend.home import render_home
from app.frontend.home_propietario import render_home_propietario
from app.frontend.login_cliente import render_login_cliente

from app.frontend.admin_panel import render_admin_panel
from app.frontend.agenda_propietario import render_agenda_propietario
from app.frontend.asignar_mesas import render_asignar_mesas
from app.frontend.bienvenida import render_bienvenida
from app.frontend.cartelera import render_cartelera as render_catalogo_clientes
from app.frontend.clientefinal_reservas import render_mis_reservas
from app.frontend.mapa_mesas import render_mapa_mesas
from app.frontend.configuracion_notificaciones import (
    render_configuracion_notificaciones,

)
from app.frontend.control_puerta import render_control_puerta
from app.frontend.control_reservas import render_control_reservas
from app.frontend.crear_eventos import render_crear_eventos
from app.frontend.crear_mesas import render_crear_mesas
from app.frontend.crear_reserva_personalizada import ( 
    render_crear_reserva_personalizada,
)
from app.frontend.crear_zonas import render_crear_zonas
from app.frontend.historial_asistencia import render_historial_asistencia
from app.frontend.mantenimiento import render_mantenimiento
from app.frontend.mini_web import render_mini_web_vip
from app.frontend.pie_pagina import render_pie_pagina
from app.frontend.reserva_mesa import render_seleccion_mesas
from app.frontend.truco_java import configurar_puente_html
from app.frontend.validaciones_cliente import render_mantenimiento_cliente
from app.frontend.filtro_locales import render_filtro_locales
from app.frontend.registro_clientes import render_registro_clientes
from app.frontend.recuperar_contrasena import render_recuperar_contrasena


# Configuración PWA mediante inyección segura de texto plano
pwa_html = chr(60) + 'link rel="manifest" href="/static/manifest.json"' + chr(62)
pwa_html += chr(60) + 'meta name="theme-color" content="#050612"' + chr(62)
pwa_html += chr(60) + 'meta name="apple-mobile-web-app-capable" content="yes"' + chr(62)
pwa_html += chr(60) + 'script' + chr(62) + "if('serviceWorker' in navigator){navigator.serviceWorker.register('/static/sw.js');}" + chr(60) + '/script' + chr(62)


st.markdown(pwa_html, unsafe_allow_html=True)

#try:
#  from app.frontend.filtro_cartelera import render_sidebar_filtros
#except ImportError:
#  from filtro_cartelera import render_sidebar_filtros

configurar_puente_html()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


st.set_page_config(page_title="Bookea - Sistema de Reservas", layout="wide")

st.markdown(   """
<style>
            
/* ============================================================
   BOOKEA — ESTILOS GLOBALES Y CORRECCIÓN DE CONTRASTE
   ============================================================ */

/* Cabecera nativa de Streamlit */
header[data-testid="stHeader"] {
    display: none !important;
    height: 0 !important;
    min-height: 0 !important;
    visibility: hidden !important;
}

/* Contenedor principal */
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main,
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.block-container {
    padding-top: -8rem !important;
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

/* ============================================================
   CORRECCIÓN DEFINITIVA DE BOTONES Y POPOVERS (FONDO OSCURO Y TEXTO BLANCO)
   ============================================================ */

/* Botones estándar y de tipo popover / enlace */
[data-testid="stButton"] > button,
[data-testid="stPopover"] > button,
button[data-baseweb="button"] {
    background-color: #141625 !important;
    background-image: none !important;
    color: #ffffff !important;
    border: 1px solid rgba(150, 55, 255, 0.35) !important;
}

/* Estado Hover / Focus / Active para botones y popovers */
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

/* Forzar que el texto y los iconos dentro de los botones sean siempre blancos */
[data-testid="stButton"] > button p,
[data-testid="stPopover"] > button p,
[data-testid="stPopover"] > button span {
    color: #ffffff !important;
}

/* Selectores desplegables */
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background-color: #141625 !important;
    color: #ffffff !important;
    border: 1px solid rgba(150, 55, 255, 0.35) !important;
}

div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover {
    background-color: #1f2238 !important;
    border-color: #00cfff !important;
}

/* Opciones de los menús desplegables */
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
</style>
""",
    unsafe_allow_html=True,
)


# --- 1. INICIALIZACIÓN DE ESTADOS DE SESIÓN Y URL ---
query_params = st.query_params

if "logged_in" not in st.session_state:
  # Intentar recuperar sesión si viene en URL
  st.session_state.logged_in = (
      True if query_params.get("logged") == "true" else False
  )
if "user_role" not in st.session_state:
  st.session_state.user_role = query_params.get("role", None)

if "origen_bienvenida" in st.session_state:
  st.session_state.menu_acceso = st.session_state.origen_bienvenida
  if st.session_state.origen_bienvenida == "Acceso Cliente":
    st.session_state.modo_cliente = "Registrarse"
  del st.session_state.origen_bienvenida
  st.rerun()

if st.session_state.get("redirigir_a_agenda", False):
  st.session_state.menu_propietario_actual = "Agenda de Eventos"
  st.session_state.redirigir_a_agenda = False
  st.rerun()

# --- INTERCEPTOR DE SLUG VIP ---
slug_vip = query_params.get("local_vip") or query_params.get("local")
if slug_vip:
    st.session_state.local_actual = slug_vip
    if not st.session_state.get("logged_in", False):
        encontrado = render_mini_web_vip(API_URL, slug_vip)
        if encontrado:
            st.stop()
        else:
            st.error(f"⚠️ El establecimiento '{slug_vip}' no se encuentra disponible.")
            st.stop()

# --- VISTA PÚBLICA (NO LOGUEADO) ---
if not st.session_state.get("logged_in", False):
    vista_publica = st.session_state.get("vista_actual_publica", "home")

    if vista_publica == "login_cliente":
        render_login_cliente(API_URL)
    elif vista_publica == "registro_clientes":
        render_registro_clientes(API_URL)     
    elif vista_publica == "recuperar_contrasena":
        render_recuperar_contrasena(API_URL)
    elif vista_publica == "home_propietario":               
        render_home_propietario(API_URL)                      
    else:
        render_home(API_URL)
        
    render_pie_pagina()
    st.stop()

# ============================================================
# ZONA LOGUEADA: EVALUACIÓN ÚNICA Y ESTRICTA DE ROLES
# ============================================================
rol_actual = str(st.session_state.get("user_role", "propietario")).strip().lower()
if not rol_actual or rol_actual == "none":
    rol_actual = "propietario"

# --- ROL: SUPERADMIN ---
if rol_actual == "superadmin":
    st.markdown("##### 🛠️ Panel Global - SuperAdmin")
    if "menu_superadmin_actual" not in st.session_state:
        st.session_state.menu_superadmin_actual = "Panel Global"

    opcion_sa = st.selectbox("Navegación Principal:", ["Panel Global", "Cerrar Sesión"], key="menu_superadmin_actual")
    if opcion_sa == "Cerrar Sesión":
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.query_params.clear()
        st.rerun()
    else:
        render_admin_panel(API_URL)
        render_pie_pagina()
        st.stop()

# --- ROL: PROPIETARIO ---
elif rol_actual == "propietario":
    user_id = st.session_state.get("user_id") or st.session_state.get("propietario_id") or st.session_state.get("id")
    local_id_actual = st.query_params.get("local_id") or st.session_state.get("local_id_actual") or 1

    locales_propietario = []
    try:
        if user_id:
            res_api = requests.get(f"{API_URL}/locales/?propietario_id={user_id}")
            if res_api.status_code != 200:
                res_api = requests.get(f"{API_URL}/locales/usuario/{user_id}", timeout=5)
            if res_api.status_code == 200:
                data_locales = res_api.json()
                locales_propietario = data_locales if isinstance(data_locales, list) else [data_locales]
    except Exception:
        locales_propietario = []

    opciones_locales = {}
    for loc in locales_propietario:
        lid = loc.get("id") or loc.get("local_id") or 1
        nombre = loc.get("nombre", loc.get("nombre_local", "Local"))
        opciones_locales[f"ID {lid} - {nombre}"] = lid

    vistas_mapeo = {
        "Agenda de Eventos": render_agenda_propietario,
        "Crear Eventos": render_crear_eventos,
        "Crear Zonas": render_crear_zonas,
        "Crear Mesas": render_crear_mesas,
        "Asignar Mesas": render_asignar_mesas,
        "Control de Reservas": render_control_reservas,
        "Control de Puerta": render_control_puerta,
        "Mapa de Mesas": render_mapa_mesas,
        "Historial de Asistencia": render_historial_asistencia,
        "Mantenimiento": render_mantenimiento,
    }

    opciones_menu = list(vistas_mapeo.keys()) + ["🚪 Cerrar Sesión"]
    opcion_seleccionada = st.selectbox("📌 Menú de Gestión", opciones_menu, key="menu_propietario_activo")

    if opcion_seleccionada == "🚪 Cerrar Sesión":
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.query_params.clear()
        st.rerun()

    vistas_mapeo.get(opcion_seleccionada, render_agenda_propietario)(API_URL)
    render_pie_pagina()
    st.stop()

# --- ROL: CLIENTE ---
elif rol_actual == "cliente":
    nombre_usuario = st.session_state.get("user_name", "Cliente")

    col_esp_izq, col_centro_cliente, col_esp_der = st.columns([1, 2.5, 1])
    with col_centro_cliente:
        st.markdown(f"👋 Hola, {nombre_usuario} 🌟 Bookea Tu Evento", unsafe_allow_html=True)

    opciones_cliente = [
        "Catálogo de Eventos",
        "🔍 Buscar Locales",
        "Mis Reservas",
        "Actualizar Datos",
        "Cerrar Sesión",
    ]

    opcion = st.selectbox("Mi Cuenta", opciones_cliente, label_visibility="collapsed", key="menu_cliente_principal")

    if opcion == "Cerrar Sesión":
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.query_params.clear()
        st.rerun()

    if opcion == "Catálogo de Eventos":
        if "paso_reserva" not in st.session_state:
            st.session_state.paso_reserva = "catalogo"

        if st.session_state.paso_reserva == "catalogo":
            render_catalogo_clientes(API_URL)
        elif st.session_state.paso_reserva == "seleccionar_mesa":
            if st.button("⬅️ Volver a la cartelera"):
                st.session_state.paso_reserva = "catalogo"
                st.rerun()
            render_seleccion_mesas(API_URL, st.session_state.get("evento_a_reservar"), st.session_state.get("user_id"))
        st.stop()

    elif opcion == "🔍 Buscar Locales":
        render_filtro_locales(API_URL)
        st.stop()
    elif opcion == "Mis Reservas":
        render_mis_reservas(API_URL, st.session_state.get("user_id"))
        st.stop()
    elif opcion == "Actualizar Datos":
        render_mantenimiento_cliente(API_URL)
        st.stop()

render_pie_pagina()
st.stop()