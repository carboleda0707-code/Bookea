import requests
import streamlit as str_lit
from header_global import render_header

def render_crear_eventos(API_URL):
  # Renderizar la cabecera global unificada (incluye menú y estilos generales)
  render_header("Soluciones para propietarios")

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
        "<h2 style='text-align: center; color: white; margin-top: 20px;'>📅 Creación de Eventos</h2>",
        unsafe_allow_html=True,
    )

  # ==========================================================
  # FORMULARIO ÚNICO DE CREACIÓN DE EVENTOS
  # ==========================================================
  with str_lit.form("form_evento"):
    nombre_evento = str_lit.text_input(
        "Nombre del Evento (ej: JUEVES DE RUMBA)"
    )
    artista = str_lit.text_input("Artista u Orquesta (Opcional)")

    fecha = str_lit.date_input("Fecha del Evento")
    hora = str_lit.time_input("Hora del Evento")

    descripcion = str_lit.text_area("Descripción")

    str_lit.markdown("---")
    str_lit.markdown("📱 **Flyer Publicitario del Evento**")

    generar_reel = str_lit.checkbox(
        "✨ Modo Inteligente para Reel (Centrar con fondo elegante sin recortar)",
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
  # PROCESAMIENTO DEL ENVÍO Y REDIRECCIÓN
  # ==========================================================
  if submit_evento:
    if str_lit.session_state.get("guardando_en_proceso", False):
      return

    str_lit.session_state["guardando_en_proceso"] = True

    hora_formateada = hora.strftime("%H:%M:%S")
    fecha_hora_str = f"{fecha}T{hora_formateada}"

    id_creador = (
        str_lit.session_state.get("usuario_id")
        or str_lit.session_state.get("propietario_id")
        or str_lit.session_state.get("cliente_id")
        or 1
    )

    data_evento = {
        "local_id": str(local_id),
        "nombre_evento": nombre_evento,
        "artista_orquesta": artista if artista else "",
        "fecha_hora": fecha_hora_str,
        "descripcion": descripcion if descripcion else "",
        "generar_reel": str(generar_reel).lower(),
        "estado": "activo",
        "creador": str(id_creador)
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