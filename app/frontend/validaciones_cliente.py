import streamlit as st
import re

def validar_telefono(telefono: str) -> bool:
    """Valida que el teléfono tenga un formato numérico válido (mínimo 7 dígitos)."""
    if not telefono:
        return True # Si es opcional o viene vacío
    # Limpia espacios o guiones y verifica que sean solo dígitos con longitud adecuada
    limpio = re.sub(r'[\s\-\(\)]', '', telefono)
    return limpio.isdigit() and len(limpio) >= 7

def render_mantenimiento_cliente(api_url: str):
    
    # ============================================================
    # ESTILOS CSS GLOBALES (CAMPOS OSCUROS, TÍTULOS, BOTÓN Y TÍTULO UNIFICADO)
    # ============================================================
    st.markdown("""
    <style>
    /* Centrar la sección principal y limitar el ancho */
    .block-container {
        max-width: 900px !important;
        margin: 0 auto !important;
    }

    /* Forzar que el saludo superior y título no se dividan en dos líneas */
    .titulo-unificado {
        white-space: nowrap !important;
        font-size: 1.1rem;
        font-weight: 500;
        margin-bottom: 1rem;
    }

    /* ============================================================
       RESALTAR TÍTULOS DE LAS ENTRADAS DE TEXTO
       ============================================================ */
    div[data-testid="stTextInput"] label p {
        color: #38bdf8 !important; /* Color azul claro destacado */
        font-weight: 600 !important;
        font-size: 15px !important;
    }

    /* ============================================================
       OSCURECER LOS CAMPOS DE ENTRADA (INPUTS)
       ============================================================ */
    div[data-testid="stTextInput"] input {
        background-color: #141625 !important;
        color: #ffffff !important;
        border: 1px solid rgba(150, 55, 255, 0.4) !important;
        border-radius: 8px !important;
    }

    div[data-testid="stTextInput"] input:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 5px rgba(56, 189, 248, 0.3) !important;
    }
    
    /* Fondo del contenedor de los inputs transparente */
    div[data-testid="stTextInput"] div[data-baseweb="input"] {
        background-color: #141625 !important;
        border-radius: 8px !important;
    }

    /* ============================================================
       ESTILIZAR BOTÓN DE FORMULARIO (ELIMINAR EFECTOS BLANCOS)
       ============================================================ */
    div[data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(150, 55, 255, 0.5) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        width: 100% !important;
    }

    div[data-testid="stFormSubmitButton"] button:hover {
        background: linear-gradient(135deg, #8b5cf6, #7c3aed) !important;
        border-color: #38bdf8 !important;
        color: #ffffff !important;
    }

    div[data-testid="stFormSubmitButton"] button:focus,
    div[data-testid="stFormSubmitButton"] button:active {
        color: #ffffff !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 0 8px rgba(56, 189, 248, 0.4) !important;
    }
    </style>
    """, unsafe_allow_html=True)
        
    # Renderizamos el saludo unificado en una sola línea horizontal
    nombre_usuario = st.session_state.get("user_name", "Sandra Bajaña")
    st.markdown(f'<div class="titulo-unificado">👋 <b>Hola, {nombre_usuario}</b> 🌟 Bookea Tu Evento</div>', unsafe_allow_html=True)

    st.header("⚙️ Mantenimiento de Cuenta")
    st.markdown("Actualiza tu información personal, correo y teléfono de contacto.")
    
    with st.form("form_mantenimiento_modular"):
        nombre_actual = st.session_state.get("user_name", "")
        correo_actual = st.session_state.get("user_email", "")
        telefono_actual = st.session_state.get("user_telefono", "")
        
        nuevo_nombre = st.text_input("Nombre", value=nombre_actual)
        nuevo_correo = st.text_input("Correo Electrónico", value=correo_actual)
        nuevo_telefono = st.text_input("Teléfono", value=telefono_actual)
        
        nueva_password = st.text_input("Nueva Contraseña (opcional)", type="password")
        confirma_password = st.text_input("Confirmar Nueva Contraseña", type="password")
        
        guardar_cambios = st.form_submit_button("Actualizar Datos")
        
        if guardar_cambios:
            if nueva_password and nueva_password != confirma_password:
                st.error("❌ Las contraseñas no coinciden. Por favor, revísalas.")
            elif not validar_telefono(nuevo_telefono):
                st.warning("⚠️ El número de teléfono no es válido. Debe contener al menos 7 dígitos numéricos.")
            else:
                if nuevo_correo != correo_actual:
                    st.info("✉️ Se ha enviado un enlace de confirmación a tu nuevo correo electrónico. Por favor, revísalo para validar el cambio.")
                else:
                    st.success("¡Datos actualizados correctamente!")
                    
def render_registro_cliente(api_url: str):
    """Renderiza el formulario de registro de clientes con validaciones de teléfono y contraseña."""
    st.header("📝 Registro de Nuevo Cliente")
    st.markdown("Crea tu cuenta para comenzar a reservar en tus locales favoritos.")
    
    with st.form("form_registro_modular"):
        nombre = st.text_input("Nombre Completo")
        correo = st.text_input("Correo Electrónico")
        telefono = st.text_input("Teléfono (Ej: 0991234567)")
        password = st.text_input("Contraseña", type="password")
        confirma_password = st.text_input("Confirmar Contraseña", type="password")
        
        btn_registrar = st.form_submit_button("Registrarse")
        
        if btn_registrar:
            if not nombre or not correo or not telefono or not password:
                st.error("❌ Por favor, completa todos los campos obligatorios.")
            elif password != confirma_password:
                st.error("❌ Las contraseñas no coinciden.")
            elif not validar_telefono(telefono):
                st.warning("⚠️ El número de teléfono no es válido. Debe contener al menos 7 dígitos numéricos.")
            else:
                st.success("¡Registro exitoso! Se ha enviado un enlace de confirmación a tu correo.")