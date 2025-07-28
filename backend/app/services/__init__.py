import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

class FileService:
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in FileService.ALLOWED_EXTENSIONS
    
    @staticmethod
    def save_file(file, subfolder=''):
        if file and FileService.allowed_file(file.filename):
            # Generar nombre único
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            
            # Crear ruta completa
            upload_path = os.path.join(
                current_app.config['UPLOAD_FOLDER'], 
                subfolder
            )
            os.makedirs(upload_path, exist_ok=True)
            
            file_path = os.path.join(upload_path, unique_filename)
            file.save(file_path)
            
            # Retornar ruta relativa
            return os.path.join(subfolder, unique_filename).replace('\\', '/')
        
        return None
    
    @staticmethod
    def delete_file(file_path):
        try:
            full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_path)
            if os.path.exists(full_path):
                os.remove(full_path)
                return True
        except Exception as e:
            print(f"Error deleting file: {e}")
        return False