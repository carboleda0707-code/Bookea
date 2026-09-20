import streamlit as st
import requests

def render_seleccion_mesas(api_url: str, evento_id: int, cliente_id: int):
    st.subheader("🪑 Selecciona tu(s) mesa(s)")
    
    try:
        # 1. Intentar mostrar info del evento de forma segura
        try:
            res_evento = requests.get(f"{api_url}/eventos/{evento_id}")
            if res_evento.status_code == 200:
                evento = res_evento.json()
                # Ajusta las llaves según cómo se llame en tu base de datos (ej. nombre_evento o titulo)
                nombre_ev = evento.get('nombre_evento') or evento.get('titulo', 'Evento')
                fecha_ev = evento.get('fecha_hora', '')
                st.markdown(f"### 📅 Evento: **{nombre_ev}**")
                if fecha_ev:
                    st.markdown(f"🕒 **Fecha y Hora:** {fecha_ev}")
                st.markdown("---")
        except:
            pass  # Si falla la consulta del evento, continúa sin bloquear la pantalla

        # 2. Consultar mesas disponibles para el evento
        response = requests.get(f"{api_url}/reservas/mesas-disponibles/{evento_id}")
        if response.status_code != 200:
            st.error("Error al cargar las mesas disponibles.")
            return
            
        mesas = response.json()
        if not mesas:
            st.warning("No hay mesas configuradas para este evento.")
            return

        mesas_seleccionadas = []
        precio_total = 0.0
        consumo_total = 0.0
        capacidad_total = 0

        # 3. Dibujar checkboxes y sumar dinámicamente
        for item in mesas:
            mesa_id = item["mesa_id"]
            numero = item["numero_mesa"]
            capacidad = item["capacidad"]
            precio = float(item.get("precio_reserva") or 0.0)
            consumo = float(item.get("consumo_minimo") or 0.0)
            disponible = item["disponible"]

            label = f"Mesa {numero} - Capacidad: {capacidad} pers. | Reserva: ${precio:.2f} | Consumo Mín: ${consumo:.2f}"

            if disponible:
                if st.checkbox(label, key=f"mesa_chk_{mesa_id}"):
                    mesas_seleccionadas.append(mesa_id)
                    precio_total += precio
                    consumo_total += consumo
                    capacidad_total += capacidad
            else:
                st.markdown(f"~~{label}~~ ❌ *(Ocupada)*")

        st.markdown("---")
        
        # 4. Mostrar métricas de cobro en tiempo real
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total a Pagar", f"${precio_total:.2f}")
        with col2:
            st.metric("Consumo Mínimo Total", f"${consumo_total:.2f}")

        # 5. Número de asistentes calculado automáticamente
        cantidad_personas = st.number_input(
            "Número total de asistentes (calculado por capacidad de mesas)", 
            min_value=1, 
            value=max(1, capacidad_total)
        )
        
        tipo_celebracion = st.selectbox("Tipo de celebración", ["Ninguna", "Cumpleaños", "Aniversario", "Despedida", "Otro"])

        st.markdown("---")
        st.markdown("### 💳 Comprobante de Pago")
        archivo_comprobante = st.file_uploader("Adjunta la captura de tu transferencia o depósito", type=['png', 'jpg', 'jpeg'])

        if st.button("Confirmar Reserva", type="primary"):
            if not mesas_seleccionadas:
                st.error("Debes seleccionar al menos una mesa.")
                return
            
            if not archivo_comprobante:
                st.error("⚠️ Por favor, adjunta tu comprobante de pago para finalizar.")
                return

            # Preparamos los datos en formato Form Data
            import json
            datos_reserva = {
                "evento_id": str(evento_id),
                "mesas_ids": json.dumps(mesas_seleccionadas),
                "cliente_id": str(cliente_id),
                "cantidad_personas": str(cantidad_personas),
                "tipo_celebracion": str(tipo_celebracion)
            }

            # Preparamos el archivo adjunto
            files = {
                "file": (archivo_comprobante.name, archivo_comprobante, archivo_comprobante.type)
            }

            res_post = requests.post(f"{api_url}/reservas/con_comprobante/", data=datos_reserva, files=files)
            
            if res_post.status_code in [200, 201]:
                st.success("¡Reserva y comprobante enviados con éxito! Quedará pendiente de validación.")
                st.balloons()
            else:
                try:
                    error_msg = res_post.json().get('detail', res_post.text)
                except:
                    error_msg = res_post.text
                st.error(f"Error al procesar la reserva: {error_msg}")

    except Exception as e:
        st.error(f"Error de conexión: {e}")