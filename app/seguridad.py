from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

# Configuración del contexto de encriptación con bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Clave secreta para firmar los tokens JWT
SECRET_KEY = "bookea_clave_secreta_super_segura_2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # Token válido por 7 días

def verificar_password(password_plana: str, password_hash: str) -> bool:
    """Verifica si una contraseña en texto plano coincide con su hash."""
    password_bytes = password_plana.encode("utf-8")[:72]
    password_segura = password_bytes.decode("utf-8", errors="ignore")
    return pwd_context.verify(password_segura, password_hash)

def obtener_password_hash(password: str) -> str:
    """Genera un hash seguro usando bcrypt para una contraseña."""
    password_bytes = password.encode("utf-8")[:72]
    password_segura = password_bytes.decode("utf-8", errors="ignore")
    return pwd_context.hash(password_segura)

def crear_token_acceso(data: dict, expires_delta: timedelta = None) -> str:
    """Crea un token JWT que podrá ser usado por la web y la app móvil."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
