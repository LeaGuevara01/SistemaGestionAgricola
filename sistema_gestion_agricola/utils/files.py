# utils/files.py
import os
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Magic numbers para validar tipos de archivo
IMAGE_SIGNATURES = {
    b'\xff\xd8\xff': 'jpeg',
    b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a': 'png',
    b'\x47\x49\x46\x38': 'gif'
}

def allowed_file(filename):
    """Verifica si la extensión del archivo está permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image_content(file_storage):
    """Valida que el archivo sea realmente una imagen"""
    try:
        # Validar usando magic numbers
        file_storage.seek(0)
        header = file_storage.read(16)
        file_storage.seek(0)
        
        # Verificar magic numbers
        is_valid_image = False
        for signature, img_type in IMAGE_SIGNATURES.items():
            if header.startswith(signature):
                is_valid_image = True
                break
                
        if not is_valid_image:
            return False
            
        # Validar tamaño
        file_storage.seek(0, 2)  # Ir al final
        size = file_storage.tell()
        file_storage.seek(0)  # Volver al inicio
        
        if size > MAX_FILE_SIZE:
            return False
            
        return True
    except Exception:
        return False

def save_uploaded_file(file_storage, folder_type='general'):
    """
    Guarda un archivo subido de forma segura.

    Parámetros:
        - file_storage: objeto FileStorage que viene de request.files['campo']
        - folder_type: tipo de carpeta ('componentes', 'maquinas', 'general')

    Retorna:
        - Nombre del archivo guardado si se guardó correctamente.
        - None si el archivo no es válido o no se guardó.
    """
    if not file_storage or not file_storage.filename:
        return None
        
    if not allowed_file(file_storage.filename):
        return None
        
    if not validate_image_content(file_storage):
        return None

    filename = secure_filename(file_storage.filename)
    
    # Generar nombre único para evitar colisiones
    import uuid
    name, ext = os.path.splitext(filename)
    unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"

    # Carpeta donde se guardan los archivos, configurada en Flask config
    if folder_type == 'componentes':
        upload_folder = current_app.config.get('UPLOAD_FOLDER_COMPONENTES')
    elif folder_type == 'maquinas':
        upload_folder = current_app.config.get('UPLOAD_FOLDER_MAQUINAS')
    else:
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')

    # Crear carpeta si no existe
    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(upload_folder, unique_filename)

    try:
        # Guardar archivo en el path
        file_storage.save(file_path)
        return unique_filename
    except Exception as e:
        current_app.logger.error(f"Error al guardar archivo: {str(e)}")
        return None
