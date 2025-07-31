"""
Utilidades para paginación
"""
from flask import request, url_for

def paginate_query(query, page=None, per_page=None, error_out=False):
    """
    Paginar query de SQLAlchemy
    
    Args:
        query: Query de SQLAlchemy
        page: Número de página (default: desde request.args)
        per_page: Items por página (default: desde request.args)
        error_out: Si debe lanzar error en página inválida
    
    Returns:
        Pagination object
    """
    if page is None:
        page = int(request.args.get('page', 1))
    
    if per_page is None:
        per_page = min(int(request.args.get('per_page', 20)), 100)
    
    return query.paginate(
        page=page,
        per_page=per_page,
        error_out=error_out
    )

def get_pagination_info(pagination, endpoint=None, **kwargs):
    """
    Obtener información de paginación para respuesta JSON
    
    Args:
        pagination: Objeto de paginación de SQLAlchemy
        endpoint: Endpoint para generar URLs de navegación
        **kwargs: Argumentos adicionales para URLs
    
    Returns:
        dict: Información de paginación
    """
    info = {
        'page': pagination.page,
        'pages': pagination.pages,
        'per_page': pagination.per_page,
        'total': pagination.total,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    }
    
    # Agregar URLs de navegación si se proporciona endpoint
    if endpoint:
        # Obtener argumentos actuales de la request
        args = dict(request.args)
        args.update(kwargs)
        
        if pagination.has_prev:
            args['page'] = pagination.prev_num
            info['prev_url'] = url_for(endpoint, **args)
        
        if pagination.has_next:
            args['page'] = pagination.next_num
            info['next_url'] = url_for(endpoint, **args)
        
        # URL de primera y última página
        args['page'] = 1
        info['first_url'] = url_for(endpoint, **args)
        
        args['page'] = pagination.pages
        info['last_url'] = url_for(endpoint, **args)
    
    return info

def create_pagination_response(items, pagination, endpoint=None, **kwargs):
    """
    Crear respuesta paginada estándar
    
    Args:
        items: Lista de items serializados
        pagination: Objeto de paginación
        endpoint: Endpoint para URLs de navegación
        **kwargs: Argumentos adicionales
    
    Returns:
        dict: Respuesta con datos y paginación
    """
    return {
        'success': True,
        'data': items,
        'pagination': get_pagination_info(pagination, endpoint, **kwargs)
    }
