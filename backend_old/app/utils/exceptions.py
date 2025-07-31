"""
Excepciones personalizadas para el sistema de gestión agrícola
"""
from typing import Dict, Any, Optional
from werkzeug.exceptions import HTTPException


class BaseAPIException(HTTPException):
    """Excepción base para todas las excepciones de la API"""
    
    def __init__(self, message: str, status_code: int = 500, payload: Dict[str, Any] = None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'error': True,
            'message': self.message,
            'error_code': self.__class__.__name__,
            'status_code': self.status_code,
            **self.payload
        }


class ValidationError(BaseAPIException):
    """Error de validación de datos"""
    
    def __init__(self, message: str = "Datos de entrada inválidos", 
                 field_errors: Dict[str, str] = None):
        super().__init__(message, 400, {'field_errors': field_errors or {}})


class NotFoundError(BaseAPIException):
    """Recurso no encontrado"""
    
    def __init__(self, resource: str, resource_id: Any = None):
        message = f"{resource} no encontrado"
        if resource_id:
            message += f" con ID: {resource_id}"
        super().__init__(message, 404, {'resource': resource, 'resource_id': resource_id})


class ConflictError(BaseAPIException):
    """Conflicto en la operación"""
    
    def __init__(self, message: str = "Conflicto en la operación", details: Dict[str, Any] = None):
        super().__init__(message, 409, {'details': details or {}})


class UnauthorizedError(BaseAPIException):
    """Error de autenticación"""
    
    def __init__(self, message: str = "No autorizado"):
        super().__init__(message, 401)


class ForbiddenError(BaseAPIException):
    """Error de autorización"""
    
    def __init__(self, message: str = "Acceso prohibido"):
        super().__init__(message, 403)


class DatabaseError(BaseAPIException):
    """Error de base de datos"""
    
    def __init__(self, message: str = "Error interno de base de datos", 
                 operation: str = None, table: str = None):
        super().__init__(message, 500, {
            'operation': operation,
            'table': table,
            'error_type': 'database_error'
        })


class BusinessLogicError(BaseAPIException):
    """Error de lógica de negocio"""
    
    def __init__(self, message: str, business_rule: str = None):
        super().__init__(message, 422, {
            'business_rule': business_rule,
            'error_type': 'business_logic_error'
        })


class ExternalServiceError(BaseAPIException):
    """Error de servicio externo"""
    
    def __init__(self, service_name: str, message: str = None):
        message = message or f"Error en servicio externo: {service_name}"
        super().__init__(message, 503, {
            'service_name': service_name,
            'error_type': 'external_service_error'
        })


class RateLimitExceededError(BaseAPIException):
    """Error de límite de velocidad excedido"""
    
    def __init__(self, retry_after: int = None):
        super().__init__("Límite de solicitudes excedido", 429, {
            'retry_after': retry_after,
            'error_type': 'rate_limit_exceeded'
        })


class FileProcessingError(BaseAPIException):
    """Error de procesamiento de archivos"""
    
    def __init__(self, file_name: str, operation: str, message: str = None):
        message = message or f"Error procesando archivo {file_name} en operación {operation}"
        super().__init__(message, 422, {
            'file_name': file_name,
            'operation': operation,
            'error_type': 'file_processing_error'
        })


class StockError(BusinessLogicError):
    """Error específico de stock"""
    
    def __init__(self, component_id: int, required_quantity: int, available_quantity: int):
        message = f"Stock insuficiente. Requerido: {required_quantity}, Disponible: {available_quantity}"
        super().__init__(message, 'insufficient_stock')
        self.payload.update({
            'component_id': component_id,
            'required_quantity': required_quantity,
            'available_quantity': available_quantity
        })


class ComponentNotFoundError(NotFoundError):
    """Error específico cuando no se encuentra un componente"""
    
    def __init__(self, component_id: int):
        super().__init__("Componente", component_id)


class MachineNotFoundError(NotFoundError):
    """Error específico cuando no se encuentra una máquina"""
    
    def __init__(self, machine_id: int):
        super().__init__("Máquina", machine_id)


class ProviderNotFoundError(NotFoundError):
    """Error específico cuando no se encuentra un proveedor"""
    
    def __init__(self, provider_id: int):
        super().__init__("Proveedor", provider_id)


class DuplicateEntryError(ConflictError):
    """Error cuando se intenta crear una entrada duplicada"""
    
    def __init__(self, entity: str, field: str, value: Any):
        message = f"{entity} con {field} '{value}' ya existe"
        super().__init__(message, {
            'entity': entity,
            'field': field,
            'value': str(value),
            'error_type': 'duplicate_entry'
        })
