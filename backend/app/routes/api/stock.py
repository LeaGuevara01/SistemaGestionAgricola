from flask import request, jsonify
from werkzeug.exceptions import BadRequest
from app.routes.api import api_bp
from app.models import Stock, Componente
from app.services.stock_service import StockService
from app.utils.db import db

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
        # Total de componentes
        total_componentes = Componente.query.filter_by(activo=True).count()
        
        # Componentes con bajo stock
        bajo_stock = StockService.obtener_componentes_bajo_stock()
        
        # Valor total del inventario
        valor_total = db.session.query(
            db.func.sum(Componente.stock_actual * Componente.precio_unitario)
        ).filter(Componente.activo == True).scalar() or 0
        
        return jsonify({
            'success': True,
            'data': {
                'total_componentes': total_componentes,
                'componentes_bajo_stock': len(bajo_stock),
                'valor_total_inventario': valor_total,
                'porcentaje_bajo_stock': round((len(bajo_stock) / total_componentes * 100) if total_componentes > 0 else 0, 2)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500