import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
from PIL import Image

class FileService:
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_IMAGE_SIZE = (800, 600)
    
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in FileService.ALLOWED_EXTENSIONS
    
    @staticmethod
    def save_file(file, subfolder='', resize=True):
        if file and FileService.allowed_file(file.filename):
            # Generar nombre único
            filename = secure_filename(file.filename)
            file_extension = filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
            
            # Crear ruta completa
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
            os.makedirs(upload_path, exist_ok=True)
            
            file_path = os.path.join(upload_path, unique_filename)
            
            # Redimensionar imagen si es necesario
            if resize and file_extension in ['jpg', 'jpeg', 'png']:
                try:
                    with Image.open(file) as img:
                        img.thumbnail(FileService.MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
                        img.save(file_path, optimize=True, quality=85)
                except Exception:
                    # Si falla el redimensionamiento, guardar original
                    file.save(file_path)
            else:
                file.save(file_path)
            
            # Retornar ruta relativa
            return os.path.join(subfolder, unique_filename).replace('\\', '/')
        
        return None
    
    @staticmethod
    def delete_file(file_path):
        try:
            if file_path:
                full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_path)
                if os.path.exists(full_path):
                    os.remove(full_path)
                    return True
        except Exception as e:
            print(f"Error deleting file: {e}")
        return False
    
    @staticmethod
    def get_file_url(file_path):
        if file_path:
            return f"/static/fotos/{file_path}"
        return None