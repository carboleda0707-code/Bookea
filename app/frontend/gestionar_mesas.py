import streamlit as st
import requests

def render_mapa_mesas(api_url: str, evento_id: int):
    st.subheader(f"Mapa de Mesas para el Evento #{evento_id}")
    
    # Consultamos el estado de las mesas a la API
    try:
        response = requests.get(f"{api_url}/reservas/mesas-disponibles/{evento_id}")
        if response.status_code == 200:
            mesas = response.json()
            
            # Creamos una cuadrícula de 4 columnas para visualizar las mesas
            cols = st.columns(4)
            for i, mesa in enumerate(mesas):
                with cols[i % 4]:
                    # Definimos color y estado
                    if mesa["disponible"]:
                        st.success(f"Mesa {mesa['numero_mesa']}\nLibre")
                    else:
                        st.error(f"Mesa {mesa['numero_mesa']}\nOCUPADA")
        else:
            st.error("No se pudo cargar el mapa de mesas.")
    except Exception as e:
        st.error(f"Error: {e}")