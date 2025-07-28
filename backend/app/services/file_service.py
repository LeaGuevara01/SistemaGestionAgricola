import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
from PIL import Image

class FileService:
    # Extensiones para imágenes
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    # Extensiones para archivos de importación
    ALLOWED_IMPORT_EXTENSIONS = {'csv', 'xlsx', 'xls'}
    
    MAX_IMAGE_SIZE = (800, 600)
    MAX_CSV_SIZE = 5 * 1024 * 1024  # 5MB para CSV
    
    @staticmethod
    def allowed_file(filename, file_type='image'):
        """
        Verifica si el archivo es permitido según el tipo
        file_type: 'image' o 'import'
        """
        if not ('.' in filename):
            return False
            
        extension = filename.rsplit('.', 1)[1].lower()
        
        if file_type == 'image':
            return extension in FileService.ALLOWED_IMAGE_EXTENSIONS
        elif file_type == 'import':
            return extension in FileService.ALLOWED_IMPORT_EXTENSIONS
        
        return False
    
    @staticmethod
    def save_file(file, subfolder='', resize=True):
        """Método existente para imágenes"""
        if file and FileService.allowed_file(file.filename, 'image'):
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
    def save_import_file(file, subfolder='imports'):
        """
        Nuevo método para guardar archivos de importación (CSV, Excel)
        """
        if file and FileService.allowed_file(file.filename, 'import'):
            # Validar tamaño de archivo
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > FileService.MAX_CSV_SIZE:
                raise ValueError(f"Archivo muy grande. Máximo permitido: {FileService.MAX_CSV_SIZE / 1024 / 1024}MB")
            
            # Generar nombre único
            filename = secure_filename(file.filename)
            file_extension = filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
            
            # Crear ruta completa
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
            os.makedirs(upload_path, exist_ok=True)
            
            file_path = os.path.join(upload_path, unique_filename)
            
            # Guardar archivo
            file.save(file_path)
            
            # Retornar ruta completa para procesamiento inmediato
            return file_path
        
        return None
    
    @staticmethod
    def cleanup_temp_file(file_path):
        """Elimina archivo temporal de importación"""
        return FileService.delete_file(file_path)
    
    @staticmethod
    def delete_file(file_path):
        """Método existente para eliminar archivos"""
        try:
            if file_path:
                # Si es ruta completa, usar directamente
                if os.path.isabs(file_path):
                    full_path = file_path
                else:
                    # Si es ruta relativa, construir ruta completa
                    full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_path)
                
                if os.path.exists(full_path):
                    os.remove(full_path)
                    return True
        except Exception as e:
            print(f"Error deleting file: {e}")
        return False
    
    @staticmethod
    def get_file_url(file_path):
        """Método existente para URLs de imágenes"""
        if file_path:
            return f"/static/fotos/{file_path}"
        return None
    
    @staticmethod
    def validate_csv_structure(file_path, required_columns):
        """
        Valida que el CSV tenga las columnas requeridas
        """
        import pandas as pd
        
        try:
            # Leer solo la primera fila para verificar columnas
            df = pd.read_csv(file_path, nrows=0)
            csv_columns = set(df.columns.str.strip().str.lower())
            required_columns_lower = set(col.lower() for col in required_columns)
            
            missing_columns = required_columns_lower - csv_columns
            
            if missing_columns:
                return {
                    'valid': False,
                    'error': f"Columnas faltantes: {', '.join(missing_columns)}"
                }
            
            return {'valid': True, 'columns': list(df.columns)}
            
        except Exception as e:
            return {
                'valid': False,
                'error': f"Error al leer archivo CSV: {str(e)}"
            }