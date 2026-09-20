import requests
import streamlit as str_lit


def render_crear_eventos(API_URL):
  # ==========================================================
  # ESTILOS CSS GLOBALES (CENTRADO ABSOLUTO DE TODO EL CONTENIDO)
  # ==========================================================
  str_lit.markdown(
      """
    <style>
    /* 1. Centrar etiquetas, textos y contenedores de texto generales */
    .stMarkdown, div[data-testid="stMarkdownContainer"] {
        text-align: center !important;
    }

    /* 2. Centrar bloques horizontales superiores (Establecimientos y Menús) */
    .block-container div[data-testid="stHorizontalBlock"] {
        justify-content: center !important;
        align-items: center !important;
    }

    /* 3. Centrar los selectbox y cajas de texto principales */
    div[data-testid="stSelectbox"],
    div[data-testid="stTextInput"], 
    div[data-testid="stTextArea"],
    div[data-testid="stDateInput"],
    div[data-testid="stTimeInput"],
    div[data-testid="stFileUploader"] {
        max-width: 320px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }

    /* 4. Centrar títulos de la vista */
    .stHeader, h1, h2, h3 {
        text-align: center !important;
    }
    
    div[data-testid="stMarkdownContainer"] h1, 
    div[data-testid="stMarkdownContainer"] h2,
    h1#creacion-de-eventos {
        text-align: center !important;
        display: block;
        width: 100%;
    }

    /* 5. Centrar el contenedor principal del formulario y limitar su ancho */
    div[data-testid="stForm"] {
        max-width: 520px !important;
        margin: 20px auto 0 auto !important;
        background-color: #0d0f1a !important;
        border: 1px solid rgba(150, 55, 255, 0.25) !important;
        border-radius: 12px !important;
        padding: 28px !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4) !important;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    /* 6. Forzar blanco brillante, negrita y centrado en las etiquetas de los campos */
    .stApp label,
    div[data-testid="stWidgetLabel"] p,
    div[data-testid="stForm"] label p,
    label[data-testid="stWidgetLabel"] p,
    .stMarkdown p strong {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        letter-spacing: 0.3px !important;
        text-align: center !important;
        display: block !important;
        width: 100% !important;
    }

    /* 7. Centrar campos internos dentro del formulario para que no se desalineen */
    div[data-testid="stForm"] div[data-testid="stTextInput"], 
    div[data-testid="stForm"] div[data-testid="stTextArea"],
    div[data-testid="stForm"] div[data-testid="stDateInput"],
    div[data-testid="stForm"] div[data-testid="stTimeInput"],
    div[data-testid="stForm"] div[data-testid="stFileUploader"],
    div[data-testid="stForm"] div[data-testid="stSelectbox"] {
        width: 100% !important;
        max-width: 320px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }

    /* 8. Botón de guardar evento centrado y moderno */
    div[data-testid="stFormSubmitButton"] {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
        margin-top: 20px !important;
    }
    
    div[data-testid="stFormSubmitButton"] > button {
        max-width: 240px !important;
        width: 100% !important;
        padding: 10px 20px !important;
        background: linear-gradient(135deg, #7928CA 0%, #4A00E0 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        box-shadow: 0 4px 12px rgba(121, 40, 202, 0.35) !important;
        transition: all 0.2s ease-in-out !important;
        margin: 0 auto !important;
    }

    div[data-testid="stFormSubmitButton"] > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 18px rgba(121, 40, 202, 0.6) !important;
        border-color: #00cfff !important;
    }

    /* 9. Asegurar centrado y contraste en checkboxes y textos secundarios */
    div[data-testid="stCheckbox"] {
        display: flex !important;
        justify-content: center !important;
        margin: 10px auto !important;
    }
    
    div[data-testid="stCheckbox"] label {
        justify-content: center !important;
    }

    div[data-testid="stCheckbox"] label span {
        color: #E2E8F0 !important;
        font-size: 14px !important;
        text-align: center !important;
    }
    </style>
    """,
      unsafe_allow_html=True,
  )

  # ==========================================================
  # CAPTURAR LOCAL ID DESDE EL ESTABLECIMIENTO ACTIVO GLOBAL
  # ==========================================================
  local_id = (
      str_lit.session_state.get("local_id_actual")
      or str_lit.session_state.get("local_id")
      or str_lit.session_state.get("local_activo_id")
      or 1
  )

  str_lit.session_state["local_id"] = int(local_id)

  # Encabezado centrado
  col_head1, col_head2, col_head3 = str_lit.columns([1, 2, 1])
  with col_head2:
    str_lit.markdown(
        "<h2 style='text-align: center; color: white;'>📅 Creación de"
        " Eventos</h2>",
        unsafe_allow_html=True,
    )

  # ==========================================================
  # FORMULARIO ÚNICO DE CREACIÓN DE EVENTOS (VERTICAL Y CENTRADO)
  # ==========================================================
  with str_lit.form("form_evento"):
    nombre_evento = str_lit.text_input(
        "Nombre del Evento (ej: JUEVES DE RUMBA)"
    )
    artista = str_lit.text_input("Artista u Orquesta (Opcional)")

    # Fecha y hora apiladas verticalmente
    fecha = str_lit.date_input("Fecha del Evento")
    hora = str_lit.time_input("Hora del Evento")

    descripcion = str_lit.text_area("Descripción")

    str_lit.markdown("---")
    str_lit.markdown("📱 **Flyer Publicitario del Evento**")

    generar_reel = str_lit.checkbox(
        "✨ Modo Inteligente para Reel (Centrar con fondo elegante sin"
        " recortar)",
        value=True,
        help=(
            "Marcado: Centra la imagen manteniendo todo el contenido original"
            " sobre un fondo vertical elegante. Desmarcado: Realiza un recorte"
            " automático (Cover) para llenar toda la pantalla vertical."
        ),
    )

    foto_flyer = str_lit.file_uploader(
        "Sube la Foto Publicitaria del Evento", type=["jpg", "jpeg", "png"]
    )

    if foto_flyer is not None:
      str_lit.info(
          "💡 Tu imagen fue adaptada automáticamente a formato vertical 9:16"
          " para mantener la agenda ordenada. Si desea modificar puedes ir a"
          " la opción editar del evento."
      )

    submit_evento = str_lit.form_submit_button("Guardar Evento")

  # ==========================================================
  # PROCESAMIENTO ÚNICO DEL ENVÍO Y REDIRECCIÓN LIMPIA
  # ==========================================================
  if submit_evento:
    if str_lit.session_state.get("guardando_en_proceso", False):
      return

    str_lit.session_state["guardando_en_proceso"] = True

    hora_formateada = hora.strftime("%H:%M:%S")
    fecha_hora_str = f"{fecha}T{hora_formateada}"

    data_evento = {
        "local_id": str(local_id),
        "nombre_evento": nombre_evento,
        "artista_orquesta": artista if artista else "",
        "fecha_hora": fecha_hora_str,
        "descripcion": descripcion if descripcion else "",
        "generar_reel": str(generar_reel).lower(),
        "estado": "activo",
    }

    files = {}
    if foto_flyer is not None:
      files = {"file": (foto_flyer.name, foto_flyer.getvalue(), foto_flyer.type)}

    try:
      response = requests.post(
          f"{API_URL}/reservas/eventos/",
          data=data_evento,
          files=files if files else None,
      )
      if response.status_code in [200, 201]:
        str_lit.session_state["guardando_en_proceso"] = False
        str_lit.session_state["redirigir_a_agenda"] = True
        str_lit.success("¡Evento creado con éxito! Redirigiendo...")
        str_lit.rerun()
      else:
        str_lit.session_state["guardando_en_proceso"] = False
        str_lit.error(f"Error al crear evento: {response.text}")
    except Exception as e:
      str_lit.session_state["guardando_en_proceso"] = False
      str_lit.error(f"Error de conexión: {e}")