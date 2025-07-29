from flask import request, jsonify
from werkzeug.exceptions import BadRequest
from . import api_bp
from ...models import Stock, Componente
from ...services.stock_service import StockService
from ...utils.db import db

@api_bp.route('/stock', methods=['GET'])
def get_stock():
    try:
        componente_id = request.args.get('componente_id')
        limit = int(request.args.get('limit', 100))
        
        movimientos = StockService.obtener_historial(componente_id, limit)
        
        return jsonify({
            'success': True,
            'data': [mov.to_dict(include_relations=True) for mov in movimientos]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/stock/movimiento', methods=['POST'])
def registrar_movimiento():
    try:
        data = request.get_json()
        
        # Validaciones
        required_fields = ['componente_id', 'tipo_movimiento', 'cantidad']
        for field in required_fields:
            if field not in data:
                raise BadRequest(f"El campo '{field}' es requerido")
        
        movimiento = StockService.registrar_movimiento(
            componente_id=data['componente_id'],
            tipo_movimiento=data['tipo_movimiento'],
            cantidad=data['cantidad'],
            motivo=data.get('motivo'),
            observaciones=data.get('observaciones'),
            usuario=data.get('usuario')
        )
        
        return jsonify({
            'success': True,
            'data': movimiento.to_dict(include_relations=True),
            'message': 'Movimiento registrado exitosamente'
        }), 201
        
    except BadRequest as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/stock/bajo-stock', methods=['GET'])
def get_bajo_stock():
    try:
        componentes = StockService.obtener_componentes_bajo_stock()
        
        return jsonify({
            'success': True,
            'data': [comp.to_dict() for comp in componentes],
            'total': len(componentes)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/stock/resumen', methods=['GET'])
def get_resumen_stock():
    try:
        # Total de componentes (sin filtro activo que no existe)
        total_componentes = Componente.query.count()
        
        # Obtener balance por componente
        stock_data = {}
        stock_items = Stock.query.all()
        
        for item in stock_items:
            comp_id = item.componente_id
            cantidad = getattr(item, 'Cantidad', 0) or 0
            tipo = getattr(item, 'Tipo', '').lower() if getattr(item, 'Tipo') else ''
            
            if comp_id not in stock_data:
                stock_data[comp_id] = {'entradas': 0, 'salidas': 0}
            
            if 'entrada' in tipo:
                stock_data[comp_id]['entradas'] += cantidad
            elif 'salida' in tipo:
                stock_data[comp_id]['salidas'] += cantidad
        
        # Calcular componentes con bajo stock (balance < 10)
        bajo_stock_count = 0
        valor_total = 0
        
        for comp_id, data in stock_data.items():
            balance = data['entradas'] - data['salidas']
            if balance < 10:  # Umbral de bajo stock
                bajo_stock_count += 1
            
            # Calcular valor (si el componente existe y tiene precio)
            componente = Componente.query.get(comp_id)
            if componente and componente.precio:
                valor_total += balance * componente.precio
        
        return jsonify({
            'success': True,
            'data': {
                'total_componentes': total_componentes,
                'componentes_bajo_stock': bajo_stock_count,
                'valor_total_inventario': round(valor_total, 2),
                'porcentaje_bajo_stock': round((bajo_stock_count / total_componentes * 100) if total_componentes > 0 else 0, 2),
                'componentes_con_stock': len(stock_data)
            }
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500