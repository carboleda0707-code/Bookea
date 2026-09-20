import streamlit as st
import requests

def render_asignar_mesas(API_URL):
    st.subheader("Asignar Mesas y Precios a Eventos")
    
    # 1. Obtener la lista de eventos desde la API para mostrarlos amigablemente
    try:
        res_eventos = requests.get(f"{API_URL}/reservas/eventos/")
        eventos = res_eventos.json() if res_eventos.status_code == 200 else []
    except Exception:
        eventos = []

    # 2. Obtener la lista de mesas registradas
    try:
        res_mesas = requests.get(f"{API_URL}/reservas/mesas/")
        mesas = res_mesas.json() if res_mesas.status_code == 200 else []
    except Exception:
        mesas = []

    if not eventos:
        st.warning("⚠️ No hay eventos registrados. Por favor, crea un evento primero.")
        return

    if not mesas:
        st.warning("⚠️ No hay mesas registradas. Por favor, crea mesas primero.")
        return

    # Diccionarios para asociar el texto visible con su respectivo ID
    opciones_eventos = {f"ID: {e['id']} - {e['nombre_evento']} ({e['fecha_hora']})": e['id'] for e in eventos}
    opciones_mesas = {f"ID: {m['id']} - Mesa: {m['numero_mesa']} (Capacidad: {m['capacidad']})": m['id'] for m in mesas}

    # Pestañas para separar la creación de la modificación
    tab1, tab2 = st.tabs(["➕ Nueva Asignación", "✏️ Modificar Asignación Existente"])

    with tab1:
        with st.form("form_asignar"):
            evento_seleccionado = st.selectbox("Selecciona el Evento", options=list(opciones_eventos.keys()), key="new_ev")
            evento_id = opciones_eventos[evento_seleccionado]

            mesa_seleccionada = st.selectbox("Selecciona la Mesa", options=list(opciones_mesas.keys()), key="new_me")
            mesa_id = opciones_mesas[mesa_seleccionada]

            precio = st.number_input("Precio de la Reserva ($)", min_value=0.0, value=20.0, step=5.0, key="new_pr")
            consumo_minimo = st.number_input("Consumo Mínimo Obligatorio ($)", min_value=0.0, value=10.0, step=5.0, key="new_cm")
            
            submit = st.form_submit_button("Vincular Mesa al Evento")
            
            if submit:
                if consumo_minimo < 10.0:
                    st.error("⚠️ El consumo mínimo obligatorio debe ser mayor o igual a $10.0[cite: 2].")
                else:
                    payload = {
                        "evento_id": int(evento_id),
                        "mesa_id": int(mesa_id),
                        "precio": float(precio),
                        "consumo_minimo": float(consumo_minimo)
                    }
                    res = requests.post(f"{API_URL}/precio-evento-mesa/", json=payload)
                    if res.status_code == 200:
                        st.success("¡Mesa vinculada al evento con éxito!")
                        st.rerun()
                    else:
                        st.error(f"Error al vincular: {res.text}")

    with tab2:
        st.info("💡 Solo puedes modificar asignaciones que aún no tengan reservas registradas.")
        
        # Obtener asignaciones actuales
        try:
            res_asig = requests.get(f"{API_URL}/precio-evento-mesa/")
            asignaciones = res_asig.json() if res_asig.status_code == 200 else []
        except Exception:
            asignaciones = []

        if not asignaciones:
            st.info("No hay asignaciones registradas para modificar.")
        else:
            opciones_asignaciones = {
                f"ID Asignación: {a['id']} | Evento: {a.get('nombre_evento', a['evento_id'])} | Mesa: {a.get('numero_mesa', a['mesa_id'])}": a 
                for a in asignaciones
            }

            asig_seleccionada_key = st.selectbox("Selecciona la Asignación a Modificar", options=list(opciones_asignaciones.keys()))
            asig_data = opciones_asignaciones[asig_seleccionada_key]

            with st.form("form_modificar"):
                # Se ajusta a 'precio_reserva' según la estructura de la API
                val_precio = float(asig_data.get('precio_reserva', asig_data.get('precio', 20.0)))
                val_consumo = float(asig_data.get('consumo_minimo', 10.0))

                nuevo_precio = st.number_input("Nuevo Precio de la Reserva ($)", min_value=0.0, value=val_precio, step=5.0, key="mod_pr")
                nuevo_consumo = st.number_input("Nuevo Consumo Mínimo Obligatorio ($)", min_value=0.0, value=val_consumo, step=5.0, key="mod_cm")
                
                submit_mod = st.form_submit_button("Actualizar Asignación")
                
                if submit_mod:
                    if nuevo_consumo < 10.0:
                        st.error("⚠️ El consumo mínimo obligatorio debe ser mayor o igual a $10.0[cite: 2].")
                    else:
                        payload_mod = {
                            "precio": float(nuevo_precio),
                            "consumo_minimo": float(nuevo_consumo)
                        }
                        res_update = requests.put(f"{API_URL}/precio-evento-mesa/{asig_data['id']}", json=payload_mod)
                        if res_update.status_code == 200:
                            st.success("¡Asignación actualizada con éxito!")
                            st.rerun()
                        else:
                            st.error(f"⚠️ No se pudo modificar (es posible que ya tenga reservas asociadas): {res_update.text}")

    st.markdown("---")
    st.subheader("Asignaciones Actuales (Precios y Mesas Vinculadas)")
    
    if asignaciones or 'asignaciones' in locals():
        if asignaciones:
            st.dataframe(asignaciones, use_container_width=True)
        else:
            st.info("No hay mesas asignadas a eventos todavía.")
    else:
        st.error("No se pudo cargar el listado de asignaciones.")