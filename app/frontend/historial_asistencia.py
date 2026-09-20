import streamlit as st
import requests
import pandas as pd

def render_historial_asistencia(api_url: str):
    st.subheader("📊 Historial y Reportes de Asistencia")
    st.write("Consulta el registro histórico de asistentes que ingresaron a los eventos.")

    usuario_id_actual = st.session_state.get("usuario_id") or st.session_state.get("propietario_id")

    # 1. Selector de local para filtrar el historial por establecimiento
    local_id_elegido = None
    try:
        resp_locales = requests.get(f"{api_url}/locales/?propietario_id={usuario_id_actual}", timeout=5) if usuario_id_actual else requests.get(f"{api_url}/locales/", timeout=5)
        if resp_locales.status_code == 200 and resp_locales.json():
            locales = resp_locales.json()
            local_opciones = {
                f"{l.get('nombre_comercial', l.get('nombre_local', l.get('nombre', 'Local')))} (ID: {l.get('id', l.get('local_id'))})": l.get('id', l.get('local_id'))
                for l in locales
            }
            local_label = st.selectbox("📍 Filtrar por Establecimiento:", list(local_opciones.keys()), key="historial_select_local")
            local_id_elegido = local_opciones[local_label]
    except Exception:
        pass

    # 2. Obtener eventos del establecimiento
    evento_id_elegido = None
    try:
        url_evs = f"{api_url}/reservas/eventos/?local_id={local_id_elegido}" if local_id_elegido else f"{api_url}/reservas/eventos/"
        resp_eventos = requests.get(url_evs, timeout=5)
        
        if resp_eventos.status_code == 200 and resp_eventos.json():
            eventos = resp_eventos.json()
            evento_opciones = {"Todos los Eventos": None}
            for e in eventos:
                e_id = e.get('id') or e.get('evento_id')
                e_nombre = e.get('nombre_evento') or e.get('titulo')
                evento_opciones[f"ID {e_id} - {e_nombre}"] = e_id
            
            evento_label = st.selectbox("📅 Filtrar por Evento:", list(evento_opciones.keys()), key="historial_select_evento")
            evento_id_elegido = evento_opciones[evento_label]
    except Exception:
        pass

    st.markdown("---")

    # 3. Obtener y filtrar los registros de asistencia global
    try:
        resp_all = requests.get(f"{api_url}/reservas/qr/todos", timeout=5)
        if resp_all.status_code == 200:
            registros = resp_all.json()
            
            if not registros:
                st.info("No hay registros de asistencia en el sistema.")
                return

            # Filtrar solo los que ya asistieron (check-in realizado)
            asistencias_confirmadas = [
                q for q in registros 
                if q.get("estado_ingreso") in ["utilizado", "completada"]
            ]

            # Aplicar filtro por evento si se seleccionó uno en específico
            if evento_id_elegido:
                asistencias_confirmadas = [
                    q for q in asistencias_confirmadas 
                    if str(q.get("evento_id")) == str(evento_id_elegido)
                ]

            if not asistencias_confirmadas:
                st.warning("No hay registros de asistencia confirmada con los filtros seleccionados.")
                return

            st.metric("Total de Asistentes Validados", len(asistencias_confirmadas))

            # Preparar datos para tabla limpia con pandas
            data_tabla = []
            for item in asistencias_confirmadas:
                data_tabla.append({
                    "Cliente": item.get("cliente_nombre", "Desconocido"),
                    "Mesa / Ubicación": f"Mesa #{item.get('mesa_id', 'N/A')}",
                    "Código QR": item.get("codigo_qr", ""),
                    "Estado": "En Sitio (Check-in)",
                    "ID Reserva": item.get("reserva_id", "N/A")
                })

            df = pd.DataFrame(data_tabla)
            st.dataframe(df, use_container_width=True)

            # Botón opcional para exportar a CSV
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Historial en CSV",
                data=csv_data,
                file_name="historial_asistencia.csv",
                mime="text/csv",
            )
        else:
            st.error("No se pudo conectar con el servidor para obtener los registros.")
    except Exception as e:
        st.error(f"Error al procesar el histórico: {e}")