import os

def guardar_foto_local(file_uploaded, local_id):
    """
    Guarda la foto subida en app/static/uploads/fotos_locales/ 
    con el formato estándar: imagen_local_[ID].[ext]
    """
    if not file_uploaded:
        return None
    
    # Directorio de destino físico
    upload_dir = os.path.join("app", "static", "uploads", "fotos_locales")
    os.makedirs(upload_dir, exist_ok=True)
    
    # Obtener la extensión original del archivo (.jpg, .png, etc.)
    ext = os.path.splitext(file_uploaded.name)[1].lower()
    if not ext:
        ext = ".jpg"
        
    # Construir el nombre estandarizado usando el ID (ej: imagen_local_3.jpg)
    nombre_archivo = f"imagen_local_{local_id}{ext}"
    ruta_completa = os.path.join(upload_dir, nombre_archivo)
    
    # Guardar el archivo físicamente en el disco
    with open(ruta_completa, "wb") as f:
        f.write(file_uploaded.getbuffer())
        
    # Retornar la ruta relativa que se guardará en la Base de Datos
    return f"app/static/uploads/fotos_locales/{nombre_archivo}"
    return None