# utils/files.py
import os
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    """Verifica si la extensión del archivo está permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file_storage):
    """
    Guarda un archivo subido de forma segura.

    Parámetros:
        - file_storage: objeto FileStorage que viene de request.files['campo']

    Retorna:
        - Nombre del archivo guardado si se guardó correctamente.
        - None si el archivo no es válido o no se guardó.
    """
    if file_storage and allowed_file(file_storage.filename):
        filename = secure_filename(file_storage.filename)

        # Carpeta donde se guardan los archivos, configurada en Flask config
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')

        # Crear carpeta si no existe
        os.makedirs(upload_folder, exist_ok=True)

        file_path = os.path.join(upload_folder, filename)

        # Guardar archivo en el path
        file_storage.save(file_path)

        return filename

    return None
