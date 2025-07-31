from flask import request, jsonify
from . import api_bp
from ...models import Stock, Componente
from ...utils.db import db


@api_bp.route('/stock', methods=['GET'])
def get_stock():
    """Obtener inventario de stock"""
    try:
        # Parámetros de filtrado
        componente_id = request.args.get('componente_id')
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)
        
        print(f"🔍 Consultando stock: componente_id={componente_id}, page={page}")
        
        # Query base
        query = Stock.query
        
        # Filtrar por componente si se especifica
        if componente_id:
            query = query.filter(Stock.componente_id == componente_id)
        
        # Ordenar por fecha/ID más reciente
        query = query.order_by(Stock.id.desc())
        
        # Paginación simple
        try:
            total = query.count()
            offset = (page - 1) * per_page
            movimientos = query.offset(offset).limit(per_page).all()
            
            has_next = offset + per_page < total
            has_prev = page > 1
            pages = (total + per_page - 1) // per_page
            
        except Exception as e:
            print(f"❌ Error en paginación de stock: {e}")
            movimientos = query.limit(50).all()
            total = len(movimientos)
            has_next = False
            has_prev = False
            pages = 1
            page = 1
            per_page = total
        
        # Convertir a diccionarios
        stock_data = []
        for mov in movimientos:
            try:
                mov_dict = mov.to_dict()
                
                # Agregar información del componente si existe
                if hasattr(mov, 'componente_id') and mov.componente_id:
                    try:
                        componente = Componente.query.get(mov.componente_id)
                        if componente:
                            mov_dict['componente'] = {
                                'id': componente.id,
                                'nombre': getattr(componente, 'Nombre', 'Sin nombre')
                            }
                    except Exception as e:
                        print(f"⚠️ Error obteniendo componente para stock {mov.id}: {e}")
                
                stock_data.append(mov_dict)
                
            except Exception as e:
                print(f"⚠️ Error serializando stock {mov.id}: {e}")
                # Fallback manual
                stock_data.append({
                    'id': mov.id,
                    'componente_id': getattr(mov, 'componente_id', None),
                    'cantidad': getattr(mov, 'cantidad', 0),
                    'tipo': getattr(mov, 'tipo_movimiento', 'unknown')
                })
        
        response_data = {
            'success': True,
            'data': {
                'stock': stock_data,
                'pagination': {
                    'page': page,
                    'pages': pages,
                    'per_page': per_page,
                    'total': total,
                    'has_next': has_next,
                    'has_prev': has_prev
                }
            },
            'message': f"Se encontraron {total} movimientos de stock"
        }
        
        print(f"✅ Stock consultado: {total} movimientos encontrados")
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"❌ Error en get_stock: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error interno del servidor'
        }), 500


@api_bp.route('/stock/test', methods=['GET'])
def test_stock():
    """Endpoint de prueba para stock"""
    try:
        total_movimientos = Stock.query.count()
        total_componentes = Componente.query.count()
        
        sample_data = {}
        if total_movimientos > 0:
            primer_movimiento = Stock.query.first()
            sample_data['sample_movimiento'] = primer_movimiento.to_dict()
        
        return jsonify({
            'success': True,
            'message': f'Stock API funcionando. {total_movimientos} movimientos, {total_componentes} componentes',
            'data': sample_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error en stock: {str(e)}'
        }), 500
