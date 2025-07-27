# routes/mantenimiento.py - Sistema de Mantenimiento Predictivo
from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, func
from ..models import db, Maquina, Componente, Frecuencia, MaquinaComponente
from ..middleware.auth import optional_auth
from ..utils.validation import sanitize_string

mantenimiento_bp = Blueprint('mantenimiento', __name__, url_prefix='/mantenimiento')

# Modelo simple para tracking de mantenimientos
class RegistroMantenimiento(db.Model):
    __tablename__ = 'registros_mantenimiento'
    
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_Maquina = db.Column(db.Integer, db.ForeignKey('maquinas.ID', ondelete='CASCADE'))
    ID_Componente = db.Column(db.Integer, db.ForeignKey('componentes.ID', ondelete='CASCADE'))
    Fecha_Mantenimiento = db.Column(db.DateTime, default=datetime.utcnow)
    Tipo_Mantenimiento = db.Column(db.String)  # 'preventivo', 'correctivo', 'urgente'
    Descripcion = db.Column(db.String)
    Costo = db.Column(db.Float)
    Estado = db.Column(db.String, default='completado')  # 'programado', 'en_proceso', 'completado'
    Proximo_Mantenimiento = db.Column(db.DateTime)
    
    maquina = db.relationship('Maquina', backref='mantenimientos')
    componente = db.relationship('Componente', backref='mantenimientos')

@mantenimiento_bp.route('/')
@optional_auth
def dashboard_mantenimiento():
    """Dashboard de mantenimiento"""
    return render_template('mantenimiento/dashboard.html')

@mantenimiento_bp.route('/programar')
@optional_auth
def programar_mantenimiento():
    """Formulario para programar mantenimiento"""
    maquinas = Maquina.query.all()
    componentes = Componente.query.all()
    return render_template('mantenimiento/programar.html', 
                         maquinas=maquinas, componentes=componentes)

