import configparser
import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)
import requests
import streamlit as st

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

try:
  from app.frontend.filtro_cartelera import render_sidebar_filtros
except ImportError:
  from filtro_cartelera import render_sidebar_filtros

configurar_puente_html()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


st.set_page_config(page_title="Bookea - Sistema de Reservas", layout="wide")

st.markdown(
    """
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
    padding-top: 0 !important;
    margin-top: 0 !important;
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

# --- INTERCEPTOR DE RUTA / SLUG VIP ---
slug_vip = query_params.get("local_vip") or query_params.get("local")

if not slug_vip:
  try:
    keys = list(query_params.keys())
    if keys:
      posible_slug = keys[0]
      if posible_slug and posible_slug.lower() not in [
          "logged_in",
          "user_role",
          "embed",
          "click_id",
          "logged",
          "role",
          "menu",
          "local_id",
          "evento_id",
          "zona",
      ]:
        slug_vip = posible_slug
  except Exception:
    pass

if slug_vip:
  st.session_state.local_actual = slug_vip

if slug_vip and not st.session_state.get("logged_in", False):
  encontrado = render_mini_web_vip(API_URL, slug_vip)
  if encontrado:
    st.stop()
  else:
    st.error(
        f"⚠️ El establecimiento '{slug_vip}' no se encuentra disponible o no"
        " existe."
    )
    st.stop()


# --- 2. VISTA DE BIENVENIDA (NO LOGEADO) ---
if not st.session_state.get("logged_in", False):
  render_bienvenida(API_URL)

else:
  # ============================================================
  # BOOKEA — CORRECCIÓN VISUAL SOLO PARA USUARIOS LOGUEADOS
  # ============================================================
  st.markdown(
      """
    <style>
    [data-testid="stButton"] > button,
    [data-testid="stButton"] > button:hover,
    [data-testid="stButton"] > button:focus,
    [data-testid="stButton"] > button:focus-visible,
    [data-testid="stButton"] > button:active {
        background-color: #080912 !important;
        background: #080912 !important;
        box-shadow: none !important;
    }
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover,
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus,
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div:active {
        background-color: #080912 !important;
        background: #080912 !important;
        box-shadow: none !important;
    }
    div[role="listbox"] li[role="option"]:hover,
    div[role="listbox"] li[role="option"]:focus,
    div[role="listbox"] li[role="option"][aria-selected="true"] {
        background-color: #20232d !important;
        color: #ffffff !important;
        box-shadow: none !important;
    }
    </style>
    """,
      unsafe_allow_html=True,
  )

  rol_actual = st.session_state.get("user_role", "propietario")

  # ==========================================
  # --- ROL: SUPERADMIN ---
  # ==========================================
  if rol_actual == "superadmin":
    st.markdown("### 🛠️ Panel Global - SuperAdmin")

    if "menu_superadmin_actual" not in st.session_state:
      st.session_state.menu_superadmin_actual = "Panel Global"

    opciones_superadmin = ["Panel Global", "Cerrar Sesión"]

    opcion_sa = st.selectbox(
        "Navegación Principal:",
        opciones_superadmin,
        key="menu_superadmin_actual",
    )

    if opcion_sa == "Cerrar Sesión":
      st.session_state.logged_in = False
      st.session_state.user_role = None
      st.session_state.pop("menu_superadmin_actual", None)
      st.query_params.clear()
      st.rerun()
    else:
      render_admin_panel(API_URL)

  # ==========================================
  # --- ROL: CLIENTE ---
  # ==========================================
  elif rol_actual == "cliente":
    nombre_usuario = st.session_state.get("user_name", "Cliente")

    # Estilo específico para compactar y centrar el selectbox del cliente
    st.markdown(
        """
        <style>
        /* Contenedor y selectbox del cliente más angosto y compacto */
        div[data-testid="stSelectbox"] {
            max-width: 280px !important;
            margin: 0 auto !important;
        }
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            min-height: 32px !important;
            padding-top: 0px !important;
            padding-bottom: 0px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col_esp_izq, col_centro_cliente, col_esp_der = st.columns([1, 2.5, 1])

    with col_centro_cliente:
      st.markdown(
          f"""<div style='text-align: center; margin-bottom: 6px;'>
              👋 <b>Hola, {nombre_usuario}</b> 🌟 Bookea Tu Evento
          </div>""",
          unsafe_allow_html=True,
      )
      
      opciones_cliente = [
          "Catálogo de Eventos",
          "Mis Reservas",
          "Actualizar Datos",
          "Cerrar Sesión",
      ]
      opcion = st.selectbox(
          "Mi Cuenta", opciones_cliente, label_visibility="collapsed"
      )

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
        render_seleccion_mesas(
            API_URL,
            st.session_state.evento_a_reservar,
            st.session_state.get("user_id"),
        )
      elif st.session_state.paso_reserva == "crear_celebracion":
        if st.button("⬅️ Volver a la cartelera"):
          st.session_state.paso_reserva = "catalogo"
          st.rerun()
        render_crear_reserva_personalizada(
            API_URL, st.session_state.get("user_id")
        )

    elif opcion == "Mis Reservas":
      render_mis_reservas(API_URL, st.session_state.get("user_id"))

    elif opcion == "Actualizar Datos":
      render_mantenimiento_cliente(API_URL)

  # ==========================================
  # --- ROL: PROPIETARIO ---
  # ==========================================
  else:
    
    user_id = st.session_state.get("propietario_id") or st.session_state.get(
        "user_id"
    )

    # 1. Obtener y filtrar los locales del propietario
    locales_propietario = []

    # Recuperar el ID del usuario logueado de forma robusta
    user_id = (
        st.session_state.get("user_id")
        or st.session_state.get("propietario_id")
        or st.session_state.get("id")
    )

    local_id_url = query_params.get("local_id")
    local_id_actual = (
        local_id_url
        or st.session_state.get("local_id_actual")
        or st.session_state.get("local_id")
        or st.session_state.get("local_activo_id")
    )

    try:
      if user_id:
        # Petición a la API filtrando estrictamente por el propietario logueado
        res_api = requests.get(f"{API_URL}/locales/?propietario_id={user_id}")
        if res_api.status_code != 200:
          res_api = requests.get(
              f"{API_URL}/locales/usuario/{user_id}", timeout=5
          )

        if res_api.status_code == 200:
          data_locales = res_api.json()
          locales_propietario = (
              data_locales if isinstance(data_locales, list) else [data_locales]
          )
    except Exception:
      locales_propietario = []

    if locales_propietario:
      opciones_locales = {}
      for loc in locales_propietario:
        lid = loc.get("id") or loc.get("local_id") or 1
        nombre = loc.get(
            "nombre", loc.get("nombre_local", loc.get("nombre_comercial", "Local"))
        )
        # Formato solicitado: ID y Nombre del local en el selector
        etiqueta = f"ID {lid} - {nombre}"
        opciones_locales[etiqueta] = lid

      nombres_opciones = list(opciones_locales.keys())

      valido = False
      for etiqueta, lid in opciones_locales.items():
        if str(lid) == str(local_id_actual):
          local_id_actual = lid
          valido = True
          break

      if not valido and nombres_opciones:
        local_id_actual = opciones_locales[nombres_opciones[0]]
    else:
      opciones_locales = {}
      nombres_opciones = []
      local_id_actual = 1

    # Sincronizamos las variables de sesión y actualizamos la URL globalmente
    st.session_state["local_id_actual"] = int(local_id_actual)
    st.session_state["local_id"] = int(local_id_actual)
    st.session_state["local_activo_id"] = int(local_id_actual)

    st.query_params["logged"] = "true"
    st.query_params["role"] = rol_actual
    st.query_params["local_id"] = str(local_id_actual)

    # ==========================================
    # ESTILOS CSS PARA DISEÑO COMPACTO Y RESPONSIVE
    # ==========================================
    st.markdown(
        """
        <style>
        .centered-header-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            width: 100%;
            text-align: center;
            margin-bottom: 20px;
        }
        div[data-testid="stSelectbox"] {
            max-width: 340px;
            margin: 0 auto !important;
        }
        div[data-testid="stSelectbox"] label p {
            color: #ffffff !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            text-align: center !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
            <div style="display: flex; justify-content: center; width: 100%;">
                <div style="background: rgba(16, 14, 36, 0.85); border: 1px solid rgba(150, 55, 255, 0.35); padding: 10px 20px; border-radius: 12px; margin-bottom: 16px; display: inline-block; text-align: center;">
                    <span style="font-size: 14px; font-weight: 600; color: #f7f7ff;">
                        Agenda Bookea ⭐ <span style="color: #ffffff;">{st.session_state.get('user_name', 'Usuario')}</span> 
                        ⭐
                    </span>
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )

    # ==========================================
    # SELECTORES CENTRADOS EN LA PARTE SUPERIOR
    # ==========================================
    col_espaciador_izq, col_centrada, col_espaciador_der = st.columns(
        [1, 2.5, 1]
    )

    with col_centrada:
      if nombres_opciones:
        current_idx = 0
        for idx, (nombre, lid) in enumerate(opciones_locales.items()):
          if str(lid) == str(local_id_actual):
            current_idx = idx
            break

        local_seleccionado_label = st.selectbox(
            "🏢 Establecimiento activo",
            nombres_opciones,
            index=current_idx,
            key="select_local_activo_top",
        )
        nuevo_local_id = opciones_locales[local_seleccionado_label]
        if str(nuevo_local_id) != str(local_id_actual):
          st.session_state["local_id_actual"] = int(nuevo_local_id)
          st.session_state["local_id"] = int(nuevo_local_id)
          st.session_state["local_activo_id"] = int(nuevo_local_id)
          st.query_params["local_id"] = str(nuevo_local_id)
          st.rerun()
      else:
        st.selectbox(
            "🏢 Establecimiento activo",
            ["Local por defecto (ID: 1)"],
            key="select_local_activo_top_default",
        )

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

      # Recuperar menú activo desde la URL si existe para persistencia absoluta
      menu_url = query_params.get("menu")
      if (
          "menu_propietario_activo" not in st.session_state
          or st.session_state.menu_propietario_activo not in opciones_menu
      ):
        if menu_url and menu_url in opciones_menu:
          st.session_state.menu_propietario_activo = menu_url
        else:
          st.session_state.menu_propietario_activo = "Agenda de Eventos"

      opcion_seleccionada = st.selectbox(
          "📌 Menú de Gestión", opciones_menu, key="menu_propietario_activo"
      )

      # Actualizar el menú actual en la URL
      if opcion_seleccionada != "🚪 Cerrar Sesión":
        st.query_params["menu"] = opcion_seleccionada

    # Evaluar si se seleccionó Cerrar Sesión
    if opcion_seleccionada == "🚪 Cerrar Sesión":
      st.session_state.logged_in = False
      st.session_state.user_role = None
      st.session_state.pop("menu_propietario_activo", None)
      st.query_params.clear()
      st.rerun()

    # Renderizado dinámico fluido de la vista seleccionada
    funcion_a_renderizar = vistas_mapeo.get(
        opcion_seleccionada, render_agenda_propietario
    )
    funcion_a_renderizar(API_URL)

# --- PIE DE PÁGINA GLOBAL ---
render_pie_pagina()