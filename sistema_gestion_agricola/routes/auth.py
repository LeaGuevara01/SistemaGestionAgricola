# routes/auth.py
from flask import Blueprint, request, jsonify, session, current_app
from ..middleware.auth import auth_manager
from ..utils.validation import sanitize_string
import hashlib
import time

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Usuarios demo (en producción usar base de datos)
DEMO_USERS = {
    'admin': {
        'password_hash': hashlib.sha256('admin123'.encode()).hexdigest(),
        'role': 'admin'
    },
    'user': {
        'password_hash': hashlib.sha256('user123'.encode()).hexdigest(),
        'role': 'user'
    }
}

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint de login"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Datos JSON requeridos'
            }), 400
        
        username = sanitize_string(data.get('username', ''))
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({
                'status': 'error',
                'message': 'Usuario y contraseña requeridos'
            }), 400
        
        # Verificar credenciales
        if username in DEMO_USERS:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if password_hash == DEMO_USERS[username]['password_hash']:
                
                # Crear sesión
                session_token = auth_manager.create_session(username)
                session['user_session'] = session_token
                
                return jsonify({
                    'status': 'success',
                    'message': 'Login exitoso',
                    'data': {
                        'session_token': session_token,
                        'username': username,
                        'role': DEMO_USERS[username]['role']
                    }
                })
        
        return jsonify({
            'status': 'error',
            'message': 'Credenciales inválidas'
        }), 401
        
    except Exception as e:
        current_app.logger.error(f"Error en login: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Endpoint de logout"""
    try:
        session_token = request.headers.get('Authorization')
        if session_token and session_token.startswith('Bearer '):
            token = session_token.split(' ')[1]
            auth_manager.revoke_session(token)
        
        if 'user_session' in session:
            auth_manager.revoke_session(session['user_session'])
            session.pop('user_session', None)
        
        return jsonify({
            'status': 'success',
            'message': 'Logout exitoso'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error en logout: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor'
        }), 500

@auth_bp.route('/generate-api-key', methods=['POST'])
def generate_api_key():
    """Generar API key para aplicaciones"""
    try:
        data = request.get_json()
        identifier = sanitize_string(data.get('identifier', 'unknown'))
        
        api_key = auth_manager.generate_api_key(identifier)
        
        return jsonify({
            'status': 'success',
            'message': 'API key generada',
            'data': {
                'api_key': api_key,
                'identifier': identifier
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error generando API key: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor'
        }), 500

@auth_bp.route('/validate', methods=['GET'])
def validate_session():
    """Validar sesión actual"""
    try:
        # Verificar API key
        api_key = request.headers.get('X-API-Key')
        if api_key and auth_manager.validate_api_key(api_key):
            return jsonify({
                'status': 'success',
                'message': 'API key válida',
                'data': {'type': 'api_key'}
            })
        
        # Verificar sesión
        session_token = request.headers.get('Authorization')
        if session_token and session_token.startswith('Bearer '):
            token = session_token.split(' ')[1]
            if auth_manager.validate_session(token):
                return jsonify({
                    'status': 'success',
                    'message': 'Sesión válida',
                    'data': {'type': 'session'}
                })
        
        return jsonify({
            'status': 'error',
            'message': 'Sesión inválida'
        }), 401
        
    except Exception as e:
        current_app.logger.error(f"Error validando sesión: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor'
        }), 500
