# middleware/security.py
from functools import wraps
from flask import request, jsonify, current_app
import secrets
import hashlib

def validate_secret_key(secret_key):
    """Valida que la SECRET_KEY sea suficientemente fuerte"""
    if not secret_key:
        return False
    if len(secret_key) < 32:
        return False
    return True

def generate_secure_secret():
    """Genera una SECRET_KEY segura"""
    return secrets.token_urlsafe(32)

def rate_limit(max_requests=100, window=3600):
    """Decorator para limitar peticiones por IP"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Implementar rate limiting básico
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            # Aquí implementarías la lógica de rate limiting
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_file_content(file_storage, allowed_types=['image/jpeg', 'image/png', 'image/gif']):
    """Valida el contenido real del archivo, no solo la extensión"""
    if not file_storage:
        return False
    
    # Leer los primeros bytes para validar el tipo real
    file_storage.seek(0)
    header = file_storage.read(512)
    file_storage.seek(0)
    
    # Validar magic numbers
    image_signatures = {
        b'\xff\xd8\xff': 'image/jpeg',
        b'\x89\x50\x4e\x47': 'image/png',
        b'\x47\x49\x46\x38': 'image/gif'
    }
    
    for signature, mime_type in image_signatures.items():
        if header.startswith(signature) and mime_type in allowed_types:
            return True
    
    return False

def sanitize_input(input_string, max_length=255):
    """Sanitiza entrada de usuario"""
    if not input_string:
        return ""
    
    # Remover caracteres peligrosos
    dangerous_chars = ['<', '>', '"', "'", '&', '%', ';', '(', ')', '+', 'script']
    
    cleaned = str(input_string)[:max_length]
    
    for char in dangerous_chars:
        cleaned = cleaned.replace(char, '')
    
    return cleaned.strip()
