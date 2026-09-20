# app/frontend/pie_pagina.py
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

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

    st.markdown(f"""
<style>
.bookea-footer-container {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    width: 100%;
    margin-top: 1rem;
    padding-bottom: 2rem;
    color: #94a3b8;
    font-family: 'Inter', sans-serif;
}}
.bookea-footer-stats {{
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 10px 20px;
    border-radius: 30px;
    margin-bottom: 15px;
    font-size: 0.9rem;
    color: #f1f5f9;
    display: inline-flex;
    gap: 15px;
    align-items: center;
}}
.bookea-footer-stats span {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
}}
.bookea-footer-links {{
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 20px;
    font-size: 0.85rem;
    margin-bottom: 10px;
}}
.bookea-footer-links span {{
    color: #cbd5e1;
}}
.bookea-footer-copy {{
    font-size: 0.8rem;
    color: #64748b;
}}
</style>

<div class="bookea-footer-container">
    <div class="bookea-footer-stats">
        <span>🔥 {total_comensales} 👤 activos</span>
        <span>&bull;</span>
        <span>{total_locales} 🏛️ Locales Registrados</span>
    </div>
    <div class="bookea-footer-links">
        <span>📅 Eventos Exclusivos</span>
        <span>⚡ Reservas Instantáneas</span>
        <span>🛡️ Seguridad Garantizada</span>
        <span>🎧 Soporte 24/7</span>
    </div>
    <div class="bookea-footer-links" style="margin-top: 5px; font-size: 1rem;">
        <span>📄 Términos y Condiciones</span>
        <span>
            <a href="https://wa.me/593983870398" target="_blank">
                🟢 Contactame: Aqui Whatsapp.me
            </a>
        </span>
        <span>❓ Ayuda</span>
    </div>
    <div class="bookea-footer-copy" style="margin-top: 2px; font-size: 0.90rem;">
        © 2026 Bookea. Todos los derechos reservados.
    </div>
</div>
""", unsafe_allow_html=True)