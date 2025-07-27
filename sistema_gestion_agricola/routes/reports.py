# routes/reports.py - Sistema de Reportes Avanzados
from flask import Blueprint, request, jsonify, render_template, make_response, send_file
from functools import wraps
from ..models import db, Maquina, Componente, Stock
from sqlalchemy import func, desc, asc, and_, or_, extract
from datetime import datetime, timedelta, date
import json
import io
import csv
from collections import defaultdict
import base64
import matplotlib
matplotlib.use('Agg')  # Backend sin GUI
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.dates import DateFormatter
import pandas as pd

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

# Decorador simple para reemplazar login_required
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Por ahora, permitir acceso sin autenticación
        return f(*args, **kwargs)
    return decorated_function

@reports_bp.route('/')
@login_required
def index():
    """Panel principal de reportes"""
    return render_template('reports/index.html', now=datetime.now)

@reports_bp.route('/stock')
@login_required
def stock_report():
    """Reporte de inventario de stock"""
    # Obtener parámetros de filtro
    filtro_tipo = request.args.get('tipo', 'all')
    fecha_desde = request.args.get('desde')
    fecha_hasta = request.args.get('hasta')
    formato = request.args.get('format', 'html')
    
    # Consulta base para stock actual - versión simplificada
    stock_query = db.session.query(
        Componente.ID,
        Componente.Nombre,
        Componente.Tipo,
        func.coalesce(
            func.sum(Stock.Cantidad), 0
        ).label('stock_actual'),
        func.min(Stock.Fecha).label('primer_movimiento'),
        func.max(Stock.Fecha).label('ultimo_movimiento')
    ).outerjoin(Stock).group_by(Componente.ID)
    
    # Aplicar filtros de fecha si se proporcionan
    if fecha_desde:
        stock_query = stock_query.filter(Stock.Fecha >= fecha_desde)
    if fecha_hasta:
        stock_query = stock_query.filter(Stock.Fecha <= fecha_hasta)
    
    resultados = stock_query.all()
    
    # Calcular estadísticas
    stock_total = sum(item.stock_actual for item in resultados)
    items_sin_stock = len([item for item in resultados if item.stock_actual == 0])
    items_stock_bajo = len([item for item in resultados if 0 < item.stock_actual < 5])
    
    # Agrupar por categoría
    por_categoria = defaultdict(lambda: {'cantidad': 0, 'stock_total': 0})
    for item in resultados:
        categoria = item.Tipo or 'Sin categoría'
        por_categoria[categoria]['cantidad'] += 1
        por_categoria[categoria]['stock_total'] += item.stock_actual
    
    data = {
        'items': resultados,
        'estadisticas': {
            'total_items': len(resultados),
            'stock_total': stock_total,
            'items_sin_stock': items_sin_stock,
            'items_stock_bajo': items_stock_bajo
        },
        'por_categoria': dict(por_categoria),
        'fecha_generacion': datetime.now()
    }
    
    if formato == 'json':
        return jsonify(data)
    elif formato == 'csv':
        return generate_csv_stock(resultados)
    else:
        return render_template('reports/stock.html', **data)