@mantenimiento_bp.route('/programar', methods=['POST'])
@optional_auth
def guardar_mantenimiento():
    """Guardar nuevo mantenimiento programado"""
    try:
        maquina_id = int(request.form.get('maquina_id'))
        componente_id = int(request.form.get('componente_id'))
        fecha_programada = datetime.strptime(request.form.get('fecha_programada'), '%Y-%m-%d')
        tipo = sanitize_string(request.form.get('tipo_mantenimiento'))
        descripcion = sanitize_string(request.form.get('descripcion'))
        costo_estimado = float(request.form.get('costo_estimado', 0))
        
        # Calcular próximo mantenimiento basado en frecuencia
        frecuencia = Frecuencia.query.filter_by(
            ID_Maquina=maquina_id, 
            ID_Componente=componente_id
        ).first()
        
        proximo_mantenimiento = None
        if frecuencia:
            if frecuencia.Unidad_tiempo == 'días':
                proximo_mantenimiento = fecha_programada + timedelta(days=frecuencia.Frecuencia)
            elif frecuencia.Unidad_tiempo == 'semanas':
                proximo_mantenimiento = fecha_programada + timedelta(weeks=frecuencia.Frecuencia)
            elif frecuencia.Unidad_tiempo == 'meses':
                proximo_mantenimiento = fecha_programada + timedelta(days=frecuencia.Frecuencia * 30)
        
        nuevo_mantenimiento = RegistroMantenimiento(
            ID_Maquina=maquina_id,
            ID_Componente=componente_id,
            Fecha_Mantenimiento=fecha_programada,
            Tipo_Mantenimiento=tipo,
            Descripcion=descripcion,
            Costo=costo_estimado,
            Estado='programado',
            Proximo_Mantenimiento=proximo_mantenimiento
        )
        
        db.session.add(nuevo_mantenimiento)
        db.session.commit()
        
        flash('Mantenimiento programado exitosamente', 'success')
        return redirect(url_for('mantenimiento.dashboard_mantenimiento'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al programar mantenimiento: {str(e)}', 'error')
        return redirect(url_for('mantenimiento.programar_mantenimiento'))

@mantenimiento_bp.route('/api/proximos')
@optional_auth
def proximos_mantenimientos():
    """API para obtener próximos mantenimientos"""
    try:
        # Mantenimientos programados para los próximos 30 días
        fecha_limite = datetime.now() + timedelta(days=30)
        
        mantenimientos = db.session.query(
            RegistroMantenimiento,
            Maquina.Nombre.label('maquina_nombre'),
            Componente.Nombre.label('componente_nombre')
        ).join(
            Maquina, RegistroMantenimiento.ID_Maquina == Maquina.ID
        ).join(
            Componente, RegistroMantenimiento.ID_Componente == Componente.ID
        ).filter(
            and_(
                RegistroMantenimiento.Fecha_Mantenimiento <= fecha_limite,
                RegistroMantenimiento.Estado.in_(['programado', 'en_proceso'])
            )
        ).order_by(RegistroMantenimiento.Fecha_Mantenimiento).all()
        
        return jsonify({
            'status': 'success',
            'data': [
                {
                    'id': item.RegistroMantenimiento.ID,
                    'maquina': item.maquina_nombre,
                    'componente': item.componente_nombre,
                    'fecha': item.RegistroMantenimiento.Fecha_Mantenimiento.strftime('%Y-%m-%d'),
                    'tipo': item.RegistroMantenimiento.Tipo_Mantenimiento,
                    'descripcion': item.RegistroMantenimiento.Descripcion,
                    'estado': item.RegistroMantenimiento.Estado,
                    'costo': item.RegistroMantenimiento.Costo,
                    'dias_restantes': (item.RegistroMantenimiento.Fecha_Mantenimiento - datetime.now()).days
                }
                for item in mantenimientos
            ]
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@mantenimiento_bp.route('/api/alertas')
@optional_auth
def alertas_mantenimiento():
    """Alertas de mantenimiento urgente"""
    try:
        hoy = datetime.now()
        
        # Mantenimientos vencidos
        vencidos = db.session.query(
            RegistroMantenimiento,
            Maquina.Nombre.label('maquina_nombre'),
            Componente.Nombre.label('componente_nombre')
        ).join(Maquina).join(Componente).filter(
            and_(
                RegistroMantenimiento.Fecha_Mantenimiento < hoy,
                RegistroMantenimiento.Estado == 'programado'
            )
        ).all()
        
        # Mantenimientos en los próximos 7 días
        proximos_urgentes = db.session.query(
            RegistroMantenimiento,
            Maquina.Nombre.label('maquina_nombre'),
            Componente.Nombre.label('componente_nombre')
        ).join(Maquina).join(Componente).filter(
            and_(
                RegistroMantenimiento.Fecha_Mantenimiento >= hoy,
                RegistroMantenimiento.Fecha_Mantenimiento <= hoy + timedelta(days=7),
                RegistroMantenimiento.Estado == 'programado'
            )
        ).all()
        
        return jsonify({
            'status': 'success',
            'data': {
                'vencidos': len(vencidos),
                'proximos_urgentes': len(proximos_urgentes),
                'detalle_vencidos': [
                    {
                        'maquina': item.maquina_nombre,
                        'componente': item.componente_nombre,
                        'dias_vencido': (hoy - item.RegistroMantenimiento.Fecha_Mantenimiento).days
                    }
                    for item in vencidos
                ],
                'detalle_proximos': [
                    {
                        'maquina': item.maquina_nombre,
                        'componente': item.componente_nombre,
                        'dias_restantes': (item.RegistroMantenimiento.Fecha_Mantenimiento - hoy).days
                    }
                    for item in proximos_urgentes
                ]
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@mantenimiento_bp.route('/completar/<int:mantenimiento_id>', methods=['POST'])
@optional_auth
def completar_mantenimiento(mantenimiento_id):
    """Marcar mantenimiento como completado"""
    try:
        mantenimiento = RegistroMantenimiento.query.get_or_404(mantenimiento_id)
        
        costo_real = float(request.form.get('costo_real', mantenimiento.Costo))
        observaciones = sanitize_string(request.form.get('observaciones', ''))
        
        mantenimiento.Estado = 'completado'
        mantenimiento.Costo = costo_real
        mantenimiento.Descripcion += f" | Observaciones: {observaciones}"
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Mantenimiento completado'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@mantenimiento_bp.route('/api/estadisticas')
@optional_auth
def estadisticas_mantenimiento():
    """Estadísticas de mantenimiento"""
    try:
        # Últimos 6 meses
        fecha_inicio = datetime.now() - timedelta(days=180)
        
        # Costos por mes
        costos_mensuales = db.session.query(
            func.date_trunc('month', RegistroMantenimiento.Fecha_Mantenimiento).label('mes'),
            func.sum(RegistroMantenimiento.Costo).label('costo_total')
        ).filter(
            RegistroMantenimiento.Fecha_Mantenimiento >= fecha_inicio
        ).group_by('mes').order_by('mes').all()
        
        # Tipos de mantenimiento
        tipos_mantenimiento = db.session.query(
            RegistroMantenimiento.Tipo_Mantenimiento,
            func.count(RegistroMantenimiento.ID).label('cantidad')
        ).filter(
            RegistroMantenimiento.Fecha_Mantenimiento >= fecha_inicio
        ).group_by(RegistroMantenimiento.Tipo_Mantenimiento).all()
        
        return jsonify({
            'status': 'success',
            'data': {
                'costos_mensuales': [
                    {
                        'mes': item.mes.strftime('%Y-%m'),
                        'costo': float(item.costo_total)
                    }
                    for item in costos_mensuales
                ],
                'tipos_mantenimiento': [
                    {
                        'tipo': item.Tipo_Mantenimiento,
                        'cantidad': item.cantidad
                    }
                    for item in tipos_mantenimiento
                ]
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
