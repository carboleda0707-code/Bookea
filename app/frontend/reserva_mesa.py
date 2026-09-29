import streamlit as st
import requests
import json


def render_seleccion_mesas(api_url: str, evento_id: int, cliente_id: int):
    st.markdown("### 🪑 Selección de Mesas por Zona y Local")
    
    try:
        # 1. Info del evento y extracción segura del local_id
        local_ev_id = None
        try:
            res_evento = requests.get(f"{api_url}/eventos/{evento_id}")
            if res_evento.status_code == 200:
                evento = res_evento.json()
                if evento:
                    nombre_ev = evento.get('nombre_evento') or evento.get('titulo', 'Evento')
                    fecha_ev = evento.get('fecha_hora', '')
                    local_ev_id = evento.get('local_id') or evento.get('local')
                    st.markdown(f"📅 **Evento:** {nombre_ev} | 🕒 **Fecha:** {fecha_ev}")
                    st.markdown("---")
        except Exception as e:
            st.warning(f"No se pudo cargar la info del evento: {e}")

        # 2. Consultar mesas disponibles
        response = requests.get(f"{api_url}/reservas/mesas-disponibles/{evento_id}")
        if response.status_code != 200:
            st.error(f"Error al cargar las mesas disponibles. Código HTTP: {response.status_code}")
            return
            
        mesas = response.json()
        if not mesas:
            st.warning("No hay mesas configuradas para este evento.")
            return

        # Inicializar el carrito en session_state si no existe
        if "carrito_reservas" not in st.session_state:
            st.session_state.carrito_reservas = {} # {mesa_id: {"tipo": "mesa/pase", "precio": X, "consumo": Y, "capacidad": Z, "numero": N}}

        # 3. Obtener el catálogo completo de zonas dinámicamente
        zonas_dict = {}
        try:
            res_zonas = requests.get(f"{api_url}/zonas/")
            if res_zonas.status_code == 200:
                for z in res_zonas.json():
                    z_id = z.get("id") or z.get("zona_id")
                    if z_id:
                        zonas_dict[int(z_id)] = {
                            "nombre_zona": z.get("nombre_zona") or z.get("nombre") or f"Zona {z_id}",
                            "descripcion": z.get("descripcion") or "",
                            "local_id": z.get("local_id")
                        }
        except Exception:
            pass

        def obtener_datos_zona_local(item):
            zona_id = item.get("zona_id")
            nombre_zona = "General"
            descripcion_zona = ""
            local_mesa_id = item.get("local_id")

            if zona_id and int(zona_id) in zonas_dict:
                info_z = zonas_dict[int(zona_id)]
                nombre_zona = info_z["nombre_zona"]
                descripcion_zona = info_z["descripcion"]
                if not local_mesa_id:
                    local_mesa_id = info_z["local_id"]
            
            return str(nombre_zona).strip(), str(descripcion_zona).strip(), local_mesa_id

        # 4. Filtrar mesas válidas
        mesas_validas = []
        for item in mesas:
            nombre_zona, descripcion_zona, local_mesa_id = obtener_datos_zona_local(item)
            if descripcion_zona.lower() == "libre":
                continue
            if local_ev_id and local_mesa_id and str(local_ev_id) != str(local_mesa_id):
                continue
            mesas_validas.append(item)

        if not mesas_validas:
            st.warning("⚠️ No hay mesas válidas disponibles.")
            return

        # 5. Generar opciones del selectbox (Recorremos sin filtrar para extraer todas las zonas)
        zonas_opciones_dict = {}
        for item in mesas_validas:
            nombre_zona, descripcion_zona, _ = obtener_datos_zona_local(item)
            etiqueta = f"{nombre_zona} — {descripcion_zona}" if (descripcion_zona and descripcion_zona.lower() != "libre") else nombre_zona
            zonas_opciones_dict[etiqueta] = nombre_zona

        opciones_disponibles = list(zonas_opciones_dict.keys())
        if not opciones_disponibles:
            opciones_disponibles = ["General"]

        # Creamos el selectbox y definimos zona_actual
        zona_seleccionada_label = st.selectbox("📍 Selecciona una Zona para ver sus mesas:", opciones_disponibles)
        zona_actual = zonas_opciones_dict.get(zona_seleccionada_label, zona_seleccionada_label)
        
        st.markdown(f"#### 🏷️ Mesas en la zona: **{zona_seleccionada_label}**")

        mesas_en_zona = 0

        # 6. Segundo bucle: Recorremos las mesas aplicando los filtros de zona y disponibilidad
        for item in mesas_validas:
            zona_mesa, _, _ = obtener_datos_zona_local(item)
            if zona_mesa.lower() != zona_actual.lower():
                continue

            disponible = item["disponible"]
            
            # Ocultar completamente las mesas que ya están ocupadas
            if not disponible:
                continue

            mesas_en_zona += 1
            mesa_id = item["mesa_id"]
            numero_raw = str(item.get("numero_mesa", ""))
            
            # Limpiar el texto para evitar duplicidades
            numero = numero_raw.replace("Mesa", "").replace("mesa", "").strip(" #-_")
            if not numero:
                numero = numero_raw

            capacidad = int(item.get("capacidad", 1))
            precio = float(item.get("precio_reserva") or 0.0)
            consumo = float(item.get("consumo_minimo") or 0.0)

            # DETECCIÓN: ¿Es un Pase General?
            if "pase" in numero_raw.lower():
                st.markdown(f"🎟️ **Pase General ({numero_raw})** — 💵 Precio c/u: \({precio:.2f} | 🍷 Consumo c/u:\){consumo:.2f}")
                
                qty_actual = st.session_state.carrito_reservas.get(mesa_id, {}).get("cantidad", 0)
                cantidad_pases = st.number_input(
                    f"Cantidad de pases que deseas comprar:",
                    min_value=0,
                    max_value=100,
                    value=qty_actual,
                    key=f"pase_qty_{mesa_id}"
                )
                
                if cantidad_pases > 0:
                    st.session_state.carrito_reservas[mesa_id] = {
                        "tipo": "pase",
                        "numero": numero_raw,
                        "cantidad": cantidad_pases,
                        "precio": precio * cantidad_pases,
                        "consumo": consumo * cantidad_pases,
                        "capacidad": cantidad_pases
                    }
                else:
                    if mesa_id in st.session_state.carrito_reservas:
                        del st.session_state.carrito_reservas[mesa_id]
            else:
                # Mesa física por zona
                label = f"Mesa **#{numero}**  |  👥 Capacidad: {capacidad} pers.  |  💵 Reserva: \({precio:.2f}  |  🍷 Consumo Mín:\){consumo:.2f}"

                ya_seleccionada = mesa_id in st.session_state.carrito_reservas
                seleccionada = st.checkbox(label, value=ya_seleccionada, key=f"mesa_chk_{mesa_id}")
                
                if seleccionada:
                    st.session_state.carrito_reservas[mesa_id] = {
                        "tipo": "mesa",
                        "numero": numero,
                        "cantidad": 1,
                        "precio": precio,
                        "consumo": consumo,
                        "capacidad": capacidad
                    }
                else:
                    if mesa_id in st.session_state.carrito_reservas:
                        del st.session_state.carrito_reservas[mesa_id]
        else:
                st.markdown(f"~~{label}~~ ❌ *(Ocupada)*")

        if mesas_en_zona == 0:
            st.info("No hay mesas registradas en esta zona para este evento.")

        # ==========================================
        # 7. CÁLCULO GLOBAL BASADO EN EL CARRITO (SESSION_STATE)
        # ==========================================
        precio_total = sum(item["precio"] for item in st.session_state.carrito_reservas.values())
        consumo_total = sum(item["consumo"] for item in st.session_state.carrito_reservas.values())
        capacidad_total = sum(item["capacidad"] for item in st.session_state.carrito_reservas.values())

        st.markdown("### 📊 Resumen Acumulado de tu Selección")
        
        # Mostrar elementos seleccionados actualmente para que el usuario sepa qué lleva acumulado
        if st.session_state.carrito_reservas:
            items_desc = []
            for m_id, dat in st.session_state.carrito_reservas.items():
                if dat["tipo"] == "pase":
                    items_desc.append(f"🎟️ {dat['cantidad']}x {dat['numero']}")
                else:
                    items_desc.append(f"🪑 Mesa #{dat['numero']}")
            st.info(" | ".join(items_desc))

        mcol1, mcol2 = st.columns(2)
        with mcol1:
            st.metric("Total a Pagar (Reserva)", f"${precio_total:.2f}")
        with mcol2:
            st.metric("Total Consumo Mínimo", f"${consumo_total:.2f}")

        # 7.2 Validar número de Asistentes
        cantidad_personas = st.number_input("Número total de asistentes", min_value=1, value=max(1, capacidad_total))
        tipo_celebracion = st.selectbox("Tipo de celebración", ["Ninguna", "Cumpleaños", "Aniversario", "Despedida", "Otro"])

        st.markdown("---")
        st.markdown("### 💳 Comprobante de Pago")
        archivo_comprobante = st.file_uploader("Adjunta la captura de tu transferencia o depósito", type=['png', 'jpg', 'jpeg'])

        if st.button("Confirmar Reserva", type="primary", use_container_width=True):
            if not st.session_state.carrito_reservas:
                st.error("⚠️ Debes seleccionar al menos una mesa o pase.")
                return
            if not archivo_comprobante:
                st.error("⚠️ Por favor, adjunta tu comprobante de pago para finalizar.")
                return

            # Construir la lista de IDs únicos para evitar el conflicto de unicidad en la BD
            mesas_ids_final = []
            for m_id, dat in st.session_state.carrito_reservas.items():
                if m_id not in mesas_ids_final:
                    mesas_ids_final.append(m_id)

            datos_reserva = {
                "evento_id": str(evento_id),
                "mesas_ids": json.dumps(mesas_ids_final),
                "cliente_id": str(cliente_id),
                "cantidad_personas": str(cantidad_personas),
                "tipo_celebracion": str(tipo_celebracion)
            }
            files = {"file": (archivo_comprobante.name, archivo_comprobante, archivo_comprobante.type)}

            res_post = requests.post(f"{api_url}/reservas/con_comprobante/", data=datos_reserva, files=files)
            if res_post.status_code in [200, 201]:
                st.success("¡Reserva y comprobante enviados con éxito!")
                del st.session_state.carrito_reservas
                st.balloons()
            else:
                try:
                    error_msg = res_post.json().get('detail', res_post.text)
                except:
                    error_msg = res_post.text
                st.error(f"Error al procesar la reserva: {error_msg}")

    except Exception as e:
        st.error(f"Error de conexión o ejecución: {e}")
        
