# routes/notifications.py - Rutas de Notificaciones
from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from functools import wraps
from ..utils.notifications import notification_manager
import json

# Decorador simple para reemplazar login_required
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function

# Objeto simulado para current_user
class MockUser:
    ID = 1
    is_admin = True

current_user = MockUser()

notifications_bp = Blueprint('notifications', __name__, url_prefix='/notifications')

@notifications_bp.route('/')
@login_required
def index():
    """Página principal de notificaciones"""
    notifications = notification_manager.get_notifications(user_id=current_user.ID)
    stats = notification_manager.get_notification_stats()
    
    return render_template('notifications/index.html', 
                         notifications=notifications,
                         stats=stats)

@notifications_bp.route('/api/list')
@login_required
def api_list():
    """API para obtener lista de notificaciones"""
    limit = request.args.get('limit', 20, type=int)
    only_unread = request.args.get('unread', False, type=bool)
    
    notifications = notification_manager.get_notifications(
        user_id=current_user.ID,
        limit=limit,
        only_unread=only_unread
    )
    
    return jsonify({
        'status': 'success',
        'notifications': notifications
    })

@notifications_bp.route('/api/mark_read/<notification_id>', methods=['POST'])
@login_required
def api_mark_read(notification_id):
    """Marcar notificación como leída"""
    success = notification_manager.mark_as_read(notification_id, current_user.ID)
    
    if success:
        return jsonify({'status': 'success', 'message': 'Notificación marcada como leída'})
    else:
        return jsonify({'status': 'error', 'message': 'Error al marcar notificación'}), 400

@notifications_bp.route('/api/stats')
@login_required
def api_stats():
    """Obtener estadísticas de notificaciones"""
    stats = notification_manager.get_notification_stats()
    
    return jsonify({
        'status': 'success',
        'stats': stats
    })

@notifications_bp.route('/api/test', methods=['POST'])
@login_required
def api_test():
    """Crear notificación de prueba"""
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': 'No autorizado'}), 403
    
    data = request.get_json()
    
    notification = notification_manager.create_notification(
        tipo=data.get('tipo', 'sistema'),
        titulo=data.get('titulo', 'Notificación de Prueba'),
        mensaje=data.get('mensaje', 'Esta es una notificación de prueba'),
        prioridad=data.get('prioridad', 'normal'),
        user_id=current_user.ID
    )
    
    return jsonify({
        'status': 'success',
        'notification': notification,
        'message': 'Notificación de prueba creada'
    })

@notifications_bp.route('/widget')
@login_required
def widget():
    """Widget de notificaciones para incluir en otras páginas"""
    notifications = notification_manager.get_notifications(
        user_id=current_user.ID,
        limit=5,
        only_unread=True
    )
    
    return render_template('notifications/widget.html', notifications=notifications)

@notifications_bp.route('/run_checks', methods=['POST'])
@login_required
def run_checks():
    """Ejecutar verificaciones de alertas"""
    if not current_user.is_admin:
        flash('No tienes permisos para ejecutar verificaciones', 'error')
        return redirect(url_for('notifications.index'))
    
    try:
        # Ejecutar verificaciones
        notification_manager.check_stock_alerts()
        notification_manager.check_maintenance_alerts()
        
        flash('Verificaciones ejecutadas correctamente', 'success')
        
    except Exception as e:
        flash(f'Error ejecutando verificaciones: {str(e)}', 'error')
    
    return redirect(url_for('notifications.index'))

@notifications_bp.route('/api/create_samples', methods=['POST'])
@login_required
def api_create_samples():
    """Crear notificaciones de ejemplo para demostración"""
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': 'No autorizado'}), 403
    
    try:
        from ..utils.notifications import create_sample_notifications
        result = create_sample_notifications()
        
        return jsonify({
            'status': 'success',
            'message': result
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500

@notifications_bp.route('/settings')
@login_required
def settings():
    """Configuración de notificaciones"""
    return render_template('notifications/settings.html')

@notifications_bp.route('/api/settings', methods=['POST'])
@login_required
def api_update_settings():
    """Actualizar configuración de notificaciones"""
    data = request.get_json()
    
    # Aquí guardarías las preferencias del usuario
    # Por simplicidad, solo retornamos éxito
    
    return jsonify({
        'status': 'success',
        'message': 'Configuración actualizada'
    })
