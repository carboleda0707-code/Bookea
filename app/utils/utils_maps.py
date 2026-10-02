import openlocationcode as olc

def generar_enlace_google_maps(codigo_plus):
    """
    Recibe un Plus Code (ej. 'W4Q4+QM7') y devuelve una URL 
    directa para abrir Google Maps en esa ubicación exacta.
    """
    if not codigo_plus:
        # Enlace por defecto a Guayaquil si no tiene código
        return "https://maps.google.com/?q=Guayaquil"
    
    try:
        # Si el código es corto (ej. 'W4Q4+QM7'), Open Location Code 
        # a veces requiere un área de referencia, pero para mapas 
        # podemos usar directamente el código en la URL de búsqueda de Google Maps,
        # ya que Google Maps entiende perfectamente los Plus Codes.
        url = f"https://www.google.com/maps/search/?api=1&query={codigo_plus}"
        return url
    except Exception:
        return "https://maps.google.com"