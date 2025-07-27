# routes/analytics.py - Sistema de Analytics Avanzado
from flask import Blueprint, render_template, jsonify, request
from datetime import datetime, timedelta
from sqlalchemy import func, desc, and_, or_
from ..models import db, Maquina, Componente, Stock, Compra, Frecuencia, MaquinaComponente
from ..middleware.auth import optional_auth

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@analytics_bp.route('/')
@optional_auth
def dashboard():
    """Dashboard principal con métricas avanzadas"""
    return render_template('analytics/dashboard.html')

@analytics_bp.route('/api/metrics')
@optional_auth
def get_metrics():
    """API endpoint para métricas del dashboard"""
    try:
        # Métricas básicas
        total_maquinas = Maquina.query.count()
        total_componentes = Componente.query.count()
        maquinas_operativas = Maquina.query.filter_by(Estado='Operativa').count()
        maquinas_taller = Maquina.query.filter_by(Estado='En taller').count()
        
        # Stock crítico (componentes con stock bajo)
        stock_critico = db.session.query(
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
        
        # Componentes más utilizados
        componentes_populares = db.session.query(
            Componente.Nombre,
            func.count(MaquinaComponente.ID_Componente).label('uso_count')
        ).join(
            MaquinaComponente, Componente.ID == MaquinaComponente.ID_Componente
        ).group_by(Componente.ID).order_by(desc('uso_count')).limit(5).all()
        
        # Próximos mantenimientos (simulado)
        proximos_mantenimientos = db.session.query(
            Maquina.Nombre.label('maquina'),
            Componente.Nombre.label('componente'),
            Frecuencia.Frecuencia,
            Frecuencia.Unidad_tiempo
        ).join(
            Frecuencia, Maquina.ID == Frecuencia.ID_Maquina
        ).join(
            Componente, Frecuencia.ID_Componente == Componente.ID
        ).limit(10).all()
        
        return jsonify({
            'status': 'success',
            'data': {
                'resumen': {
                    'total_maquinas': total_maquinas,
                    'total_componentes': total_componentes,
                    'maquinas_operativas': maquinas_operativas,
                    'maquinas_taller': maquinas_taller,
                    'efectividad': round((maquinas_operativas / max(total_maquinas, 1)) * 100, 1)
                },
                'stock_critico': [
                    {'nombre': item.Nombre, 'stock': item.stock_actual}
                    for item in stock_critico
                ],
                'componentes_populares': [
                    {'nombre': item.Nombre, 'usos': item.uso_count}
                    for item in componentes_populares
                ],
                'proximos_mantenimientos': [
                    {
                        'maquina': item.maquina,
                        'componente': item.componente,
                        'frecuencia': f"{item.Frecuencia} {item.Unidad_tiempo}"
                    }
                    for item in proximos_mantenimientos
                ]
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@analytics_bp.route('/api/stock-timeline')
@optional_auth
def stock_timeline():
    """Timeline de movimientos de stock"""
    try:
        # Últimos 30 días de movimientos
        fecha_limite = datetime.now() - timedelta(days=30)
        
        movimientos = db.session.query(
            Stock.Fecha,
            Stock.Tipo,
            Stock.Cantidad,
            Componente.Nombre
        ).join(Componente).filter(
            Stock.Fecha >= fecha_limite
        ).order_by(Stock.Fecha.desc()).limit(50).all()
        
        return jsonify({
            'status': 'success',
            'data': [
                {
                    'fecha': item.Fecha.strftime('%Y-%m-%d'),
                    'tipo': item.Tipo,
                    'cantidad': item.Cantidad,
                    'componente': item.Nombre
                }
                for item in movimientos
            ]
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@analytics_bp.route('/api/efficiency-report')
@optional_auth
def efficiency_report():
    """Reporte de eficiencia por máquina"""
    try:
        # Análisis de eficiencia basado en estado y componentes
        maquinas_analisis = db.session.query(
            Maquina.Nombre,
            Maquina.Estado,
            Maquina.Año,
            func.count(MaquinaComponente.ID_Componente).label('total_componentes')
        ).outerjoin(
            MaquinaComponente, Maquina.ID == MaquinaComponente.ID_Maquina
        ).group_by(Maquina.ID).all()
        
        return jsonify({
            'status': 'success',
            'data': [
                {
                    'nombre': item.Nombre,
                    'estado': item.Estado,
                    'año': item.Año,
                    'componentes': item.total_componentes,
                    'score_eficiencia': calculate_efficiency_score(item)
                }
                for item in maquinas_analisis
            ]
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def calculate_efficiency_score(maquina):
    """Calcula un score de eficiencia para la máquina"""
    score = 100
    
    # Penalizar por estado
    if maquina.Estado == 'En taller':
        score -= 30
    elif maquina.Estado == 'Fuera de servicio':
        score -= 50
    
    # Bonus por antigüedad moderada
    if maquina.Año:
        años = datetime.now().year - maquina.Año
        if años > 10:
            score -= (años - 10) * 2
        elif años < 3:
            score += 10
    
    # Bonus por componentes (más componentes = más compleja pero potente)
    if maquina.total_componentes > 5:
        score += 10
    
    return max(0, min(100, score))
