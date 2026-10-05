import streamlit as st

def inicializar_gestion_local():
    """
    Captura y sincroniza el local activo desde los parámetros de la URL 
    o el estado de la sesión de manera transversal (funciona para home.py, mini-web, etc.).
    """
    # 1. Intentar capturar desde los parámetros de la URL si existen
    url_local_id = st.query_params.get("local_id") or st.query_params.get("id_local")
    
    if url_local_id:
        st.session_state["id_local_actual"] = url_local_id

def obtener_local_actual(locales_disponibles):
    """
    Devuelve el diccionario del local activo actual.
    Prioriza: st.session_state -> primer local disponible como respaldo.
    """
    if not locales_disponibles:
        return None

    # Asegurar que la sesión esté sincronizada
    inicializar_gestion_local()

    id_activo = (
        st.session_state.get("id_local_actual")
        or st.session_state.get("local_id")
    )

    if id_activo:
        for l in locales_disponibles:
            # Comparamos tanto por ID (str o int) como por nombre/slug si coincide
            if (
                str(l.get("id")) == str(id_activo) 
                or str(l.get("nombre", "")).strip().lower() == str(id_activo).strip().lower()
            ):
                return l

    # Si no hay coincidencia o no está definido, devolvemos el primero por defecto
    return locales_disponibles[0]

def fijar_local_actual(local_id):
    """
    Actualiza el local activo en la sesión y en la URL de forma limpia 
    para que cualquier módulo se entere del cambio.
    """
    st.session_state["id_local_actual"] = local_id
    # Opcional: actualizar query params para mantener consistencia en la URL
    try:
        st.query_params["local_id"] = str(local_id)
    except Exception:
        pass