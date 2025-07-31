"""
Validadores para datos de entrada
"""
import re
from flask import jsonify

def validate_json(data, required_fields=None, optional_fields=None):
    """
    Validar datos JSON de entrada
    
    Args:
        data: Diccionario con datos a validar
        required_fields: Lista de campos requeridos
        optional_fields: Lista de campos opcionales permitidos
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not data:
        return False, "No se proporcionaron datos"
    
    if required_fields:
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                return False, f"Campo '{field}' es requerido"
    
    # Validar que no hay campos no permitidos
    if optional_fields is not None:
        allowed_fields = set(required_fields or []) | set(optional_fields or [])
        for field in data.keys():
            if field not in allowed_fields:
                return False, f"Campo '{field}' no está permitido"
    
    return True, None

def validate_email(email):
    """Validar formato de email"""
    if not email:
        return True  # Email es opcional en la mayoría de casos
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validar formato de teléfono"""
    if not phone:
        return True  # Teléfono es opcional
    
    # Permitir números con espacios, guiones y paréntesis
    pattern = r'^[\+]?[\d\s\-\(\)]+$'
    return re.match(pattern, phone) is not None and len(re.sub(r'[\s\-\(\)\+]', '', phone)) >= 10

def validate_cuit_dni(cuit_dni):
    """Validar formato de CUIT/DNI argentino"""
    if not cuit_dni:
        return True  # Es opcional
    
    # Remover guiones y espacios
    clean_cuit = re.sub(r'[\s\-]', '', cuit_dni)
    
    # CUIT: 11 dígitos, DNI: 8 dígitos
    if len(clean_cuit) in [8, 11] and clean_cuit.isdigit():
        return True
    
    return False

def validate_file_extension(filename, allowed_extensions=None):
    """
    Validar extensión de archivo
    
    Args:
        filename: Nombre del archivo
        allowed_extensions: Set de extensiones permitidas
    
    Returns:
        bool: True si la extensión es válida
    """
    if not filename or '.' not in filename:
        return False
    
    if allowed_extensions is None:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx'}
    
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in allowed_extensions

def validate_currency_amount(amount):
    """Validar monto monetario"""
    try:
        float_amount = float(amount)
        return float_amount >= 0
    except (ValueError, TypeError):
        return False

def validate_stock_quantity(quantity):
    """Validar cantidad de stock"""
    try:
        int_quantity = int(quantity)
        return int_quantity >= 0
    except (ValueError, TypeError):
        return False

def validate_percentage(percentage):
    """Validar porcentaje (0-100)"""
    try:
        float_percentage = float(percentage)
        return 0 <= float_percentage <= 100
    except (ValueError, TypeError):
        return False

def validate_rating(rating):
    """Validar calificación (1-5)"""
    try:
        float_rating = float(rating)
        return 1.0 <= float_rating <= 5.0
    except (ValueError, TypeError):
        return False

class ValidationError(Exception):
    """Excepción personalizada para errores de validación"""
    pass

def create_validation_error_response(message, status_code=400):
    """Crear respuesta JSON para errores de validación"""
    return jsonify({
        'success': False,
        'error': message,
        'type': 'validation_error'
    }), status_code
