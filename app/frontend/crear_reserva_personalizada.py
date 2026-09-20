import streamlit as st
import requests
import json
import datetime
import urllib.parse

def render_crear_reserva_personalizada(API_URL, cliente_id):
    st.header("🎉 Crea tu Celebración y Reserva tu Mesa")
    st.write("Selecciona los detalles de tu evento, elige tus mesas y valida la capacidad en tiempo real.")

    # 0. Recuperar el ID del local actual seleccionado en la cartelera
    id_local_actual = st.session_state.get("id_local_actual", None)

    # 1. Cargamos los eventos disponibles filtrados estrictamente por el local actual
    try:
        url_eventos = f"{API_URL}/reservas/eventos/"
        params = {}
        if id_local_actual:
            params["local_id"] = id_local_actual
        params["incluir_pendientes"] = "true"

        resp_eventos = requests.get(url_eventos, params=params, timeout=5)
        lista_bruta = resp_eventos.json() if resp_eventos.status_code == 200 else []
        
        lista_eventos = []
        for ev in lista_bruta:
            ev_local = ev.get("local_id")
            if id_local_actual and ev_local and int(ev_local) != int(id_local_actual):
                continue
            lista_eventos.append(ev)
    except Exception:
        lista_eventos = []

    evento_seleccionado_id = None
    if lista_eventos:
        opciones_eventos = {}
        for ev in lista_eventos:
            nombre_ev = ev.get('nombre_evento', '')
            if str(nombre_ev).strip().lower() == "tu evento":
                label_opcion = "Tu Evento"
            else:
                fecha_corta = ev.get('fecha_hora', '').split('T')[0]
                label_opcion = f"{nombre_ev} (Fecha: {fecha_corta})"

        for ev in lista_eventos:
            nombre_ev = str(ev.get('nombre_evento', '')).strip().lower()
            if nombre_ev == "tu evento" or "tu evento" in nombre_ev:
                evento_seleccionado_id = ev.get("id")
                break
        if not evento_seleccionado_id and lista_eventos:
            evento_seleccionado_id = lista_eventos[0].get("id")

    # 2. Carga de mesas disponibles en tiempo real
    mesas_disponibles = []
    mapa_mesas = {}

    if evento_seleccionado_id:
        try:
            resp_mesas = requests.get(f"{API_URL}/reservas/mesas-disponibles/{evento_seleccionado_id}", timeout=5)
            if resp_mesas.status_code == 200:
                mesas = resp_mesas.json()
                mesas_disponibles = [m for m in mesas if m.get("disponible") is True or m.get("disponible") is None]
        except Exception:
            pass

    if not mesas_disponibles and lista_eventos:
        for ev in lista_eventos:
            ev_id = ev.get("id")
            if ev_id:
                try:
                    resp_alt = requests.get(f"{API_URL}/reservas/mesas-disponibles/{ev_id}", timeout=3)
                    if resp_alt.status_code == 200:
                        mesas_alt = resp_alt.json()
                        if mesas_alt:
                            mesas_disponibles = [m for m in mesas_alt if m.get("disponible") is True or m.get("disponible") is None]
                            if mesas_disponibles:
                                break
                except Exception:
                    continue

    if not mesas_disponibles:
        st.error("❌ No se pudieron cargar las mesas. Asegúrate de haber creado mesas y precios en el panel de administración del dueño.")
        mesas_ids_elegidas = []
    else:
        mapa_mesas = {m["mesa_id"]: m for m in mesas_disponibles}
        opciones_mesas = {
            m["mesa_id"]: f"Mesa #{m.get('numero_mesa')} - Capacidad: {m.get('capacidad')} - Precio: ${m.get('precio_reserva', 0)}" 
            for m in mesas_disponibles
        }
        
        st.markdown("### 2️⃣ Selección de Mesas, Precios y Capacidad")
        mesas_ids_elegidas = st.multiselect(
            "Selecciona tu(s) Mesa(s):", 
            options=list(opciones_mesas.keys()), 
            format_func=lambda x: opciones_mesas[x],
            key="multiselect_mesas_dinamico"
        )

    cantidad_personas = st.number_input("Cantidad Total de Personas Asistentes:", min_value=1, max_value=100, value=2, step=1, key="num_personas_dinamico")

    # 🛡️ VALIDACIÓN EN TIEMPO REAL
    capacidad_total_mesas = sum([mapa_mesas[m_id].get("capacidad", 4) for m_id in mesas_ids_elegidas]) if mesas_ids_elegidas else 0

    if mesas_ids_elegidas:
        if cantidad_personas > capacidad_total_mesas:
            st.warning(f"⚠️ **Atención:** La capacidad sumada de tus mesas seleccionadas es de **{capacidad_total_mesas} personas**, pero indicaste **{cantidad_personas} asistentes**. Selecciona más mesas o reduce los invitados.")
        else:
            st.success(f"✅ Capacidad óptima: Tus mesas soportan hasta {capacidad_total_mesas} personas para {cantidad_personas} asistentes.")
            
        # 💰 RESUMEN FINANCIERO
        total_precio_mesas = sum([mapa_mesas[m_id].get("precio_reserva", 0) for m_id in mesas_ids_elegidas])
        total_consumo_min = sum([mapa_mesas[m_id].get("consumo_minimo", 0) for m_id in mesas_ids_elegidas])
        
        st.info(
            f"📊 **Resumen Financiero de la Selección:**\n\n"
            f"• **Total a Pagar (Reserva):** ${total_precio_mesas:.2f}\n"
            f"• **Consumo Mínimo Total:** ${total_consumo_min:.2f}"
        )

    st.markdown("---")

    # Formulario para envío de datos
    with st.form("form_reserva_completa_cliente"):
        st.markdown("### 📝 Datos de la Celebración y Pago")
        nombre_evento = st.text_input("Nombre de tu Celebración personalizada (ej: Cumpleaños de Sandra)", placeholder="Cumpleaños / Aniversario")
        tipo_celebracion = st.text_input("Tipo de Celebración:", value="Cumpleaños")
        descripcion = st.text_area("Dedicatoria o Mensaje (Opcional)", placeholder="¡Ven a celebrar conmigo!")
        
        col_f, col_h = st.columns(2)
        with col_f:
            fecha = st.date_input(
                "Fecha de la Celebración",
                value=datetime.date.today(),
                min_value=datetime.date.today()
            )
        with col_h:
            hora = st.time_input("Hora de inicio", value=datetime.time(20, 0))
            
        st.markdown("📱 **Foto o Flyer para tu Celebración**")
        generar_reel = st.checkbox(
            "✨ Modo Inteligente para Reel (Centrar con fondo elegante sin recortar)", 
            value=True
        )

        foto_flyer = st.file_uploader("Sube tu foto o imagen conmemorativa", type=["jpg", "jpeg", "png"])
        
        st.markdown("### 💳 Comprobante de Pago")
        archivo_comprobante = st.file_uploader("Sube tu comprobante de pago", type=["jpg", "jpeg", "png", "pdf"], key="comprobante_cliente")

        submit_total = st.form_submit_button("🚀 Enviar Solicitud de Celebración y Reserva")
        
        if submit_total:
            if not nombre_evento:
                st.warning("Por favor, ingresa un nombre para tu celebración.")
                return
            if not mesas_ids_elegidas:
                st.error("Debes seleccionar al menos una mesa disponible.")
                return
            if cantidad_personas > capacidad_total_mesas:
                st.error("❌ No puedes enviar la reserva: La cantidad de personas supera estrictamente la capacidad de las mesas seleccionadas.")
                return
            if not archivo_comprobante:
                st.warning("Por favor, adjunta tu comprobante de pago.")
                return

            fecha_hora_str = f"{fecha}T{hora.strftime('%H:%M:%S')}"
            
            # Recuperamos el correo del cliente desde la sesión para vincularlo como creador
            correo_cliente_actual = st.session_state.get("user_email", st.session_state.get("email", ""))
            
            data_evento = {
                "local_id": str(id_local_actual) if id_local_actual else "1", 
                "nombre_evento": nombre_evento,
                "artista_orquesta": f"Cliente ID: {cliente_id} (Reserva de Celebración)",
                "fecha_hora": fecha_hora_str,
                "descripcion": descripcion if descripcion else "Celebración personalizada de cliente",
                "estado": "pendiente",
                "creador": correo_cliente_actual  # 👈 Vinculación para privacidad del evento confirmado
            }
            
            files_evento = {"file": (foto_flyer.name, foto_flyer.getvalue(), foto_flyer.type)} if foto_flyer else None

            try:
                # Paso 1: Creamos el evento (en estado pendiente)
                resp_evento = requests.post(f"{API_URL}/reservas/eventos/", data=data_evento, files=files_evento, timeout=15)
                
                if resp_evento.status_code in [200, 201]:
                    evento_data = resp_evento.json()
                    nuevo_evento_id = evento_data.get("id") or evento_data.get("evento_id")
                    
                    # Paso 2: Creamos la reserva vinculada
                    payload_reserva = {
                        "evento_id": int(nuevo_evento_id),
                        "cliente_id": int(cliente_id),
                        "cantidad_personas": int(cantidad_personas),
                        "tipo_celebracion": tipo_celebracion,
                        "mesas_ids": json.dumps([int(m_id) for m_id in mesas_ids_elegidas])
                    }

                    files_comprobante = {
                        "file": (archivo_comprobante.name, archivo_comprobante.getvalue(), archivo_comprobante.type)
                    }

                    resp_reserva = requests.post(f"{API_URL}/reservas/con_comprobante/", data=payload_reserva, files=files_comprobante, timeout=15)

                    if resp_reserva.status_code in [200, 201]:
                        st.success("🎉 ¡Tu solicitud de celebración y reserva ha sido enviada con éxito! Está en revisión por el establecimiento. Una vez el dueño verifique el pago, la aprobará y recibirás tu confirmación con códigos QR.")
                        
                        celular_administrador = ""
                        try:
                            resp_cfg = requests.get(f"{API_URL}/configuracion/", timeout=3)
                            if resp_cfg.status_code == 200:
                                cfg_data = resp_cfg.json()
                                celular_administrador = cfg_data.get("celular_remitente", "").strip()
                        except Exception:
                            pass

                        numero_admin_limpio = ''.join(filter(str.isdigit, celular_administrador))

                        if numero_admin_limpio:
                            nombres_mesas = ', '.join([str(mapa_mesas[m_id].get('numero_mesa')) for m_id in mesas_ids_elegidas])
                            texto_alerta_admin = (
                                f"🔔 *NUEVA RESERVA PENDIENTE DE APROBACIÓN* 🔔\n\n"
                                f"Hola Admin, el cliente ha enviado una solicitud de celebración que requiere tu revisión:\n"
                                f"🎉 *Evento:* {nombre_evento}\n"
                                f"📅 *Fecha:* {fecha} a las {hora}\n"
                                f"👥 *Asistentes:* {cantidad_personas}\n"
                                f"🪑 *Mesa(s):* #{nombres_mesas}\n"
                                f"🆔 *Cliente ID:* {cliente_id}\n\n"
                                f"Por favor ingresa al módulo 'Control de Reservas' para verificar el comprobante, aprobar el evento y enviar los QR."
                            )
                            
                            whatsapp_admin_url = f"https://wa.me/{numero_admin_limpio}?text={urllib.parse.quote(texto_alerta_admin)}"
                            
                            st.markdown("### 📲 Notificar al Administrador")
                            st.markdown(f"Haz clic para enviar la alerta rápida de WhatsApp al dueño: \n\n [<img src='https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg' width='25' style='vertical-align: middle;'/> **Notificar Nueva Reserva al Administrador**]({whatsapp_admin_url})", unsafe_allow_html=True)
                        else:
                            st.warning("⚠️ El número de WhatsApp del administrador no está configurado en el sistema. Por favor ve al panel de configuración e ingresa el número.")
                        
                        st.balloons()
                    else:
                        st.error(f"Se creó la solicitud de evento pero falló el envío de la reserva/comprobante: {resp_reserva.text}")
                else:
                    st.error(f"Error al iniciar la solicitud de celebración: {resp_evento.text}")
            except Exception as e:
                st.error(f"Error de conexión: {e}")