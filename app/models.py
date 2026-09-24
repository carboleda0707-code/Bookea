from datetime import datetime
from sqlalchemy import (
    BigInteger,  # <--- Asegúrate de importar BigInteger aquí
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    Text,
    UniqueConstraint,
)

from sqlalchemy.orm import relationship
from .database import Base

# --- TABLA INTERMEDIA PARA MUCHAS MESAS EN UNA RESERVA ---
reserva_mesas = Table(
    "reserva_mesas",
    Base.metadata,
    Column(
        "reserva_id",
        Integer,
        ForeignKey("reservas.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "mesa_id",
        Integer,
        ForeignKey("mesas.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Empresa(Base):
  __tablename__ = "empresas"

  id = Column(BigInteger, primary_key=True, index=True)  # <--- Cambiado a BigInteger
  nombre_comercial = Column(String(150), nullable=False)
  ruc_nit = Column(String(20), unique=True, nullable=False, index=True)
  activo = Column(Boolean, default=True)
  creado_en = Column(DateTime, default=datetime.utcnow)

  locales = relationship("Local", back_populates="empresa", cascade="all, delete")
  usuarios = relationship("Usuario", back_populates="empresa", cascade="all, delete")


class Local(Base):
  __tablename__ = "locales"

  id = Column(Integer, primary_key=True, index=True)
  empresa_id = Column(
      BigInteger, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=True
  )  # <--- Cambiado a BigInteger
  propietario_id = Column(
      Integer,
      ForeignKey("usuarios.propietario_id", ondelete="CASCADE"),
      nullable=True,
  )

  nombre = Column(String(100), nullable=False)
  slug = Column(String(100), unique=True, index=True, nullable=True)
  tipo_establecimiento = Column(String(50), default="Salsoteca / Bar")
  correo_envio = Column(String, nullable=True)
  password_app = Column(String, nullable=True)
  direccion = Column(Text, nullable=True)
  ciudad = Column(String(100), nullable=True)

  # --- CAMPO NUEVO PARA LOS LIKES DE CADA LOCAL ---
  likes = Column(Integer, default=0, nullable=True)

  # --- CAMPO NUEVO PARA LOS AVISOS DE CORREO ---
  aviso_reserva = Column(Text, nullable=True)
  # ---------------------------------------------

  latitud = Column(Numeric(precision=10, scale=6), nullable=True)
  longitud = Column(Numeric(precision=10, scale=6), nullable=True)
  pais = Column(String(100), default="Ecuador", nullable=True)

  email_contacto = Column(String(150), nullable=True)
  telefono = Column(String(20), nullable=True)
  telefono_contacto = Column(String(50), nullable=True)
  tipo_plan = Column(String(20), default="Normal")
  pagado = Column(Boolean, default=False)
  activo = Column(Boolean, default=True)

  creado_en = Column(DateTime, default=datetime.utcnow)

  empresa = relationship("Empresa", back_populates="locales")
  propietario = relationship(
      "Usuario", back_populates="locales", foreign_keys=[propietario_id]
  )
  zonas = relationship("Zona", back_populates="local", cascade="all, delete")
  eventos = relationship("Evento", back_populates="local", cascade="all, delete")


class Zona(Base):
  __tablename__ = "zonas"

  id = Column(Integer, primary_key=True, index=True)
  local_id = Column(Integer, ForeignKey("locales.id", ondelete="CASCADE"))
  nombre_zona = Column(String(100), nullable=False)
  descripcion = Column(Text)

  local = relationship("Local", back_populates="zonas")
  mesas = relationship("Mesa", back_populates="zona", cascade="all, delete")


class Mesa(Base):
  __tablename__ = "mesas"

  id = Column(Integer, primary_key=True, index=True)
  zona_id = Column(Integer, ForeignKey("zonas.id", ondelete="CASCADE"))
  numero_mesa = Column(String(50), nullable=False)
  capacidad = Column(Integer, nullable=False)
  forma = Column(String(30), default="rectangulo")
  pos_x = Column(Integer, default=0)
  pos_y = Column(Integer, default=0)
  activo = Column(Boolean, default=True)

  zona = relationship("Zona", back_populates="mesas")
  precios_evento = relationship(
      "PrecioEventoMesa", back_populates="mesa", cascade="all, delete"
  )
  reservas = relationship(
      "Reserva", secondary=reserva_mesas, back_populates="mesas"
  )


class Evento(Base):
  __tablename__ = "eventos"

  id = Column(Integer, primary_key=True, index=True)
  local_id = Column(Integer, ForeignKey("locales.id", ondelete="CASCADE"))
  nombre_evento = Column(String(150), nullable=False)
  artista_orquesta = Column(String(150), nullable=True)

  genero_musical = Column(String(100), nullable=True)
  incluye_piqueos = Column(Boolean, default=False)
  tipo_ambiente = Column(String(100), nullable=True)
  capacidad_total = Column(Integer, default=50)

  fecha_hora = Column(DateTime, nullable=False)
  descripcion = Column(Text)
  estado = Column(String(30), default="programado")
  imagen = Column(String(255))

  # --- CAMPO NUEVO PARA EL CREADOR (ID del propietario o comensal) ---
  creador = Column(Integer, nullable=True)

  local = relationship("Local", back_populates="eventos")
  precios_mesas = relationship(
      "PrecioEventoMesa", back_populates="evento", cascade="all, delete"
  )
  reservas = relationship("Reserva", back_populates="evento")


class PrecioEventoMesa(Base):
  __tablename__ = "precios_evento_mesa"

  id = Column(Integer, primary_key=True, index=True)
  evento_id = Column(Integer, ForeignKey("eventos.id", ondelete="CASCADE"))
  mesa_id = Column(Integer, ForeignKey("mesas.id", ondelete="CASCADE"))
  precio_reserva = Column(Numeric(10, 2), nullable=False, default=0.00)
  consumo_minimo = Column(Numeric(10, 2), nullable=False, default=0.00)
  estado = Column(String(30), default="desocupado")

  __table_args__ = (
      UniqueConstraint("evento_id", "mesa_id", name="_evento_mesa_uc"),
  )

  evento = relationship("Evento", back_populates="precios_mesas")
  mesa = relationship("Mesa", back_populates="precios_evento")


class Reserva(Base):
  __tablename__ = "reservas"

  id = Column(Integer, primary_key=True, index=True)
  evento_id = Column(Integer, ForeignKey("eventos.id", ondelete="CASCADE"))
  cliente_id = Column(
      Integer, ForeignKey("usuarios_finales.id", ondelete="CASCADE")
  )

  cantidad_personas = Column(Integer, nullable=False)
  tipo_celebracion = Column(String(50), default="ninguna")
  estado_reserva = Column(String(30), default="pendiente_pago")
  codigo_reserva = Column(String(30), unique=True, nullable=False, index=True)
  comprobante_pago = Column(String(255), nullable=True)
  mensaje_personalizado = Column(Text, nullable=True)  # <-- Columna añadida
  creado_en = Column(DateTime, default=datetime.utcnow)

  evento = relationship("Evento", back_populates="reservas")
  mesas = relationship(
      "Mesa", secondary=reserva_mesas, back_populates="reservas"
  )  # <-- Relación corregida hacia Mesa
  cliente = relationship("UsuarioFinal", back_populates="reservas")
  pago = relationship(
      "Pago", back_populates="reserva", uselist=False, cascade="all, delete"
  )
  ingreso = relationship(
      "IngresoPuerta",
      back_populates="reserva",
      uselist=False,
      cascade="all, delete",
  )


class ConfiguracionNotificaciones(Base):
  __tablename__ = "configuracion_notificaciones"

  id = Column(Integer, primary_key=True, index=True)
  correo_remitente = Column(String, nullable=True)
  password_correo = Column(String, nullable=True)
  celular_remitente = Column(String, nullable=True)


class Pago(Base):
  __tablename__ = "pagos"

  id = Column(Integer, primary_key=True, index=True)
  reserva_id = Column(Integer, ForeignKey("reservas.id", ondelete="CASCADE"))
  monto_total = Column(Numeric(10, 2), nullable=False)
  metodo_pago = Column(String(50), default="transferencia")
  url_comprobante = Column(Text, nullable=True)
  estado_pago = Column(String(30), default="pendiente")
  validado_por_usuario_id = Column(Integer, nullable=True)
  fecha_pago = Column(DateTime, default=datetime.utcnow)

  reserva = relationship("Reserva", back_populates="pago")


class IngresoPuerta(Base):
  __tablename__ = "ingresos_puerta"

  id = Column(Integer, primary_key=True, index=True)
  reserva_id = Column(Integer, ForeignKey("reservas.id", ondelete="CASCADE"))
  codigo_qr = Column(String(50), unique=True, nullable=False, index=True)
  estado_ingreso = Column(String(30), default="no_utilizado")
  fecha_ingreso = Column(DateTime, nullable=True)
  escaneado_por = Column(String(100), nullable=True)
  mesa_id = Column(Integer, ForeignKey("mesas.id"), nullable=True)
  reserva = relationship("Reserva", back_populates="ingreso")


class Usuario(Base):
  __tablename__ = "usuarios"

  propietario_id = Column(Integer, primary_key=True, index=True)
  empresa_id = Column(
      BigInteger, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=True
  )
  nombre = Column(String(100), nullable=False)
  correo = Column(String(150), unique=True, nullable=False, index=True)
  slug = Column(String(150), unique=True, index=True, nullable=True)
  contrasena = Column(String(255), nullable=False)
  rol = Column(String(30), default="propietario")

  nombre_comercial = Column(String(150), nullable=True)
  tipo_negocio = Column(String(50), nullable=True)

  latitud = Column(Numeric(precision=10, scale=6), nullable=True)
  longitud = Column(Numeric(precision=10, scale=6), nullable=True)

  tipo_plan = Column(String(20), default="Normal")
  pagado = Column(Boolean, default=False)
  activo = Column(Boolean, default=True)
  creado_en = Column(DateTime, default=datetime.utcnow)

  empresa = relationship("Empresa", back_populates="usuarios")
  locales = relationship("Local", back_populates="propietario", cascade="all, delete")


class UsuarioFinal(Base):
  __tablename__ = "usuarios_finales"

  id = Column(Integer, primary_key=True, index=True)
  nombre = Column(String(100), nullable=False)
  email = Column(String(150), unique=True, index=True, nullable=False)
  password_hash = Column(String(255), nullable=False)
  telefono = Column(String(20), nullable=True)
  fecha_registro = Column(DateTime, default=datetime.utcnow)
  es_activo = Column(Boolean, default=True)

  reset_token = Column(String(10), nullable=True)
  reset_token_expires = Column(DateTime, nullable=True)

  latitud = Column(Numeric(precision=10, scale=6), nullable=True)
  longitud = Column(Numeric(precision=10, scale=6), nullable=True)

  reservas = relationship("Reserva", back_populates="cliente")


class Anuncio(Base):
  __tablename__ = "anuncios"

  id = Column(Integer, primary_key=True, index=True)
  nombre_marca = Column(String(100))
  url_imagen = Column(String)
  enlace_destino = Column(String)
  activo = Column(Boolean, default=True)