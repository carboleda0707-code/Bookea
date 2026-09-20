import os
import shutil
import uuid
import json
import qrcode

from sqlalchemy import text 

from fastapi import APIRouter, Depends, HTTPException, status, File, Form, UploadFile
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models, schemas
from app.utils.email import enviar_correo_smtp

from pydantic import BaseModel
from typing import Optional

class AprobarReservaRequest(BaseModel):
    mensaje_personalizado: Optional[str] = None


QRS_DIR = "app/static/uploads/qrs"
os.makedirs(QRS_DIR, exist_ok=True)

COMPROBANTES_DIR = "app/static/uploads/comprobantes"
os.makedirs(COMPROBANTES_DIR, exist_ok=True)

router = APIRouter(prefix="/reservas", tags=["Reservas"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

UPLOAD_DIR = "app/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/evento/{evento_id}")
def obtener_detalle_evento(evento_id: int, db: Session = Depends(get_db)):
    evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return {
        "nombre_evento": evento.nombre_evento,
        "fecha_hora": evento.fecha_hora.strftime("%d/%m/%Y %H:%M")
    }

@router.post("/eventos/")
def crear_evento(
    local_id: int = Form(...),
    nombre_evento: str = Form(...),
    artista_orquesta: str = Form(None),
    fecha_hora: str = Form(...),
    descripcion: str = Form(None),
    estado: str = Form("activo"),  # Por defecto activo si lo crea el propietario
    creador: str = Form(None),     # Nuevo campo para almacenar el creador/correo
    file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    try:
        if nombre_evento.strip().lower() == "tu evento":
            existente = db.query(models.Evento).filter(
                models.Evento.local_id == local_id,
                models.Evento.nombre_evento.ilike("tu evento")
            ).first()
            
            if existente:
                return {
                    "mensaje": "La plantilla 'Tu Evento' ya existe para este local.",
                    "id": existente.id
                }

        nombre_archivo = None
        if file and file.filename:
            nombre_archivo = file.filename
            file_path = os.path.join(UPLOAD_DIR, nombre_archivo)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        fecha_hora_dt = datetime.fromisoformat(fecha_hora)

        resultado = db.execute(text("""
            SELECT COALESCE(MIN(t1.id + 1), 1) 
            FROM eventos t1 
            LEFT JOIN eventos t2 ON t1.id + 1 = t2.id 
            WHERE t2.id IS NULL;
        """)).fetchone()
        
        nuevo_id = resultado[0]

        nuevo_evento = models.Evento(
            id=nuevo_id,
            local_id=local_id,
            nombre_evento=nombre_evento,
            artista_orquesta=artista_orquesta,
            fecha_hora=fecha_hora_dt,
            descripcion=descripcion,
            imagen=nombre_archivo,
            estado=estado,
            creador=creador  # Guardamos el correo o creador del evento
        )
        
        db.add(nuevo_evento)
        db.commit()
        db.refresh(nuevo_evento)
        
        return {"mensaje": "¡Evento creado con éxito!", "id": nuevo_evento.id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error al procesar: {str(e)}")


@router.get("/eventos/")
def listar_eventos(
    local_id: int = None, 
    usuario_id: int = None, 
    incluir_pendientes: bool = True, # Forzado en True para evitar bloqueos por estado
    cliente_email: str = None,  
    db: Session = Depends(get_db)
):
    query = db.query(models.Evento).join(models.Local, models.Evento.local_id == models.Local.id)
    
    if local_id is not None:
        query = query.filter(models.Evento.local_id == local_id)
    elif usuario_id is not None:
        query = query.filter(models.Local.propietario_id == usuario_id)
        
    # Se eliminan los filtros estrictos de estado para asegurar que la API devuelva todos los registros del local
    eventos = query.all()
    
    eventos_filtrados = []
    encontro_plantilla = False
    
    for ev in eventos:
        es_plantilla = ev.nombre_evento and ev.nombre_evento.strip().lower() == "tu evento"
        if es_plantilla:
            if not encontro_plantilla:
                eventos_filtrados.append(ev)
                encontro_plantilla = True
        else:
            eventos_filtrados.append(ev)
            
    return eventos_filtrados

@router.get("/mesas-disponibles/{evento_id}")
def obtener_mesas_disponibles(evento_id: int, db: Session = Depends(get_db)):
    todas_las_mesas = db.query(models.Mesa).all()
    
    reservas_activas = db.query(models.Reserva).filter(
        models.Reserva.evento_id == evento_id,
        models.Reserva.estado_reserva != "cancelada"
    ).all()
    
    lista_reservadas = []
    for r in reservas_activas:
        for m in r.mesas:
            lista_reservadas.append(m.id)
            
    precios_evento = {
        item.mesa_id: item for item in db.query(models.PrecioEventoMesa).filter(
            models.PrecioEventoMesa.evento_id == evento_id
        ).all()
    }
    
    if not precios_evento and evento_id != 1:
        precios_evento = {
            item.mesa_id: item for item in db.query(models.PrecioEventoMesa).filter(
                models.PrecioEventoMesa.evento_id == 1
            ).all()
        }
    
    resultado = []
    for mesa in todas_las_mesas:
        precio_info = precios_evento.get(mesa.id)
        
        p_reserva = float(precio_info.precio_reserva) if precio_info and precio_info.precio_reserva > 0 else 25.00
        p_consumo = float(precio_info.consumo_minimo) if precio_info and precio_info.consumo_minimo > 0 else 15.00

        resultado.append({
            "mesa_id": mesa.id,
            "numero_mesa": mesa.numero_mesa,
            "capacidad": mesa.capacidad,
            "precio_reserva": p_reserva,
            "consumo_minimo": p_consumo,
            "disponible": mesa.id not in lista_reservadas
        })
        
    return resultado

@router.get("/")
def listar_reservas(local_id: int = None, usuario_id: int = None, db: Session = Depends(get_db)):
    query = db.query(models.Reserva, models.UsuarioFinal, models.Evento).join(
        models.UsuarioFinal, models.Reserva.cliente_id == models.UsuarioFinal.id
    ).join(
        models.Evento, models.Reserva.evento_id == models.Evento.id
    ).join(
        models.Local, models.Evento.local_id == models.Local.id
    )
    
    if local_id is not None:
        query = query.filter(models.Evento.local_id == local_id)
    elif usuario_id is not None:
        query = query.filter(models.Local.propietario_id == usuario_id)
        
    resultados = query.all()

    lista_final = []
    for reserva, cliente, evento in resultados:
        numero_mesa_str = ", ".join([m.numero_mesa for m in reserva.mesas]) if reserva.mesas else "N/A"
        
        lista_final.append({
            "id": reserva.id,
            "evento_id": reserva.evento_id,
            "nombre_evento": getattr(evento, "nombre_evento", "Evento General"),
            "mesa_id": numero_mesa_str,
            "cliente_id": reserva.cliente_id,
            "cliente_nombre": cliente.nombre,
            "cliente_correo": cliente.email,
            "cliente_telefono": cliente.telefono,
            "cantidad_personas": reserva.cantidad_personas,
            "tipo_celebracion": reserva.tipo_celebracion,
            "codigo_reserva": reserva.codigo_reserva,
            "estado_reserva": reserva.estado_reserva,
            "comprobante_pago": reserva.comprobante_pago,
            "creado_en": reserva.creado_en,
            "mensaje_personalizado": getattr(reserva, "mensaje_personalizado", None)
        })
        
    return lista_final

@router.post("/con_comprobante/")
async def crear_reserva_con_pago(
    evento_id: int = Form(...),
    cliente_id: int = Form(...),
    cantidad_personas: int = Form(...),
    tipo_celebracion: str = Form(None),
    mesas_ids: str = Form(...), 
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    cliente_existe = db.query(models.UsuarioFinal).filter(models.UsuarioFinal.id == cliente_id).first()
    if not cliente_existe:
        raise HTTPException(
            status_code=400, 
            detail=f"El cliente con ID {cliente_id} no está registrado en la base de datos."
        )
    
    lista_mesas = json.loads(mesas_ids)
    
    try:
        reservas_existentes = db.query(models.Reserva).filter(
            models.Reserva.evento_id == evento_id,
            models.Reserva.estado_reserva != "cancelada"
        ).all()
        
        mesas_ocupadas_ids = []
        for r in reservas_existentes:
            for m in r.mesas:
                if m.id in lista_mesas:
                    mesas_ocupadas_ids.append(m.id)
                    
        if mesas_ocupadas_ids:
            raise HTTPException(
                status_code=400,
                detail=f"Lo sentimos, las mesas con ID {list(set(mesas_ocupadas_ids))} acaban de ser reservadas por otro usuario."
            )

        nombre_archivo = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = os.path.join(COMPROBANTES_DIR, nombre_archivo)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        codigo_unico = f"RES-{uuid.uuid4().hex[:6].upper()}"
        
        nueva_reserva = models.Reserva(
            evento_id=evento_id,
            cliente_id=cliente_id,
            cantidad_personas=cantidad_personas,
            tipo_celebracion=tipo_celebracion,
            codigo_reserva=codigo_unico,
            estado_reserva="pendiente_pago",
            comprobante_pago=nombre_archivo,
            creado_en=datetime.now()
        )
        db.add(nueva_reserva)
        db.flush()
        
        mesas_objs = db.query(models.Mesa).filter(models.Mesa.id.in_(lista_mesas)).all()
        for mesa in mesas_objs:
            nueva_reserva.mesas.append(mesa)
            
        for mesa_id in lista_mesas:
            existe_asignacion = db.query(models.PrecioEventoMesa).filter(
                models.PrecioEventoMesa.evento_id == evento_id,
                models.PrecioEventoMesa.mesa_id == mesa_id
            ).first()
            
            if not existe_asignacion:
                nueva_asignacion = models.PrecioEventoMesa(
                    evento_id=evento_id,
                    mesa_id=mesa_id,
                    precio_reserva=0.0,
                    consumo_minimo=0.0
                )
                db.add(nueva_asignacion)
            
        for i in range(cantidad_personas):
            codigo_qr_unico = f"QR-{uuid.uuid4().hex[:8].upper()}-{i+1}"
            
            img = qrcode.make(codigo_qr_unico)
            os.makedirs("app/static/uploads/qrs", exist_ok=True)
            img.save(f"app/static/uploads/qrs/{codigo_qr_unico}.png")
            
            nuevo_ingreso = models.IngresoPuerta(
                reserva_id=nueva_reserva.id,
                codigo_qr=codigo_qr_unico,
                estado_ingreso="no_utilizado"
            )
            db.add(nuevo_ingreso)
            
        db.commit()

        try:
            evento_obj = db.query(models.Evento).filter(models.Evento.id == evento_id).first()
            local_obj = db.query(models.Local).filter(models.Local.id == evento_obj.local_id).first() if evento_obj else None
            
            if local_obj and local_obj.correo_envio and local_obj.password_app:
                asunto = f"¡Reserva Registrada! - Código: {codigo_unico}"
                cuerpo_html = f"""
                <h3>Hola {cliente_existe.nombre},</h3>
                <p>Tu reserva ha sido registrada con éxito y está pendiente de aprobación por el establecimiento.</p>
                <p><b>Código de reserva:</b> {codigo_unico}</p>
                <p>¡Te avisaremos pronto!</p>
                """
                enviar_correo_smtp(
                    remitente=local_obj.correo_envio,
                    password=local_obj.password_app,
                    destinatario=cliente_existe.email,
                    asunto=asunto,
                    html_content=cuerpo_html
                )
        except Exception as e:
            print(f"❌ Error al enviar correo de reserva creada: {e}")

        return {"mensaje": "¡Reserva y comprobante guardados con éxito!", "codigo_reserva": codigo_unico}

    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno al procesar el pago y reserva: {str(e)}")

@router.put("/{reserva_id}/aprobar")
def aprobar_reserva(reserva_id: int, payload: AprobarReservaRequest = None, db: Session = Depends(get_db)):
    reserva = db.query(models.Reserva).filter(models.Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    
    reserva.estado_reserva = "confirmada"
    
    mensaje_personalizado = payload.mensaje_personalizado if payload else None
    if mensaje_personalizado:
        reserva.mensaje_personalizado = mensaje_personalizado
    
    if reserva.evento_id:
        evento = db.query(models.Evento).filter(models.Evento.id == reserva.evento_id).first()
        if evento:
            evento.estado = "confirmado"
            if evento.nombre_evento.startswith("[EN REVISIÓN]"):
                evento.nombre_evento = evento.nombre_evento.replace("[EN REVISIÓN]", "").strip()

    db.commit()
    db.refresh(reserva)
    
    cliente = db.query(models.UsuarioFinal).filter(models.UsuarioFinal.id == reserva.cliente_id).first()
    evento_obj = db.query(models.Evento).filter(models.Evento.id == reserva.evento_id).first()
    local_obj = db.query(models.Local).filter(models.Local.id == evento_obj.local_id).first() if evento_obj else None
    
    remitente_correo = local_obj.correo_envio if local_obj else "No configurado"
    destinatario = cliente.email if cliente else ""
    
    ingresos_qr = db.query(models.IngresoPuerta).filter(models.IngresoPuerta.reserva_id == reserva.id).all()
    lista_codigos_qr = [qr.codigo_qr for qr in ingresos_qr]

    if local_obj and local_obj.correo_envio and local_obj.password_app and destinatario:
        try:
            qr_items_html = ""
            for i, qr in enumerate(ingresos_qr, start=1):
                api_qr_img = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr.codigo_qr}"
                qr_items_html += f"""
                <div style="margin-bottom: 20px; border: 1px solid #ddd; padding: 12px; border-radius: 8px; display: inline-block; text-align: center; background-color: #f9f9f9; margin-right: 10px;">
                    <p style="margin: 0 0 8px 0; font-weight: bold; color: #333;">Acompañante {i}</p>
                    <img src="{api_qr_img}" alt="QR {qr.codigo_qr}" width="130" height="130" style="display: block; margin: 0 auto; border-radius: 4px;"><br>
                    <p style="margin: 5px 0 0 0; font-size: 13px; color: #555;">Código: <b>{qr.codigo_qr}</b></p>
                </div>
                """
            
            mensaje_custom_html = ""
            if mensaje_personalizado and mensaje_personalizado.strip():
                mensaje_custom_html = f"""
                <div style="background-color: #e8f4fd; border-left: 4px solid #2196F3; padding: 12px; border-radius: 4px; margin: 15px 0; color: #0d3c61;">
                    <p style="margin: 0 0 4px 0; font-weight: bold; font-size: 13px;">Mensaje especial del establecimiento:</p>
                    <p style="margin: 0; font-size: 14px; white-space: pre-line;">{mensaje_personalizado}</p>
                </div>
                """

            cuerpo_html = f"""
            <h3>¡Buenas noticias, {cliente.nombre}!</h3>
            <p>Tu reserva ha sido <b>aprobada</b> con éxito.</p>
            <p><b>Código de reserva principal:</b> {reserva.codigo_reserva}</p>
            {mensaje_custom_html}
            <p>Aquí tienes los pases con los códigos QR visuales para cada uno de tus {reserva.cantidad_personas} asistentes:</p>
            <div style="text-align: center; margin-top: 15px;">
                {qr_items_html}
            </div>
            <p style="margin-top: 20px;">¡Te esperamos en el evento!</p>
            """
            
            enviar_correo_smtp(
                remitente=local_obj.correo_envio,
                password=local_obj.password_app,
                destinatario=destinatario,
                asunto=f"¡Reserva Aprobada! - Código: {reserva.codigo_reserva}",
                html_content=cuerpo_html
            )
        except Exception as e:
            print(f"❌ ERROR DETALLADO AL ENVIAR CORREO SMTP: {str(e)}")

    return {
        "mensaje": f"Reserva {reserva.codigo_reserva} aprobada con éxito", 
        "estado": reserva.estado_reserva,
        "cliente_correo": destinatario,
        "codigos_qr": lista_codigos_qr
    }

@router.get("/cliente/{cliente_id}")
def listar_reservas_por_cliente(cliente_id: int, db: Session = Depends(get_db)):
    reservas = db.query(models.Reserva).filter(models.Reserva.cliente_id == cliente_id).all()
    
    lista_final = []
    for reserva in reservas:
        evento = db.query(models.Evento).filter(models.Evento.id == reserva.evento_id).first()
        local = db.query(models.Local).filter(models.Local.id == evento.local_id).first() if evento and evento.local_id else None
        
        numeros_mesas = ", ".join([str(m.numero_mesa) for m in reserva.mesas]) if reserva.mesas else "N/A"
        
        nombre_local = "Establecimiento General"
        if local:
            nombre_local = getattr(local, "nombre_local", getattr(local, "nombre", "Establecimiento General"))

        lista_final.append({
            "id": reserva.id,
            "codigo_reserva": reserva.codigo_reserva,
            "estado_reserva": reserva.estado_reserva,
            "cantidad_personas": reserva.cantidad_personas,
            "tipo_celebracion": reserva.tipo_celebracion,
            "comprobante_pago": reserva.comprobante_pago,
            "creado_en": reserva.creado_en,
            "nombre_evento": evento.nombre_evento if evento else "Evento",
            "fecha_hora_evento": evento.fecha_hora.strftime("%d/%m/%Y %H:%M") if evento and evento.fecha_hora else "",
            "nombre_local": nombre_local,
            "numero_mesa": numeros_mesas,
            "mensaje_personalizado": getattr(reserva, "mensaje_personalizado", None)
        })
    return lista_final

@router.put("/{reserva_id}/checkin")
def registrar_checkin(reserva_id: int, db: Session = Depends(get_db)):
    reserva = db.query(models.Reserva).filter(models.Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    
    reserva.estado_reserva = "completada"
    db.commit()
    db.refresh(reserva)
    return {"message": "Check-in registrado con éxito", "estado": reserva.estado_reserva}

@router.get("/qr/todos")
def listar_todos_qr(db: Session = Depends(get_db)):
    resultados = db.query(models.IngresoPuerta, models.Reserva, models.UsuarioFinal).join(
        models.Reserva, models.IngresoPuerta.reserva_id == models.Reserva.id
    ).join(
        models.UsuarioFinal, models.Reserva.cliente_id == models.UsuarioFinal.id
    ).all()
    
    lista_final = []
    for ingreso, reserva, cliente in resultados:
        mesa_asignada = ingreso.mesa_id if getattr(ingreso, "mesa_id", None) else (reserva.mesas[0].id if reserva.mesas else "N/A")
        lista_final.append({
            "ingreso_id": ingreso.id,
            "reserva_id": reserva.id,
            "codigo_qr": ingreso.codigo_qr,
            "estado_ingreso": ingreso.estado_ingreso,
            "cliente_nombre": cliente.nombre,
            "mesa_id": mesa_asignada,
            "codigo_reserva": reserva.codigo_reserva
        })
    return lista_final

@router.get("/qr/{codigo_qr}")
def obtener_detalle_qr(codigo_qr: str, db: Session = Depends(get_db)):
    ingreso = db.query(models.IngresoPuerta).filter(models.IngresoPuerta.codigo_qr == codigo_qr.strip().upper()).first()
    if not ingreso:
        raise HTTPException(status_code=404, detail="Código QR no encontrado")
    
    reserva = db.query(models.Reserva).filter(models.Reserva.id == ingreso.reserva_id).first()
    cliente = db.query(models.UsuarioFinal).filter(models.UsuarioFinal.id == reserva.cliente_id).first() if reserva else None
    
    mesa_obj = db.query(models.Mesa).filter(models.Mesa.id == ingreso.mesa_id).first() if getattr(ingreso, "mesa_id", None) else None
    numeros_mesas = mesa_obj.numero_mesa if mesa_obj else (", ".join([m.numero_mesa for m in reserva.mesas]) if reserva and reserva.mesas else "N/A")
    
    fecha_ingreso_str = ingreso.fecha_ingreso.strftime("%d/%m/%Y %H:%M:%S") if getattr(ingreso, "fecha_ingreso", None) else None

    return {
        "ingreso_id": ingreso.id,
        "codigo_qr": ingreso.codigo_qr,
        "estado_ingreso": ingreso.estado_ingreso,
        "fecha_ingreso": fecha_ingreso_str,
        "reserva_id": reserva.id if reserva else None,
        "codigo_reserva": reserva.codigo_reserva if reserva else "",
        "cliente_nombre": cliente.nombre if cliente else "Desconocido",
        "cliente_telefono": cliente.telefono if cliente else "",
        "cantidad_personas": reserva.cantidad_personas if reserva else 0,
        "mesa_id": numeros_mesas
    }

@router.put("/qr/{ingreso_id}/checkin")
def registrar_checkin_qr(ingreso_id: int, db: Session = Depends(get_db)):
    ingreso = db.query(models.IngresoPuerta).filter(models.IngresoPuerta.id == ingreso_id).first()
    if not ingreso:
        ingreso = db.query(models.IngresoPuerta).filter(models.IngresoPuerta.codigo_qr == str(ingreso_id)).first()
        
    if not ingreso:
        raise HTTPException(status_code=404, detail="Pase QR no encontrado")
    
    if ingreso.estado_ingreso in ["utilizado", "completada", "ingresado"]:
        return {"mensaje": "El QR ya había sido utilizado anteriormente", "estado_ingreso": ingreso.estado_ingreso}

    ingreso.estado_ingreso = "utilizado"
    ingreso.fecha_ingreso = datetime.now()
    
    reserva = db.query(models.Reserva).filter(models.Reserva.id == ingreso.reserva_id).first()
    mesas_a_actualizar = [ingreso.mesa_id] if getattr(ingreso, "mesa_id", None) else [m.id for m in reserva.mesas]

    if reserva and reserva.evento_id:
        for mesa_id in mesas_a_actualizar:
            if not mesa_id:
                continue
            asignacion_mesa = db.query(models.PrecioEventoMesa).filter(
                models.PrecioEventoMesa.evento_id == reserva.evento_id,
                models.PrecioEventoMesa.mesa_id == mesa_id
            ).first()
            
            if asignacion_mesa:
                asignacion_mesa.estado = "ingresado"
            else:
                nueva_asignacion = models.PrecioEventoMesa(
                    evento_id=reserva.evento_id,
                    mesa_id=mesa_id,
                    estado="ingresado"
                )
                db.add(nueva_asignacion)
            
    db.commit()
    db.refresh(ingreso)
    
    return {"mensaje": "Check-in registrado con éxito y mesa actualizada", "estado_ingreso": ingreso.estado_ingreso}

@router.delete("/eventos/{evento_id}", status_code=status.HTTP_200_OK)
def eliminar_evento(evento_id: int, db: Session = Depends(get_db)):
    evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="El evento no existe.")
    
    db.delete(evento)
    db.commit()
    return {"message": "Evento eliminado exitosamente"}

@router.put("/eventos/{evento_id}")
def actualizar_evento(
    evento_id: int,
    nombre_evento: str = Form(...),
    artista_orquesta: str = Form(None),
    fecha_hora: str = Form(...),
    descripcion: str = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="El evento no existe.")
    
    try:
        evento.nombre_evento = nombre_evento
        evento.artista_orquesta = artista_orquesta
        evento.fecha_hora = datetime.fromisoformat(fecha_hora)
        evento.descripcion = descripcion
        
        if file and file.filename:
            nombre_archivo = file.filename
            file_path = os.path.join(UPLOAD_DIR, nombre_archivo)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            evento.imagen = nombre_archivo
            
        db.commit()
        db.refresh(evento)
        return {"mensaje": "¡Evento actualizado con éxito!", "id": evento.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error al actualizar: {str(e)}")
    
@router.put("/{reserva_id}/rechazar")
def rechazar_reserva(reserva_id: int, db: Session = Depends(get_db)):
    reserva = db.query(models.Reserva).filter(models.Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    
    reserva.estado_reserva = "rechazada"
    db.commit()
    db.refresh(reserva)
    
    cliente = db.query(models.UsuarioFinal).filter(models.UsuarioFinal.id == reserva.cliente_id).first()
    
    if cliente and cliente.email:
        try:
            evento_obj = db.query(models.Evento).filter(models.Evento.id == reserva.evento_id).first()
            local_obj = db.query(models.Local).filter(models.Local.id == evento_obj.local_id).first() if evento_obj else None
            
            if local_obj and local_obj.correo_envio and local_obj.password_app:
                asunto = f"Actualización sobre tu reserva - Código: {reserva.codigo_reserva}"
                cuerpo_html = f"""
                <h3>Hola {cliente.nombre},</h3>
                <p>Lamentamos informarte que tu reserva con código <b>{reserva.codigo_reserva}</b> no pudo ser aprobada en esta ocasión.</p>
                """
                enviar_correo_smtp(
                    remitente=local_obj.correo_envio,
                    password=local_obj.password_app,
                    destinatario=cliente.email,
                    asunto=asunto,
                    html_content=cuerpo_html
                )
        except Exception as e:
            print(f"❌ Error al enviar correo de reserva rechazada: {e}")

    return {
        "mensaje": f"Reserva {reserva.codigo_reserva} rechazada correctamente",
        "estado": reserva.estado_reserva
    }