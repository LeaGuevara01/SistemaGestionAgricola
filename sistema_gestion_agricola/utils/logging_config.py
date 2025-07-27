# utils/logging_config.py
import logging
import logging.handlers
import os
from datetime import datetime
from flask import request

def setup_logging(app):
    """Configura logging para la aplicación"""
    
    if app.config.get('DEBUG'):
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    
    # Crear directorio de logs
    log_dir = os.path.join(app.root_path, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Configurar formato
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    
    # Handler para archivo general
    file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    
    # Handler para errores
    error_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'error.log'),
        maxBytes=10240000,
        backupCount=10
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Handler para accesos
    access_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'access.log'),
        maxBytes=10240000,
        backupCount=10
    )
    access_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(remote_addr)s - %(method)s %(url)s - %(status_code)s'
    ))
    
    # Configurar loggers
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_handler)
    app.logger.setLevel(log_level)
    
    # Logger para accesos
    access_logger = logging.getLogger('access')
    access_logger.addHandler(access_handler)
    access_logger.setLevel(logging.INFO)
    
    return access_logger

def log_request(app, access_logger):
    """Middleware para logging de requests"""
    
    @app.before_request
    def log_request_info():
        app.logger.debug(f'Request: {request.method} {request.url}')
    
    @app.after_request
    def log_response_info(response):
        access_logger.info('', extra={
            'remote_addr': request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
            'method': request.method,
            'url': request.url,
            'status_code': response.status_code
        })
        return response

class SecurityLogger:
    """Logger específico para eventos de seguridad"""
    
    def __init__(self, app=None):
        self.logger = logging.getLogger('security')
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        # Handler para eventos de seguridad
        log_dir = os.path.join(app.root_path, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        security_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, 'security.log'),
            maxBytes=10240000,
            backupCount=10
        )
        
        formatter = logging.Formatter(
            '[%(asctime)s] SECURITY - %(levelname)s: %(message)s'
        )
        security_handler.setFormatter(formatter)
        
        self.logger.addHandler(security_handler)
        self.logger.setLevel(logging.WARNING)
    
    def log_failed_login(self, username, ip_address):
        """Log de intento de login fallido"""
        self.logger.warning(f'Failed login attempt - Username: {username}, IP: {ip_address}')
    
    def log_rate_limit_exceeded(self, ip_address):
        """Log de rate limit excedido"""
        self.logger.warning(f'Rate limit exceeded - IP: {ip_address}')
    
    def log_invalid_file_upload(self, filename, ip_address):
        """Log de intento de subida de archivo inválido"""
        self.logger.warning(f'Invalid file upload attempt - File: {filename}, IP: {ip_address}')
    
    def log_sql_injection_attempt(self, query, ip_address):
        """Log de posible intento de inyección SQL"""
        self.logger.error(f'Possible SQL injection attempt - Query: {query}, IP: {ip_address}')
    
    def log_unauthorized_access(self, endpoint, ip_address):
        """Log de acceso no autorizado"""
        self.logger.warning(f'Unauthorized access attempt - Endpoint: {endpoint}, IP: {ip_address}')

# Instancia global
security_logger = SecurityLogger()
