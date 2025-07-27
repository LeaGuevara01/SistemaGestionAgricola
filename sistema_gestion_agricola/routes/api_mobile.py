# routes/api_mobile.py - API Móvil Avanzada
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, func, desc
from ..models import db, Maquina, Componente, Stock, Compra, Frecuencia, MaquinaComponente, Proveedor
from ..middleware.auth import require_auth, optional_auth
from ..utils.validation import sanitize_string
from ..utils.files import save_uploaded_file

api_mobile_bp = Blueprint('api_mobile', __name__, url_prefix='/api/mobile')

@api_mobile_bp.route('/dashboard')
@optional_auth
def mobile_dashboard():
    """Dashboard optimizado para móvil"""
    try:
        # Resumen rápido
        total_maquinas = Maquina.query.count()
        maquinas_operativas = Maquina.query.filter_by(Estado='Operativa').count()
        componentes_stock_bajo = db.session.query(Componente).join(Stock).group_by(Componente.ID).having(
            func.sum(func.case((Stock.Tipo == 'entrada', Stock.Cantidad), else_=-Stock.Cantidad)) < 5
        ).count()
        
        # Alertas urgentes
        alertas = []
        
        # Stock crítico
        if componentes_stock_bajo > 0:
            alertas.append({
                'tipo': 'stock_critico',
                'mensaje': f'{componentes_stock_bajo} componentes con stock bajo',
                'prioridad': 'alta'
            })
        
        # Máquinas en taller
        maquinas_taller = Maquina.query.filter_by(Estado='En taller').count()
        if maquinas_taller > 0:
            alertas.append({
                'tipo': 'maquinas_taller',
                'mensaje': f'{maquinas_taller} máquinas en taller',
                'prioridad': 'media'
            })
        
        return jsonify({
            'status': 'success',
            'data': {
                'resumen': {
                    'total_maquinas': total_maquinas,
                    'maquinas_operativas': maquinas_operativas,
                    'eficiencia': round((maquinas_operativas / max(total_maquinas, 1)) * 100, 1),
                    'componentes_stock_bajo': componentes_stock_bajo
                },
                'alertas': alertas,
                'ultima_actualizacion': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_mobile_bp.route('/maquinas')
@optional_auth
def maquinas_mobile():
    """Lista de máquinas optimizada para móvil"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        search = sanitize_string(request.args.get('search', ''))
        estado_filter = request.args.get('estado', '')
        
        query = Maquina.query
        
        if search:
            query = query.filter(
                or_(
                    Maquina.Nombre.ilike(f'%{search}%'),
                    Maquina.Marca.ilike(f'%{search}%'),
                    Maquina.Modelo.ilike(f'%{search}%')
                )
            )
        
        if estado_filter:
            query = query.filter(Maquina.Estado == estado_filter)
        
        maquinas = query.order_by(Maquina.Nombre).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'status': 'success',
            'data': {
                'maquinas': [
                    {
                        'id': m.ID,
                        'codigo': m.Codigo,
                        'nombre': m.Nombre,
                        'marca': m.Marca,
                        'modelo': m.Modelo,
                        'año': m.Año,
                        'estado': m.Estado,
                        'foto': m.Foto,
                        'estado_color': get_estado_color(m.Estado)
                    }
                    for m in maquinas.items
                ],
                'pagination': {
                    'page': maquinas.page,
                    'pages': maquinas.pages,
                    'per_page': maquinas.per_page,
                    'total': maquinas.total,
                    'has_next': maquinas.has_next,
                    'has_prev': maquinas.has_prev
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_mobile_bp.route('/maquinas/<int:maquina_id>')
@optional_auth
def maquina_detalle_mobile(maquina_id):
    """Detalle de máquina optimizado para móvil"""
    try:
        maquina = Maquina.query.get_or_404(maquina_id)
        
        # Componentes asociados con frecuencias
        componentes = db.session.query(
            Componente,
            Frecuencia.Frecuencia.label('frecuencia'),
            Frecuencia.Unidad_tiempo.label('unidad_tiempo')
        ).join(
            MaquinaComponente, MaquinaComponente.ID_Componente == Componente.ID
        ).outerjoin(
            Frecuencia, 
            and_(Frecuencia.ID_Maquina == maquina_id, Frecuencia.ID_Componente == Componente.ID)
        ).filter(MaquinaComponente.ID_Maquina == maquina_id).all()
        
        return jsonify({
            'status': 'success',
            'data': {
                'maquina': {
                    'id': maquina.ID,
                    'codigo': maquina.Codigo,
                    'nombre': maquina.Nombre,
                    'marca': maquina.Marca,
                    'modelo': maquina.Modelo,
                    'año': maquina.Año,
                    'estado': maquina.Estado,
                    'observaciones': maquina.Observaciones,
                    'foto': maquina.Foto,
                    'estado_color': get_estado_color(maquina.Estado)
                },
                'componentes': [
                    {
                        'id': c.Componente.ID,
                        'nombre': c.Componente.Nombre,
                        'descripcion': c.Componente.Descripcion,
                        'tipo': c.Componente.Tipo,
                        'frecuencia': c.frecuencia,
                        'unidad_tiempo': c.unidad_tiempo,
                        'frecuencia_texto': f"{c.frecuencia} {c.unidad_tiempo}" if c.frecuencia else "No definida"
                    }
                    for c in componentes
                ]
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_mobile_bp.route('/stock')
@optional_auth
def stock_mobile():
    """Inventario optimizado para móvil"""
    try:
        search = sanitize_string(request.args.get('search', ''))
        tipo_filter = request.args.get('tipo', '')
        stock_bajo = request.args.get('stock_bajo', '').lower() == 'true'
        
        # Query base con stock actual
        query = db.session.query(
            Componente,
            func.coalesce(
                func.sum(
                    func.case(
                        (Stock.Tipo == 'entrada', Stock.Cantidad),
                        (Stock.Tipo == 'salida', -Stock.Cantidad),
                        else_=0
                    )
                ), 0
            ).label('stock_actual')
        ).outerjoin(Stock, Componente.ID == Stock.ID_Componente).group_by(Componente.ID)
        
        if search:
            query = query.filter(
                or_(
                    Componente.Nombre.ilike(f'%{search}%'),
                    Componente.Descripcion.ilike(f'%{search}%')
                )
            )
        
        if tipo_filter:
            query = query.filter(Componente.Tipo == tipo_filter)
        
        if stock_bajo:
            query = query.having(func.coalesce(
                func.sum(
                    func.case(
                        (Stock.Tipo == 'entrada', Stock.Cantidad),
                        (Stock.Tipo == 'salida', -Stock.Cantidad),
                        else_=0
                    )
                ), 0
            ) < 5)
        
        resultados = query.order_by(Componente.Nombre).all()
        
        return jsonify({
            'status': 'success',
            'data': [
                {
                    'id': item.Componente.ID,
                    'codigo': item.Componente.ID_Componente,
                    'nombre': item.Componente.Nombre,
                    'descripcion': item.Componente.Descripcion,
                    'tipo': item.Componente.Tipo,
                    'stock_actual': int(item.stock_actual),
                    'stock_estado': get_stock_estado(int(item.stock_actual)),
                    'foto': item.Componente.Foto
                }
                for item in resultados
            ]
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_mobile_bp.route('/stock/movimiento', methods=['POST'])
@require_auth
def agregar_movimiento_stock():
    """Agregar movimiento de stock desde móvil"""
    try:
        data = request.get_json()
        
        componente_id = int(data.get('componente_id'))
        cantidad = int(data.get('cantidad'))
        tipo = sanitize_string(data.get('tipo'))  # 'entrada' o 'salida'
        observacion = sanitize_string(data.get('observacion', ''))
        
        if tipo not in ['entrada', 'salida']:
            return jsonify({
                'status': 'error',
                'message': 'Tipo debe ser entrada o salida'
            }), 400
        
        if cantidad <= 0:
            return jsonify({
                'status': 'error',
                'message': 'Cantidad debe ser mayor a 0'
            }), 400
        
        # Verificar que el componente existe
        componente = Componente.query.get(componente_id)
        if not componente:
            return jsonify({
                'status': 'error',
                'message': 'Componente no encontrado'
            }), 404
        
        # Crear movimiento
        from ..models.stock import Stock
        movimiento = Stock(
            ID_Componente=componente_id,
            Cantidad=cantidad,
            Tipo=tipo,
            Observacion=observacion
        )
        
        db.session.add(movimiento)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Movimiento de {tipo} registrado exitosamente',
            'data': {
                'id': movimiento.ID,
                'componente': componente.Nombre,
                'cantidad': cantidad,
                'tipo': tipo
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@api_mobile_bp.route('/upload/foto', methods=['POST'])
@require_auth
def upload_foto_mobile():
    """Upload de foto desde móvil"""
    try:
        if 'foto' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No se proporcionó archivo'
            }), 400
        
        file = request.files['foto']
        tipo = request.form.get('tipo', 'general')  # 'maquina', 'componente', 'general'
        
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No se seleccionó archivo'
            }), 400
        
        filename = save_uploaded_file(file, tipo)
        
        if filename:
            return jsonify({
                'status': 'success',
                'message': 'Foto subida exitosamente',
                'data': {
                    'filename': filename,
                    'url': f'/static/fotos/{tipo}s/{filename}'
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Error al procesar archivo'
            }), 400
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def get_estado_color(estado):
    """Obtiene color para el estado de la máquina"""
    colores = {
        'Operativa': '#28a745',
        'En taller': '#ffc107',
        'Fuera de servicio': '#dc3545',
        'En mantenimiento': '#17a2b8'
    }
    return colores.get(estado, '#6c757d')

def get_stock_estado(cantidad):
    """Obtiene estado del stock basado en cantidad"""
    if cantidad <= 0:
        return {'texto': 'Sin stock', 'color': '#dc3545'}
    elif cantidad < 5:
        return {'texto': 'Stock bajo', 'color': '#ffc107'}
    elif cantidad < 20:
        return {'texto': 'Stock normal', 'color': '#28a745'}
    else:
        return {'texto': 'Stock alto', 'color': '#007bff'}