@reports_bp.route('/movimientos')
@login_required
def movimientos_report():
    """Reporte de movimientos de stock"""
    fecha_desde = request.args.get('desde', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    fecha_hasta = request.args.get('hasta', datetime.now().strftime('%Y-%m-%d'))
    tipo_movimiento = request.args.get('tipo', 'all')
    formato = request.args.get('format', 'html')
    
    # Consulta de movimientos
    movimientos_query = db.session.query(
        Stock.ID,
        Stock.Fecha,
        Stock.Tipo,
        Stock.Cantidad,
        Stock.Observacion,
        Componente.Nombre.label('componente_nombre')
    ).join(Componente)
    
    # Aplicar filtros
    movimientos_query = movimientos_query.filter(
        and_(Stock.Fecha >= fecha_desde, Stock.Fecha <= fecha_hasta)
    )
    
    if tipo_movimiento != 'all':
        movimientos_query = movimientos_query.filter(Stock.Tipo == tipo_movimiento)
    
    movimientos = movimientos_query.order_by(desc(Stock.Fecha)).all()
    
    # Estadísticas de movimientos
    total_entradas = sum(m.Cantidad for m in movimientos if m.Tipo == 'entrada')
    total_salidas = sum(m.Cantidad for m in movimientos if m.Tipo == 'salida')
    
    # Movimientos por día
    movimientos_por_dia = defaultdict(lambda: {'entradas': 0, 'salidas': 0})
    for movimiento in movimientos:
        fecha_str = movimiento.Fecha.strftime('%Y-%m-%d')
        if movimiento.Tipo == 'entrada':
            movimientos_por_dia[fecha_str]['entradas'] += movimiento.Cantidad
        else:
            movimientos_por_dia[fecha_str]['salidas'] += movimiento.Cantidad
    
    data = {
        'movimientos': movimientos,
        'estadisticas': {
            'total_movimientos': len(movimientos),
            'total_entradas': total_entradas,
            'total_salidas': total_salidas,
            'saldo_neto': total_entradas - total_salidas
        },
        'movimientos_por_dia': dict(movimientos_por_dia),
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'fecha_generacion': datetime.now()
    }
    
    if formato == 'json':
        return jsonify(data)
    elif formato == 'csv':
        return generate_csv_movimientos(movimientos)
    else:
        return render_template('reports/movimientos.html', **data)

@reports_bp.route('/maquinas')
@login_required
def maquinas_report():
    """Reporte de estado de máquinas"""
    formato = request.args.get('format', 'html')
    
    # Obtener todas las máquinas con estadísticas
    maquinas = db.session.query(Maquina).all()
    
    # Estadísticas por estado
    estados = defaultdict(int)
    for maquina in maquinas:
        estados[maquina.Estado] += 1
    
    # Máquinas por ubicación
    ubicaciones = defaultdict(int)
    for maquina in maquinas:
        ubicacion = getattr(maquina, 'Ubicacion', 'Sin ubicación')
        ubicaciones[ubicacion] += 1
    
    # Máquinas más antiguas (por fecha de adquisición simulada)
    maquinas_ordenadas = sorted(maquinas, key=lambda x: x.ID)
    
    data = {
        'maquinas': maquinas,
        'estadisticas': {
            'total_maquinas': len(maquinas),
            'operativas': estados.get('Operativa', 0),
            'en_taller': estados.get('En taller', 0),
            'fuera_servicio': estados.get('Fuera de servicio', 0)
        },
        'por_estado': dict(estados),
        'por_ubicacion': dict(ubicaciones),
        'fecha_generacion': datetime.now()
    }
    
    if formato == 'json':
        return jsonify(data)
    elif formato == 'csv':
        return generate_csv_maquinas(maquinas)
    else:
        return render_template('reports/maquinas.html', **data)

@reports_bp.route('/analytics')
@login_required
def analytics_report():
    """Reporte de análisis avanzado"""
    dias = request.args.get('dias', 30, type=int)
    fecha_fin = datetime.now()
    fecha_inicio = fecha_fin - timedelta(days=dias)
    
    # Tendencias de stock
    movimientos_periodo = db.session.query(
        Stock.Fecha,
        Stock.Tipo,
        Stock.Cantidad,
        Componente.Tipo
    ).join(Componente).filter(
        Stock.Fecha >= fecha_inicio
    ).all()
    
    # Análisis de tendencias
    tendencias_diarias = defaultdict(lambda: {'entradas': 0, 'salidas': 0})
    for mov in movimientos_periodo:
        fecha_str = mov.Fecha.strftime('%Y-%m-%d')
        if mov.Tipo == 'entrada':
            tendencias_diarias[fecha_str]['entradas'] += mov.Cantidad
        else:
            tendencias_diarias[fecha_str]['salidas'] += mov.Cantidad
    
    # Predicciones simples (tendencia lineal)
    fechas = sorted(tendencias_diarias.keys())
    if len(fechas) >= 7:  # Necesitamos al menos una semana de datos
        ultimos_7_dias = fechas[-7:]
        promedio_entradas = sum(tendencias_diarias[f]['entradas'] for f in ultimos_7_dias) / 7
        promedio_salidas = sum(tendencias_diarias[f]['salidas'] for f in ultimos_7_dias) / 7
        
        predicciones = []
        for i in range(1, 8):  # Próximos 7 días
            fecha_pred = (fecha_fin + timedelta(days=i)).strftime('%Y-%m-%d')
            predicciones.append({
                'fecha': fecha_pred,
                'entradas_predichas': round(promedio_entradas),
                'salidas_predichas': round(promedio_salidas)
            })
    else:
        predicciones = []
    
    # Componentes más activos
    actividad_componentes = db.session.query(
        Componente.Nombre,
        func.count(Stock.ID).label('total_movimientos'),
        func.sum(Stock.Cantidad).label('cantidad_total')
    ).join(Stock).filter(
        Stock.Fecha >= fecha_inicio
    ).group_by(Componente.ID).order_by(desc('total_movimientos')).limit(10).all()
    
    data = {
        'periodo_dias': dias,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'tendencias_diarias': dict(tendencias_diarias),
        'predicciones': predicciones,
        'componentes_activos': actividad_componentes,
        'fecha_generacion': datetime.now()
    }
    
    return render_template('reports/analytics.html', **data)

@reports_bp.route('/custom')
@login_required
def custom_report():
    """Constructor de reportes personalizados"""
    return render_template('reports/custom.html')

@reports_bp.route('/api/custom', methods=['POST'])
@login_required
def api_custom_report():
    """API para generar reportes personalizados"""
    data = request.get_json()
    
    tipo_reporte = data.get('tipo')
    filtros = data.get('filtros', {})
    campos = data.get('campos', [])
    
    try:
        if tipo_reporte == 'stock_personalizado':
            resultado = generate_custom_stock_report(filtros, campos)
        elif tipo_reporte == 'movimientos_personalizado':
            resultado = generate_custom_movements_report(filtros, campos)
        elif tipo_reporte == 'maquinas_personalizado':
            resultado = generate_custom_machines_report(filtros, campos)
        else:
            return jsonify({'error': 'Tipo de reporte no válido'}), 400
        
        return jsonify({
            'status': 'success',
            'data': resultado
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_custom_stock_report(filtros, campos):
    """Generar reporte personalizado de stock"""
    query = db.session.query(Componente)
    
    # Aplicar filtros
    if filtros.get('categoria'):
        query = query.filter(Componente.Tipo == filtros['categoria'])
    
    if filtros.get('stock_minimo'):
        # Aquí necesitarías una subconsulta más compleja para filtrar por stock
        pass
    
    componentes = query.all()
    
    # Formatear resultado según campos solicitados
    resultado = []
    for comp in componentes:
        item = {}
        if 'nombre' in campos:
            item['nombre'] = comp.Nombre
        if 'categoria' in campos:
            item['categoria'] = comp.Tipo
        if 'descripcion' in campos:
            item['descripcion'] = comp.Descripcion
        resultado.append(item)
    
    return resultado

def generate_custom_movements_report(filtros, campos):
    """Generar reporte personalizado de movimientos"""
    query = db.session.query(Stock).join(Componente)
    
    # Aplicar filtros de fecha
    if filtros.get('fecha_desde'):
        query = query.filter(Stock.Fecha >= filtros['fecha_desde'])
    if filtros.get('fecha_hasta'):
        query = query.filter(Stock.Fecha <= filtros['fecha_hasta'])
    
    if filtros.get('tipo'):
        query = query.filter(Stock.Tipo == filtros['tipo'])
    
    movimientos = query.all()
    
    resultado = []
    for mov in movimientos:
        item = {}
        if 'fecha' in campos:
            item['fecha'] = mov.Fecha.isoformat()
        if 'tipo' in campos:
            item['tipo'] = mov.Tipo
        if 'cantidad' in campos:
            item['cantidad'] = mov.Cantidad
        if 'componente' in campos:
            item['componente'] = mov.componente.Nombre
        resultado.append(item)
    
    return resultado

def generate_custom_machines_report(filtros, campos):
    """Generar reporte personalizado de máquinas"""
    query = db.session.query(Maquina)
    
    if filtros.get('estado'):
        query = query.filter(Maquina.Estado == filtros['estado'])
    
    if filtros.get('ubicacion'):
        query = query.filter(Maquina.Ubicacion == filtros['ubicacion'])
    
    maquinas = query.all()
    
    resultado = []
    for maq in maquinas:
        item = {}
        if 'nombre' in campos:
            item['nombre'] = maq.Nombre
        if 'estado' in campos:
            item['estado'] = maq.Estado
        if 'ubicacion' in campos:
            item['ubicacion'] = getattr(maq, 'Ubicacion', 'Sin ubicación')
        if 'descripcion' in campos:
            item['descripcion'] = maq.Observaciones
        resultado.append(item)
    
    return resultado

def generate_csv_stock(items):
    """Generar CSV de reporte de stock"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Cabeceras
    writer.writerow(['ID', 'Nombre', 'Categoría', 'Stock Actual', 'Primer Movimiento', 'Último Movimiento'])
    
    # Datos
    for item in items:
        writer.writerow([
            item.ID,
            item.Nombre,
            item.Tipo or 'Sin categoría',
            item.stock_actual,
            item.primer_movimiento.strftime('%Y-%m-%d') if item.primer_movimiento else 'N/A',
            item.ultimo_movimiento.strftime('%Y-%m-%d') if item.ultimo_movimiento else 'N/A'
        ])
    
    output.seek(0)
    
    return make_response(
        output.getvalue(),
        200,
        {
            'Content-Type': 'text/csv',
            'Content-Disposition': f'attachment; filename=reporte_stock_{datetime.now().strftime("%Y%m%d")}.csv'
        }
    )

def generate_csv_movimientos(movimientos):
    """Generar CSV de movimientos"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Fecha', 'Tipo', 'Componente', 'Cantidad', 'Observación'])
    
    for mov in movimientos:
        writer.writerow([
            mov.Fecha.strftime('%Y-%m-%d %H:%M'),
            mov.Tipo,
            mov.componente_nombre,
            mov.Cantidad,
            mov.Observacion or ''
        ])
    
    output.seek(0)
    
    return make_response(
        output.getvalue(),
        200,
        {
            'Content-Type': 'text/csv',
            'Content-Disposition': f'attachment; filename=movimientos_{datetime.now().strftime("%Y%m%d")}.csv'
        }
    )

def generate_csv_maquinas(maquinas):
    """Generar CSV de máquinas"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['ID', 'Nombre', 'Estado', 'Ubicación', 'Descripción'])
    
    for maq in maquinas:
        writer.writerow([
            maq.ID,
            maq.Nombre,
            maq.Estado,
            getattr(maq, 'Ubicacion', 'Sin ubicación'),
            maq.Observaciones or ''
        ])
    
    output.seek(0)
    
    return make_response(
        output.getvalue(),
        200,
        {
            'Content-Type': 'text/csv',
            'Content-Disposition': f'attachment; filename=maquinas_{datetime.now().strftime("%Y%m%d")}.csv'
        }
    )

@reports_bp.route('/chart/<chart_type>')
@login_required
def generate_chart(chart_type):
    """Generar gráficos dinámicos"""
    try:
        plt.style.use('seaborn-v0_8')
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if chart_type == 'stock_por_categoria':
            # Gráfico de stock por categoría
            categorias = db.session.query(
                Componente.Tipo,
                func.count(Componente.ID).label('cantidad')
            ).group_by(Componente.Tipo).all()
            
            labels = [cat.Tipo or 'Sin categoría' for cat in categorias]
            valores = [cat.cantidad for cat in categorias]
            
            ax.pie(valores, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.set_title('Distribución de Componentes por Categoría')
            
        elif chart_type == 'movimientos_tiempo':
            # Gráfico de movimientos en el tiempo
            fecha_inicio = datetime.now() - timedelta(days=30)
            movimientos = db.session.query(
                func.date(Stock.Fecha).label('fecha'),
                func.count(Stock.ID).label('cantidad')
            ).filter(Stock.Fecha >= fecha_inicio).group_by(func.date(Stock.Fecha)).all()
            
            fechas = [mov.fecha for mov in movimientos]
            cantidades = [mov.cantidad for mov in movimientos]
            
            ax.plot(fechas, cantidades, marker='o', linewidth=2, markersize=6)
            ax.set_title('Movimientos de Stock en los Últimos 30 Días')
            ax.set_xlabel('Fecha')
            ax.set_ylabel('Número de Movimientos')
            ax.tick_params(axis='x', rotation=45)
            
        else:
            ax.text(0.5, 0.5, 'Tipo de gráfico no válido', ha='center', va='center')
            ax.set_title('Error')
        
        plt.tight_layout()
        
        # Convertir a base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        return jsonify({
            'status': 'success',
            'image': f'data:image/png;base64,{img_str}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
