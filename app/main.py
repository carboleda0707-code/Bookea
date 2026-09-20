from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app import models
from app.routers import auth, clientes_auth, reservas, zonas, precios_mesas, locales, admin, recuperacion
from fastapi.staticfiles import StaticFiles
from app.routers import locales # O como se llame tu archivo de router de locales

from pathlib import Path

# Definimos la ruta base del proyecto de forma absoluta
BASE_DIR = Path(__file__).resolve().parent.parent

# 1. Primero creas la aplicación FastAPI
app = FastAPI(
    title="API de Reservas Multi-Local (SaaS)",
    description="Sistema de reservas para restaurantes, bares, discotecas y más.",
    version="1.0.0"
)

# 2. Montas la carpeta static para servir imágenes (comprobantes y QRs)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 3. Montas la interfaz web móvil (frontend_web)
app.mount("/app", StaticFiles(directory=str(BASE_DIR / "frontend_web"), html=True), name="frontend_web")

# 4. Creas las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Justo donde registras los demás routers:
app.include_router(recuperacion.router)

# 5. Registras los routers AQUÍ ABAJO (cuando 'app' ya existe)
app.include_router(auth.router)
app.include_router(clientes_auth.router)
app.include_router(reservas.router)
app.include_router(zonas.router)
app.include_router(precios_mesas.router)
app.include_router(admin.router)

app.include_router(locales.router)

@app.get("/anuncios/activos/")
def obtener_anuncios(db: Session = Depends(get_db)):
    return db.query(models.Anuncio).filter(models.Anuncio.activo == True).all()

@app.get("/")
def read_root():
    return {"mensaje": "Bienvenido a la API de Reservas Multi-Local 🚀"}

# Esto fuerza la creación de solo las tablas que faltan en la base de datos
models.Base.metadata.create_all(bind=engine)
print("¡Tablas sincronizadas correctamente!")