# middleware/error_handlers.py
from flask import jsonify, current_app
import logging
import traceback

def register_error_handlers(app):
    """Registra manejadores de errores seguros para la aplicación"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'status': 'error',
            'message': 'Solicitud incorrecta',
            'error_code': 400
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'status': 'error',
            'message': 'No autorizado',
            'error_code': 401
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'status': 'error',
            'message': 'Acceso prohibido',
            'error_code': 403
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'status': 'error',
            'message': 'Recurso no encontrado',
            'error_code': 404
        }), 404

    @app.errorhandler(413)
    def file_too_large(error):
        return jsonify({
            'status': 'error',
            'message': 'Archivo demasiado grande',
            'error_code': 413
        }), 413

    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return jsonify({
            'status': 'error',
            'message': 'Demasiadas solicitudes',
            'error_code': 429
        }), 429

    @app.errorhandler(500)
    def internal_error(error):
        # Log del error completo para debugging
        current_app.logger.error(f"Error interno: {str(error)}")
        current_app.logger.error(traceback.format_exc())
        
        # Respuesta genérica para el usuario
        if current_app.config.get('DEBUG'):
            return jsonify({
                'status': 'error',
                'message': f'Error interno del servidor: {str(error)}',
                'error_code': 500
            }), 500
        else:
            return jsonify({
                'status': 'error',
                'message': 'Error interno del servidor',
                'error_code': 500
            }), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        # Log del error para debugging
        current_app.logger.error(f"Error no manejado: {str(error)}")
        current_app.logger.error(traceback.format_exc())
        
        # No exponer detalles en producción
        if current_app.config.get('DEBUG'):
            return jsonify({
                'status': 'error',
                'message': str(error),
                'error_code': 500
            }), 500
        else:
            return jsonify({
                'status': 'error',
                'message': 'Error interno del servidor',
                'error_code': 500
            }), 500
