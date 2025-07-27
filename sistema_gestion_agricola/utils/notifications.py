# utils/notifications.py - Sistema de Notificaciones
from datetime import datetime, timedelta
from flask import current_app
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os

class NotificationManager:
    """Gestor de notificaciones del sistema"""
    
    def __init__(self):
        self.notifications_file = 'logs/notifications.json'
        self.ensure_notifications_file()
    
    def ensure_notifications_file(self):
        """Asegura que existe el archivo de notificaciones"""
        os.makedirs('logs', exist_ok=True)
        if not os.path.exists(self.notifications_file):
            with open(self.notifications_file, 'w') as f:
                json.dump([], f)
    
    def create_notification(self, tipo, titulo, mensaje, prioridad='normal', user_id=None):
        """Crear nueva notificación"""
        notification = {
            'id': self.generate_id(),
            'tipo': tipo,  # 'mantenimiento', 'stock', 'sistema', 'alerta'
            'titulo': titulo,
            'mensaje': mensaje,
            'prioridad': prioridad,  # 'baja', 'normal', 'alta', 'critica'
            'fecha_creacion': datetime.now().isoformat(),
            'leida': False,
            'user_id': user_id,
            'acciones': []
        }
        
        self.save_notification(notification)
        
        # Auto-enviar si es crítica
        if prioridad == 'critica':
            self.send_email_notification(notification)
        
        return notification
    
    def generate_id(self):
        """Generar ID único para notificación"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def save_notification(self, notification):
        """Guardar notificación en archivo"""
        try:
            with open(self.notifications_file, 'r') as f:
                notifications = json.load(f)
            
            notifications.append(notification)
            
            # Mantener solo últimas 1000 notificaciones
            if len(notifications) > 1000:
                notifications = notifications[-1000:]
            
            with open(self.notifications_file, 'w') as f:
                json.dump(notifications, f, indent=2, default=str)
                
        except Exception as e:
            current_app.logger.error(f"Error guardando notificación: {e}")
    
    def get_notifications(self, user_id=None, limit=50, only_unread=False):
        """Obtener notificaciones"""
        try:
            with open(self.notifications_file, 'r') as f:
                notifications = json.load(f)
            
            # Filtrar por usuario si se especifica
            if user_id:
                notifications = [n for n in notifications if n.get('user_id') == user_id or n.get('user_id') is None]
            
            # Filtrar solo no leídas si se especifica
            if only_unread:
                notifications = [n for n in notifications if not n.get('leida', False)]
            
            # Ordenar por fecha (más recientes primero)
            notifications.sort(key=lambda x: x['fecha_creacion'], reverse=True)
            
            return notifications[:limit]
            
        except Exception as e:
            current_app.logger.error(f"Error obteniendo notificaciones: {e}")
            return []
    
    def mark_as_read(self, notification_id, user_id=None):
        """Marcar notificación como leída"""
        try:
            with open(self.notifications_file, 'r') as f:
                notifications = json.load(f)
            
            for notification in notifications:
                if notification['id'] == notification_id:
                    if user_id is None or notification.get('user_id') == user_id:
                        notification['leida'] = True
                        notification['fecha_lectura'] = datetime.now().isoformat()
                        break
            
            with open(self.notifications_file, 'w') as f:
                json.dump(notifications, f, indent=2, default=str)
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error marcando notificación como leída: {e}")
            return False
    
    def send_email_notification(self, notification):
        """Enviar notificación por email (simulado)"""
        try:
            # En un entorno real, configurarías SMTP aquí
            current_app.logger.info(f"EMAIL ENVIADO: {notification['titulo']} - {notification['mensaje']}")
            return True
        except Exception as e:
            current_app.logger.error(f"Error enviando email: {e}")
            return False
    
    def check_stock_alerts(self):
        """Verificar alertas de stock bajo"""
        from ..models import db, Componente, Stock
        from sqlalchemy import func
        
        try:
            # Componentes con stock bajo (menos de 5)
            stock_bajo = db.session.query(
                Componente.Nombre,
                func.coalesce(
                    func.sum(
                        func.case(
                            (Stock.Tipo == 'entrada', Stock.Cantidad),
                            (Stock.Tipo == 'salida', -Stock.Cantidad),
                            else_=0
                        )
                    ), 0
                ).label('stock_actual')
            ).outerjoin(Stock).group_by(Componente.ID).having(
                func.coalesce(
                    func.sum(
                        func.case(
                            (Stock.Tipo == 'entrada', Stock.Cantidad),
                            (Stock.Tipo == 'salida', -Stock.Cantidad),
                            else_=0
                        )
                    ), 0
                ) < 5
            ).all()
            
            for item in stock_bajo:
                self.create_notification(
                    tipo='stock',
                    titulo='Stock Crítico',
                    mensaje=f'El componente {item.Nombre} tiene stock crítico: {int(item.stock_actual)} unidades',
                    prioridad='alta'
                )
            
        except Exception as e:
            current_app.logger.error(f"Error verificando alertas de stock: {e}")
    
    def check_maintenance_alerts(self):
        """Verificar alertas de mantenimiento"""
        try:
            # Simulación de verificación de mantenimientos próximos
            # En una implementación real, consultarías la tabla de mantenimientos
            
            from ..models import db, Maquina
            
            maquinas_taller = Maquina.query.filter_by(Estado='En taller').all()
            
            for maquina in maquinas_taller:
                self.create_notification(
                    tipo='mantenimiento',
                    titulo='Máquina en Taller',
                    mensaje=f'La máquina {maquina.Nombre} está en taller y requiere atención',
                    prioridad='normal'
                )
                
        except Exception as e:
            current_app.logger.error(f"Error verificando alertas de mantenimiento: {e}")
    
    def get_notification_stats(self):
        """Obtener estadísticas de notificaciones"""
        try:
            notifications = self.get_notifications(limit=1000)
            
            total = len(notifications)
            no_leidas = len([n for n in notifications if not n.get('leida', False)])
            criticas = len([n for n in notifications if n.get('prioridad') == 'critica'])
            
            # Por tipo
            tipos = {}
            for notification in notifications:
                tipo = notification.get('tipo', 'otros')
                tipos[tipo] = tipos.get(tipo, 0) + 1
            
            return {
                'total': total,
                'no_leidas': no_leidas,
                'criticas': criticas,
                'por_tipo': tipos
            }
            
        except Exception as e:
            current_app.logger.error(f"Error obteniendo estadísticas: {e}")
            return {'total': 0, 'no_leidas': 0, 'criticas': 0, 'por_tipo': {}}

# Instancia global
notification_manager = NotificationManager()

def create_sample_notifications():
    """Crear notificaciones de ejemplo para demostración"""
    
    # Notificación de stock crítico
    notification_manager.create_notification(
        tipo='stock',
        titulo='⚠️ Stock Crítico - Filtros de Aceite',
        mensaje='Los filtros de aceite tienen solo 2 unidades en stock. Se recomienda realizar un pedido urgente.',
        prioridad='alta'
    )
    
    # Notificación de mantenimiento programado
    notification_manager.create_notification(
        tipo='mantenimiento',
        titulo='🔧 Mantenimiento Programado',
        mensaje='La cosechadora John Deere requiere mantenimiento preventivo del sistema hidráulico programado para mañana.',
        prioridad='normal'
    )
    
    # Notificación de máquina fuera de servicio
    notification_manager.create_notification(
        tipo='alerta',
        titulo='🚨 Tractor Fuera de Servicio',
        mensaje='El tractor Case IH está fuera de servicio debido a una falla en el motor. Contactar al técnico inmediatamente.',
        prioridad='critica'
    )
    
    # Notificación del sistema
    notification_manager.create_notification(
        tipo='sistema',
        titulo='🔄 Actualización Completada',
        mensaje='El sistema de gestión agrícola ha sido actualizado exitosamente con nuevas funcionalidades de reportes.',
        prioridad='normal'
    )
    
    # Notificación de nuevo pedido
    notification_manager.create_notification(
        tipo='stock',
        titulo='📦 Nuevo Pedido Recibido',
        mensaje='Se ha recibido un pedido de 50 unidades de correas para las máquinas cosechadoras.',
        prioridad='baja'
    )
    
    return "Notificaciones de ejemplo creadas exitosamente"

# Funciones de conveniencia
def notify_stock_critical(componente_nombre, stock_actual):
    """Notificación de stock crítico"""
    return notification_manager.create_notification(
        tipo='stock',
        titulo='⚠️ Stock Crítico',
        mensaje=f'El componente {componente_nombre} tiene solo {stock_actual} unidades en stock',
        prioridad='alta'
    )

def notify_maintenance_due(maquina_nombre, componente_nombre):
    """Notificación de mantenimiento debido"""
    return notification_manager.create_notification(
        tipo='mantenimiento',
        titulo='🔧 Mantenimiento Programado',
        mensaje=f'La máquina {maquina_nombre} requiere mantenimiento del componente {componente_nombre}',
        prioridad='normal'
    )

def notify_machine_down(maquina_nombre):
    """Notificación de máquina fuera de servicio"""
    return notification_manager.create_notification(
        tipo='alerta',
        titulo='🚨 Máquina Fuera de Servicio',
        mensaje=f'La máquina {maquina_nombre} está fuera de servicio',
        prioridad='critica'
    )

def notify_system_update(mensaje):
    """Notificación de actualización del sistema"""
    return notification_manager.create_notification(
        tipo='sistema',
        titulo='🔄 Actualización del Sistema',
        mensaje=mensaje,
        prioridad='normal'
    )
