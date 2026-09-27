import os
import configparser
import requests
import streamlit as st

def render_filtro_locales(api_url):
    """
    Renderiza los filtros de país, ciudad, tipo de establecimiento, 
    selector de local, barra de búsqueda de eventos y cercanía GPS.
    Retorna: (info_local_actual, busqueda_evento, orden_cercania)
    """
    
    # ==========================================
    # 0.1. CARGA DE PAÍSES Y CONFIGURACIÓN INI
    # ==========================================
    config_paises = configparser.ConfigParser()
    if os.path.exists("paises.ini"):
        config_paises.read("paises.ini", encoding="utf-8")
    paises_dict = (
        dict(config_paises["PREFIJOS"])
        if "PREFIJOS" in config_paises
        else {"Ecuador": "+593"}
    )
    paises_dict = {pais.title(): prefijo for pais, prefijo in paises_dict.items()}
    lista_paises = list(paises_dict.keys())

    # ==========================================
    # 0.2. OBTENCIÓN ROBUSTA DE LOCALES
    # ==========================================
    try:
        resp_locales = requests.get(f"{api_url}/locales", timeout=5)
        locales = resp_locales.json() if resp_locales.status_code == 200 else []
    except Exception:
        locales = []

    if not locales:
        locales = [{
            "id": 1,
            "nombre": "Mi Local",
            "tipo_establecimiento": "Restaurante/Bar",
            "ciudad": "Guayaquil",
            "pais": "Ecuador",
            "direccion": "Av. Principal 123",
            "telefono_contacto": "0999999999"
        }]

    # ==========================================
    # 0.3. DETECCIÓN DEL LOCAL INICIAL
    # ==========================================
    local_inicial = None
    id_local_guardado = st.session_state.get("id_local_actual")
    if id_local_guardado:
        for l in locales:
            if str(l.get("id")) == str(id_local_guardado):
                local_inicial = l
                break

    if not local_inicial:
        local_inicial = locales[0]

    def_pais = str(local_inicial.get("pais", "Ecuador")).strip().title()
    def_ciudad = str(local_inicial.get("ciudad", "Guayaquil")).strip()
    def_tipo = str(
        local_inicial.get(
            "tipo_establecimiento",
            local_inicial.get("tipo_negocio", "Restaurante/Bar"),
        )
    ).strip()
    def_id = local_inicial.get("id")

    # ==========================================
    # 1. PANEL DE FILTROS Y SELECTORES JERÁRQUICOS
    # ==========================================
    with st.container(border=True):
        st.markdown("### 🔍 Filtros de Búsqueda y Ubicación")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            idx_pais = lista_paises.index(def_pais) if def_pais in lista_paises else 0
            pais_filtro = st.selectbox("Filtrar por País", lista_paises, index=idx_pais, key="filtro_pais_cartelera")
        with col_f2:
            ciudades_disponibles = sorted(list(set(str(l.get("ciudad")).strip() for l in locales if l.get("ciudad"))))
            idx_ciudad = ciudades_disponibles.index(def_ciudad) if def_ciudad in ciudades_disponibles else 0
            ciudad_filtro = st.selectbox("Filtrar por Ciudad", ciudades_disponibles, index=idx_ciudad, key="filtro_ciudad_cartelera")

        locales_filtrados_geo = [l for l in locales if str(l.get("ciudad")) == ciudad_filtro]
        if not locales_filtrados_geo:
            locales_filtrados_geo = locales

        st.markdown("---")

        col_f3, col_f4 = st.columns(2)
        with col_f3:
            tipos_disponibles = sorted(list(set(str(loc.get("tipo_establecimiento")).strip() for loc in locales_filtrados_geo if loc.get("tipo_establecimiento"))))
            idx_tipo = tipos_disponibles.index(def_tipo) if def_tipo in tipos_disponibles else 0
            filtro_tipo = st.selectbox("Tipo de Local", tipos_disponibles, index=idx_tipo, key="filtro_tipo_local")

        locales_filtrados_selector = [l for l in locales_filtrados_geo if str(l.get("tipo_establecimiento", "")) == filtro_tipo]
        if not locales_filtrados_selector:
            locales_filtrados_selector = locales_filtrados_geo
        
        opciones_locales = {}
        idx_local_default = 0
        for idx_l, loc in enumerate(locales_filtrados_selector):
            loc_id = loc.get("id")
            nombre_l = loc.get("nombre", loc.get("nombre_local", "Mi Local"))
            ciudad_l = loc.get("ciudad", "General")
            tipo_l = loc.get("tipo_establecimiento", "Local")
            
            etiqueta = f"{nombre_l} — [{ciudad_l}] ({tipo_l})"
            opciones_locales[etiqueta] = loc
            
            if str(loc_id) == str(def_id):
                idx_local_default = idx_l

        nombres_opciones = list(opciones_locales.keys())
        if not nombres_opciones:
            nombres_opciones = ["Mi Local"]
            opciones_locales["Mi Local"] = locales[0]
            idx_local_default = 0
            
        with col_f4:
            local_seleccionado_etiqueta = st.selectbox("Establecimiento", nombres_opciones, index=idx_local_default, key="filtro_nombre_local")
            info_local_actual = opciones_locales.get(local_seleccionado_etiqueta, list(opciones_locales.values())[0])

        st.markdown("---")

        busqueda_evento = st.text_input("Buscar Evento", placeholder="🔍 Buscar evento, artista...", key="busqueda_evento_input")
        orden_cercania = st.checkbox("🎯 Orden por cercanía GPS", value=False, key="check_cercania_gps_cartelera")

        st.session_state["id_local_actual"] = info_local_actual.get("id")
        st.session_state["info_local_actual"] = info_local_actual
        st.session_state["busqueda_evento"] = busqueda_evento
        st.session_state["orden_cercania"] = orden_cercania

    return info_local_actual, busqueda_evento, orden_cercania