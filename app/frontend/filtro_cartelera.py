import streamlit as st

def render_sidebar_filtros(locales, lista_paises, def_pais, def_ciudad, def_tipo, def_id):
    """
    Renderiza los filtros de ubicación y establecimiento en la barra lateral,
    organizados dentro de la pestaña 'Descubre más'.
    Retorna el local seleccionado actualmente y los parámetros de filtro.
    """
    st.markdown("""
    <style>
        /* Fondo negro absoluto para los menús desplegables flotantes de Streamlit */
        div[data-baseweb="popover"], 
        div[data-baseweb="menu"],
        ul[data-baseweb="menu"] {
            background-color: #121620 !important;
            border: 1px solid #323d54 !important;
        }
        
        /* Color del texto de las opciones del menú desplegable */
        div[data-baseweb="popover"] div, 
        ul[data-baseweb="menu"] div, 
        ul[data-baseweb="menu"] span {
            color: #ffffff !important;
            background-color: transparent !important;
        }

        /* Color al pasar el cursor sobre las opciones */
        ul[data-baseweb="menu"] li:hover {
            background-color: #1f293d !important;
            color: #00bfff !important;
        }

        /* Estilizar los selectbox y text_input de la barra lateral para quitarles el fondo blanco */
        [data-testid="stSidebar"] div[data-baseweb="select"] > div,
        [data-testid="stSidebar"] input {
            background-color: #121620 !important;
            color: #ffffff !important;
            border: 1px solid #323d54 !important;
            border-radius: 6px !important;
        }

        /* Asegurar que el texto dentro de los selectbox y campos de texto sea blanco */
        [data-testid="stSidebar"] div[data-baseweb="select"] span,
        [data-testid="stSidebar"] input::placeholder {
            color: #a0aec0 !important;
        }

        /* Color al enfocar los inputs o selectores en la barra lateral */
        [data-testid="stSidebar"] div[data-baseweb="select"] > div:focus-within,
        [data-testid="stSidebar"] input:focus {
            border-color: #00bfff !important;
            box-shadow: 0 0 0 1px #00bfff !important;
        }

        /* Compactar los espacios y márgenes verticales en la barra lateral */
        [data-testid="stSidebar"] .element-container {
            margin-bottom: -0.6rem !important;
        }
        
        [data-testid="stSidebar"] hr {
            margin-top: 0.4rem !important;
            margin-bottom: 0.4rem !important;
        }

        [data-testid="stSidebar"] h3 {
            margin-bottom: 0.2rem !important;
            margin-top: 0.2rem !important;
            font-size: 1.1rem !important;
        }
    </style>
""", unsafe_allow_html=True)
    
    with st.sidebar:
        # Pestañas en la barra lateral
        tab_menu, tab_descubre = st.tabs(["Menú Cliente", "Descubre más 🌐"])
        
        with tab_menu:
            st.markdown("### Navegación del Cliente")
            if "menu_cliente_actual" not in st.session_state:
                st.session_state.menu_cliente_actual = "Catálogo de Eventos"

            opciones_cliente = [
                "Catálogo de Eventos", 
                "Mis Reservas", 
                "Mantenimiento / Actualizar Datos", 
                "Volver a Bookea", 
                "Cerrar Sesión"
            ]
            
            if st.session_state.menu_cliente_actual not in opciones_cliente:
                st.session_state.menu_cliente_actual = "Catálogo de Eventos"

            opcion = st.radio(
                "Seleccione una opción:",
                opciones_cliente,
                index=opciones_cliente.index(st.session_state.menu_cliente_actual),
                key="menu_cliente_actual",
                label_visibility="collapsed"
            )
            
            # Guardamos la opción seleccionada en el estado para que frontend.py la lea
            st.session_state["_opcion_menu_cliente_sidebar"] = opcion

        with tab_descubre:
            st.markdown("### Filtros de Ubicación")
            orden_cercania = st.checkbox("🎯 Ordenar por cercanía GPS", value=False, key="check_cercania_gps_cartelera")
            
            st.markdown("---")
            
            # Filtro de País
            idx_pais = lista_paises.index(def_pais) if def_pais in lista_paises else 0
            pais_filtro = st.selectbox("Filtrar por País", lista_paises, index=idx_pais, key="filtro_pais_cartelera")
            
            # Filtro de Ciudad basado en datos reales
            ciudades_disponibles = sorted(list(set(str(l.get("ciudad")).strip() for l in locales if l.get("ciudad"))))
            idx_ciudad = ciudades_disponibles.index(def_ciudad) if def_ciudad in ciudades_disponibles else 0
            ciudad_filtro = st.selectbox("Filtrar por Ciudad", ciudades_disponibles, index=idx_ciudad, key="filtro_ciudad_cartelera")

            # Filtrado geográfico
            locales_filtrados_geo = [l for l in locales if str(l.get("ciudad")) == ciudad_filtro]
            if not locales_filtrados_geo:
                locales_filtrados_geo = locales

            st.markdown("---")
            st.markdown("### Establecimiento")

            # Tipos de establecimiento
            tipos_disponibles = sorted(list(set(str(loc.get("tipo_establecimiento")).strip() for loc in locales_filtrados_geo if loc.get("tipo_establecimiento"))))
            idx_tipo = tipos_disponibles.index(def_tipo) if def_tipo in tipos_disponibles else 0
            filtro_tipo = st.selectbox("Tipo de Local", tipos_disponibles, index=idx_tipo, key="filtro_tipo_local")

            # Selector de local específico
            locales_filtrados_selector = [l for l in locales_filtrados_geo if str(l.get("tipo_establecimiento", "")) == filtro_tipo]
            if not locales_filtrados_selector:
                locales_filtrados_selector = locales_filtrados_geo
            
            opciones_locales = {}
            idx_local_default = 0
            for idx_l, loc in enumerate(locales_filtrados_selector):
                loc_id = loc.get("id")
                nombre_l = loc.get("nombre_local", "Mi Local")
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
                
            local_seleccionado_etiqueta = st.selectbox("Establecimiento", nombres_opciones, index=idx_local_default, key="filtro_nombre_local")
            info_local_actual = opciones_locales.get(local_seleccionado_etiqueta, list(opciones_locales.values())[0])

            # Campo de búsqueda de eventos dentro de la misma pestaña lateral
            st.markdown("---")
            busqueda_evento = st.text_input("Buscar Evento", placeholder="🔍 Buscar evento, artista...", key="busqueda_evento_input")

    return info_local_actual, busqueda_evento, orden_cercania