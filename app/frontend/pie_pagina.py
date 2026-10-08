import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

def render_pie_pagina():
    total_comensales = 3
    total_locales = 3
    try:
        resp = requests.get(f"{API_URL}/auth/stats/social-proof", timeout=2)
        if resp.status_code == 200:
            data = resp.json()
            total_comensales = data.get("total_usuarios", 3)
            total_locales = data.get("total_locales", 3)
    except Exception:
        pass

    html_footer = f"""
    🔥 {total_comensales} activos • 🏛️ {total_locales} Locales Registrados

    📅 Eventos Exclusivos  |  ⚡ Reservas Instantáneas  |  🛡️ Seguridad Garantizada  |  🎧 Soporte 24/7

    📄 Términos y Condiciones  | 
    🟢 Contáctame por WhatsApp  | 
    ❓ Ayuda

    © 2026 Bookea. Todos los derechos reservados.
    """

    st.markdown(html_footer, unsafe_allow_html=True)