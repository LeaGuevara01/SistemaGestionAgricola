"""
Configuración de logging estructurado profesional
"""
import os
import sys
import logging
import structlog
from datetime import datetime
from typing import Any, Dict

class CustomFormatter(logging.Formatter):
    """Formateador personalizado para logging estructurado"""
    
    COLORS = {
        logging.DEBUG: '\033[36m',    # Cyan
        logging.INFO: '\033[32m',     # Green
        logging.WARNING: '\033[33m',  # Yellow
        logging.ERROR: '\033[31m',    # Red
        logging.CRITICAL: '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        # Agregar timestamp y nivel
        record.timestamp = datetime.utcnow().isoformat()
        
        # Colorear el nivel si es development
        if os.getenv('FLASK_ENV') == 'development':
            color = self.COLORS.get(record.levelno, '')
            record.levelname = f"{color}{record.levelname}{self.RESET}"
        
        return super().format(record)

def configure_logging(app):
    """Configurar logging estructurado según el ambiente"""
    
    # Nivel de logging según ambiente
    env = os.getenv('FLASK_ENV', 'development')
    log_level = logging.DEBUG if env == 'development' else logging.INFO
    
    # Configurar structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if env == 'production' else structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configurar handler principal
    handler = logging.StreamHandler(sys.stdout)
    
    if env == 'development':
        # Formato amigable para desarrollo
        formatter = CustomFormatter(
            '%(timestamp)s | %(levelname)s | %(name)s | %(message)s'
        )
    else:
        # Formato JSON para producción
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"logger": "%(name)s", "message": "%(message)s", '
            '"module": "%(module)s", "function": "%(funcName)s", "line": %(lineno)d}'
        )
    
    handler.setFormatter(formatter)
    handler.setLevel(log_level)
    
    # Configurar logger de la aplicación
    app_logger = logging.getLogger('elorza_backend')
    app_logger.setLevel(log_level)
    app_logger.addHandler(handler)
    
    # Configurar loggers de Flask y SQLAlchemy
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(
        logging.INFO if env == 'development' else logging.WARNING
    )
    
    # Logger para auditoría (siempre INFO)
    audit_logger = logging.getLogger('elorza_audit')
    audit_logger.setLevel(logging.INFO)
    audit_logger.addHandler(handler)
    
    return structlog.get_logger('elorza_backend')

def get_logger(name: str = None) -> structlog.BoundLogger:
    """Obtener logger estructurado"""
    return structlog.get_logger(name or 'elorza_backend')

def log_request(logger, request, response_status: int = None, **extra_data):
    """Log de request HTTP estructurado"""
    logger.info(
        "HTTP Request",
        method=request.method,
        path=request.path,
        remote_addr=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        response_status=response_status,
        **extra_data
    )

def log_database_operation(logger, operation: str, table: str, record_id: Any = None, **extra_data):
    """Log de operación de base de datos"""
    logger.info(
        "Database Operation",
        operation=operation,
        table=table,
        record_id=record_id,
        **extra_data
    )

def log_business_event(logger, event: str, entity: str, entity_id: Any = None, **extra_data):
    """Log de evento de negocio"""
    logger.info(
        "Business Event",
        event=event,
        entity=entity,
        entity_id=entity_id,
        **extra_data
    )

def log_error(logger, error: Exception, context: Dict[str, Any] = None):
    """Log de error estructurado"""
    logger.error(
        "Application Error",
        error_type=type(error).__name__,
        error_message=str(error),
        context=context or {},
        exc_info=True
    )
