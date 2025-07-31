"""
Manejador de archivos
"""
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app

def get_upload_path(subfolder=None):
    """Obtener ruta de uploads"""
    base_path = current_app.config['UPLOAD_FOLDER']
    if subfolder:
        path = os.path.join(base_path, subfolder)
    else:
        path = base_path
    
    # Crear directorio si no existe
    os.makedirs(path, exist_ok=True)
    return path

def generate_unique_filename(original_filename):
    """Generar nombre único para archivo"""
    if not original_filename or '.' not in original_filename:
        return None
    
    # Obtener extensión
    extension = original_filename.rsplit('.', 1)[1].lower()
    
    # Generar nombre único
    unique_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    return f"{timestamp}_{unique_id}.{extension}"

def save_uploaded_file(file, subfolder=None, allowed_extensions=None):
    """
    Guardar archivo subido
    
    Args:
        file: Archivo de Flask request.files
        subfolder: Subcarpeta donde guardar (ej: 'componentes', 'maquinas')
        allowed_extensions: Set de extensiones permitidas
    
    Returns:
        str: Nombre del archivo guardado o None si hay error
    """
    if not file or file.filename == '':
        return None
    
    # Validar extensión
    if allowed_extensions is None:
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', 
                                                   {'png', 'jpg', 'jpeg', 'gif', 'pdf'})
    
    if not validate_file_extension(file.filename, allowed_extensions):
        return None
    
    try:
        # Generar nombre único
        filename = generate_unique_filename(file.filename)
        if not filename:
            return None
        
        # Obtener ruta de destino
        upload_path = get_upload_path(subfolder)
        file_path = os.path.join(upload_path, filename)
        
        # Guardar archivo
        file.save(file_path)
        
        return filename
        
    except Exception as e:
        print(f"Error guardando archivo: {e}")
        return None

def delete_file(filename, subfolder=None):
    """
    Eliminar archivo
    
    Args:
        filename: Nombre del archivo
        subfolder: Subcarpeta donde está el archivo
    
    Returns:
        bool: True si se eliminó correctamente
    """
    if not filename:
        return False
    
    try:
        upload_path = get_upload_path(subfolder)
        file_path = os.path.join(upload_path, filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error eliminando archivo: {e}")
        return False

def get_file_url(filename, subfolder=None):
    """
    Obtener URL del archivo
    
    Args:
        filename: Nombre del archivo
        subfolder: Subcarpeta donde está el archivo
    
    Returns:
        str: URL del archivo
    """
    if not filename:
        return None
    
    if subfolder:
        return f"/static/uploads/{subfolder}/{filename}"
    else:
        return f"/static/uploads/{filename}"

def validate_file_extension(filename, allowed_extensions):
    """Validar extensión de archivo"""
    if not filename or '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in allowed_extensions

def get_file_size(file_path):
    """Obtener tamaño de archivo en bytes"""
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0

def is_file_too_large(file, max_size=None):
    """Verificar si archivo es demasiado grande"""
    if max_size is None:
        max_size = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)  # 16MB default
    
    # Flask ya maneja esto automáticamente, pero podemos verificar manualmente
    file.seek(0, 2)  # Ir al final del archivo
    size = file.tell()
    file.seek(0)  # Volver al inicio
    
    return size > max_size
