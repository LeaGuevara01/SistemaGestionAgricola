# utils/validation.py
import re
from flask import request, jsonify, current_app
from functools import wraps
from werkzeug.exceptions import BadRequest

def validate_required_fields(required_fields):
    """Decorator para validar campos requeridos en forms"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            missing_fields = []
            for field in required_fields:
                if field not in request.form or not request.form[field].strip():
                    missing_fields.append(field)
            
            if missing_fields:
                return jsonify({
                    'status': 'error',
                    'message': f'Campos requeridos faltantes: {", ".join(missing_fields)}'
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def sanitize_string(value, max_length=255, allow_html=False):
    """Sanitiza strings de entrada"""
    if not value:
        return ""
    
    value = str(value).strip()[:max_length]
    
    if not allow_html:
        # Escapar caracteres HTML
        value = value.replace('<', '&lt;').replace('>', '&gt;')
        value = value.replace('"', '&quot;').replace("'", '&#x27;')
        value = value.replace('&', '&amp;')
    
    return value

def validate_email(email):
    """Valida formato de email"""
    if not email:
        return True  # Campo opcional
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Valida formato de teléfono"""
    if not phone:
        return True  # Campo opcional
    
    # Permitir solo números, espacios, guiones y paréntesis
    pattern = r'^[\d\s\-\(\)\+]{7,20}$'
    return re.match(pattern, phone) is not None

def validate_alphanumeric(value, allow_spaces=True):
    """Valida que solo contenga caracteres alfanuméricos"""
    if not value:
        return True
    
    if allow_spaces:
        pattern = r'^[a-zA-Z0-9\s\-_\.]+$'
    else:
        pattern = r'^[a-zA-Z0-9\-_\.]+$'
    
    return re.match(pattern, value) is not None

def validate_numeric(value, min_val=None, max_val=None):
    """Valida valores numéricos"""
    try:
        num_val = float(value)
        if min_val is not None and num_val < min_val:
            return False
        if max_val is not None and num_val > max_val:
            return False
        return True
    except (ValueError, TypeError):
        return False

class InputValidator:
    """Clase para validar inputs de formularios"""
    
    @staticmethod
    def validate_componente_form(form_data):
        """Valida formulario de componente"""
        errors = []
        
        # Código requerido
        codigo = form_data.get('codigo', '').strip()
        if not codigo:
            errors.append("Código es requerido")
        elif not validate_alphanumeric(codigo, allow_spaces=False):
            errors.append("Código solo debe contener letras, números y guiones")
        
        # Nombre requerido
        nombre = form_data.get('nombre', '').strip()
        if not nombre:
            errors.append("Nombre es requerido")
        elif len(nombre) > 255:
            errors.append("Nombre demasiado largo")
        
        # Email opcional pero debe ser válido
        email = form_data.get('email', '').strip()
        if email and not validate_email(email):
            errors.append("Formato de email inválido")
        
        # Teléfono opcional pero debe ser válido
        telefono = form_data.get('telefono', '').strip()
        if telefono and not validate_phone(telefono):
            errors.append("Formato de teléfono inválido")
        
        return errors
    
    @staticmethod
    def validate_proveedor_form(form_data):
        """Valida formulario de proveedor"""
        errors = []
        
        # Nombre requerido
        nombre = form_data.get('nombre', '').strip()
        if not nombre:
            errors.append("Nombre es requerido")
        elif len(nombre) > 255:
            errors.append("Nombre demasiado largo")
        
        # Email opcional pero debe ser válido
        email = form_data.get('email', '').strip()
        if email and not validate_email(email):
            errors.append("Formato de email inválido")
        
        # Teléfono opcional pero debe ser válido
        telefono = form_data.get('telefono', '').strip()
        if telefono and not validate_phone(telefono):
            errors.append("Formato de teléfono inválido")
        
        return errors
