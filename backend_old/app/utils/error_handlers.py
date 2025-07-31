"""
Manejadores de errores centralizados
"""
from flask import jsonify, request
from marshmallow import ValidationError as MarshmallowValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, InternalError, OperationalError
from werkzeug.exceptions import HTTPException
from .exceptions import BaseAPIException
from .logging_config import get_logger, log_error
from .db import reset_transaction
from typing import Tuple, Dict, Any
import psycopg2


def register_error_handlers(app):
    """Registrar todos los manejadores de errores"""
    
    logger = get_logger('error_handler')
    
    @app.errorhandler(BaseAPIException)
    def handle_api_exception(error: BaseAPIException) -> Tuple[Dict[str, Any], int]:
        """Manejar excepciones personalizadas de la API"""
        
        # Log del error
        logger.warning(
            "API Exception",
            error_type=type(error).__name__,
            message=error.message,
            status_code=error.status_code,
            endpoint=request.endpoint,
            method=request.method,
            ip=request.remote_addr
        )
        
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(InternalError)
    def handle_psycopg2_internal_error(error: InternalError) -> Tuple[Dict[str, Any], int]:
        """Manejar errores específicos de psycopg2 (PostgreSQL)"""
        
        # Log del error
        log_error(logger, error, {
            'error_type': 'postgresql_internal_error',
            'endpoint': request.endpoint
        })
        
        # Resetear la transacción
        reset_transaction()
        
        # Determinar el tipo específico de error
        error_str = str(error.orig) if hasattr(error, 'orig') else str(error)
        
        if 'current transaction is aborted' in error_str:
            message = 'Transacción de base de datos interrumpida. Se ha restablecido la conexión.'
            error_code = 'TransactionAborted'
        else:
            message = 'Error interno de la base de datos PostgreSQL'
            error_code = 'PostgreSQLInternalError'
        
        response_data = {
            'error': True,
            'message': message,
            'error_code': error_code,
            'status_code': 500,
            'transaction_reset': True
        }
        
        return jsonify(response_data), 500
    
    @app.errorhandler(OperationalError)
    def handle_operational_error(error: OperationalError) -> Tuple[Dict[str, Any], int]:
        """Manejar errores operacionales de base de datos"""
        
        # Log del error
        log_error(logger, error, {
            'error_type': 'database_operational_error',
            'endpoint': request.endpoint
        })
        
        # Resetear la transacción por si acaso
        reset_transaction()
        
        response_data = {
            'error': True,
            'message': 'Error de conexión con la base de datos',
            'error_code': 'DatabaseConnectionError',
            'status_code': 503,
            'transaction_reset': True
        }
        
        return jsonify(response_data), 503
    
    @app.errorhandler(MarshmallowValidationError)
    def handle_validation_error(error: MarshmallowValidationError) -> Tuple[Dict[str, Any], int]:
        """Manejar errores de validación de Marshmallow"""
        
        # Log del error de validación
        logger.warning(
            "Validation Error",
            validation_errors=error.messages,
            endpoint=request.endpoint,
            method=request.method
        )
        
        response_data = {
            'error': True,
            'message': 'Datos de entrada inválidos',
            'error_code': 'ValidationError',
            'status_code': 400,
            'field_errors': error.messages
        }
        
        return jsonify(response_data), 400
    
    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error: IntegrityError) -> Tuple[Dict[str, Any], int]:
        """Manejar errores de integridad de base de datos"""
        
        # Log del error
        log_error(logger, error, {
            'error_type': 'database_integrity',
            'endpoint': request.endpoint
        })
        
        # Determinar tipo específico de error de integridad
        error_message = str(error.orig)
        
        if 'UNIQUE constraint failed' in error_message or 'duplicate key' in error_message:
            message = 'Ya existe un registro con estos datos'
            error_code = 'DuplicateEntry'
        elif 'FOREIGN KEY constraint failed' in error_message:
            message = 'Referencia a un registro que no existe'
            error_code = 'ForeignKeyViolation'
        elif 'NOT NULL constraint failed' in error_message:
            message = 'Campo obligatorio faltante'
            error_code = 'NotNullViolation'
        else:
            message = 'Error de integridad en la base de datos'
            error_code = 'IntegrityError'
        
        response_data = {
            'error': True,
            'message': message,
            'error_code': error_code,
            'status_code': 422
        }
        
        return jsonify(response_data), 422
    
    @app.errorhandler(SQLAlchemyError)
    def handle_database_error(error: SQLAlchemyError) -> Tuple[Dict[str, Any], int]:
        """Manejar errores generales de SQLAlchemy"""
        
        # Log del error
        log_error(logger, error, {
            'error_type': 'database_error',
            'endpoint': request.endpoint
        })
        
        response_data = {
            'error': True,
            'message': 'Error interno de base de datos',
            'error_code': 'DatabaseError',
            'status_code': 500
        }
        
        return jsonify(response_data), 500
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException) -> Tuple[Dict[str, Any], int]:
        """Manejar excepciones HTTP de Werkzeug"""
        
        # Solo log errores 5xx como errores, 4xx como warnings
        if error.code >= 500:
            log_error(logger, error, {
                'error_type': 'http_error',
                'endpoint': request.endpoint,
                'status_code': error.code
            })
        else:
            logger.warning(
                "HTTP Error",
                status_code=error.code,
                description=error.description,
                endpoint=request.endpoint,
                method=request.method
            )
        
        response_data = {
            'error': True,
            'message': error.description or f'Error HTTP {error.code}',
            'error_code': error.name,
            'status_code': error.code
        }
        
        return jsonify(response_data), error.code
    
    @app.errorhandler(404)
    def handle_not_found(error) -> Tuple[Dict[str, Any], int]:
        """Manejar errores 404 específicamente"""
        
        logger.info(
            "Not Found",
            path=request.path,
            method=request.method,
            ip=request.remote_addr
        )
        
        response_data = {
            'error': True,
            'message': 'Recurso no encontrado',
            'error_code': 'NotFound',
            'status_code': 404,
            'path': request.path
        }
        
        return jsonify(response_data), 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error) -> Tuple[Dict[str, Any], int]:
        """Manejar errores de método no permitido"""
        
        logger.warning(
            "Method Not Allowed",
            method=request.method,
            path=request.path,
            allowed_methods=error.valid_methods if hasattr(error, 'valid_methods') else None
        )
        
        response_data = {
            'error': True,
            'message': f'Método {request.method} no permitido para este endpoint',
            'error_code': 'MethodNotAllowed',
            'status_code': 405,
            'allowed_methods': list(error.valid_methods) if hasattr(error, 'valid_methods') else None
        }
        
        return jsonify(response_data), 405
    
    @app.errorhandler(500)
    def handle_internal_error(error) -> Tuple[Dict[str, Any], int]:
        """Manejar errores internos del servidor"""
        
        log_error(logger, error, {
            'error_type': 'internal_server_error',
            'endpoint': request.endpoint
        })
        
        response_data = {
            'error': True,
            'message': 'Error interno del servidor',
            'error_code': 'InternalServerError',
            'status_code': 500
        }
        
        return jsonify(response_data), 500
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception) -> Tuple[Dict[str, Any], int]:
        """Manejar errores inesperados"""
        
        log_error(logger, error, {
            'error_type': 'unexpected_error',
            'endpoint': request.endpoint,
            'error_class': type(error).__name__
        })
        
        # En desarrollo, mostrar el error completo
        if app.config.get('DEBUG'):
            response_data = {
                'error': True,
                'message': str(error),
                'error_code': type(error).__name__,
                'status_code': 500,
                'debug_info': {
                    'error_type': type(error).__name__,
                    'error_message': str(error)
                }
            }
        else:
            # En producción, mensaje genérico
            response_data = {
                'error': True,
                'message': 'Error interno del servidor',
                'error_code': 'UnexpectedError',
                'status_code': 500
            }
        
        return jsonify(response_data), 500


def create_error_response(message: str, status_code: int = 400, 
                         error_code: str = None, **extra_data) -> Tuple[Dict[str, Any], int]:
    """Crear respuesta de error estandarizada"""
    
    response_data = {
        'error': True,
        'message': message,
        'error_code': error_code or 'GenericError',
        'status_code': status_code,
        **extra_data
    }
    
    return response_data, status_code


def create_success_response(data: Any = None, message: str = None, **extra_data) -> Dict[str, Any]:
    """Crear respuesta exitosa estandarizada"""
    
    response_data = {
        'success': True,
        'data': data,
        **extra_data
    }
    
    if message:
        response_data['message'] = message
    
    return response_data
