"""
Formateadores de datos
"""
from datetime import datetime, date
from decimal import Decimal

def format_currency(amount, currency='ARS', decimals=2):
    """
    Formatear monto monetario
    
    Args:
        amount: Monto a formatear
        currency: Código de moneda
        decimals: Cantidad de decimales
    
    Returns:
        str: Monto formateado
    """
    if amount is None:
        return f"{currency} 0.00"
    
    try:
        if isinstance(amount, (int, float, Decimal)):
            formatted = f"{float(amount):,.{decimals}f}"
            return f"{currency} {formatted}"
        else:
            return f"{currency} 0.00"
    except (ValueError, TypeError):
        return f"{currency} 0.00"

def format_date(date_obj, format_str='%d/%m/%Y'):
    """
    Formatear fecha
    
    Args:
        date_obj: Objeto datetime o date
        format_str: Formato de salida
    
    Returns:
        str: Fecha formateada
    """
    if date_obj is None:
        return None
    
    try:
        if isinstance(date_obj, str):
            # Intentar parsear si es string
            date_obj = datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
        
        if isinstance(date_obj, (datetime, date)):
            return date_obj.strftime(format_str)
        
        return str(date_obj)
    except (ValueError, AttributeError):
        return str(date_obj)

def format_datetime(datetime_obj, format_str='%d/%m/%Y %H:%M'):
    """
    Formatear fecha y hora
    
    Args:
        datetime_obj: Objeto datetime
        format_str: Formato de salida
    
    Returns:
        str: Fecha y hora formateada
    """
    return format_date(datetime_obj, format_str)

def format_percentage(value, decimals=2):
    """
    Formatear porcentaje
    
    Args:
        value: Valor a formatear
        decimals: Cantidad de decimales
    
    Returns:
        str: Porcentaje formateado
    """
    if value is None:
        return "0.00%"
    
    try:
        formatted = f"{float(value):.{decimals}f}"
        return f"{formatted}%"
    except (ValueError, TypeError):
        return "0.00%"

def format_number(value, decimals=0, thousands_separator=True):
    """
    Formatear número
    
    Args:
        value: Número a formatear
        decimals: Cantidad de decimales
        thousands_separator: Si usar separador de miles
    
    Returns:
        str: Número formateado
    """
    if value is None:
        return "0"
    
    try:
        if thousands_separator:
            return f"{float(value):,.{decimals}f}"
        else:
            return f"{float(value):.{decimals}f}"
    except (ValueError, TypeError):
        return "0"

def truncate_text(text, max_length=100, suffix='...'):
    """
    Truncar texto
    
    Args:
        text: Texto a truncar
        max_length: Longitud máxima
        suffix: Sufijo para texto truncado
    
    Returns:
        str: Texto truncado
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def format_file_size(size_bytes):
    """
    Formatear tamaño de archivo
    
    Args:
        size_bytes: Tamaño en bytes
    
    Returns:
        str: Tamaño formateado
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}"

def sanitize_filename(filename):
    """
    Sanitizar nombre de archivo
    
    Args:
        filename: Nombre original
    
    Returns:
        str: Nombre sanitizado
    """
    import re
    
    if not filename:
        return "file"
    
    # Remover caracteres especiales
    sanitized = re.sub(r'[^\w\-_\.]', '_', filename)
    
    # Remover múltiples guiones bajos consecutivos
    sanitized = re.sub(r'_{2,}', '_', sanitized)
    
    # Remover guiones bajos al inicio y final
    sanitized = sanitized.strip('_')
    
    return sanitized if sanitized else "file"
