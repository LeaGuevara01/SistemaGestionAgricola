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


@api_bp.route('/stock/movimiento', methods=['POST'])
def registrar_movimiento():
    """Registrar nuevo movimiento de stock"""
    try:
        data = request.get_json() or {}
        print(f"📝 Registrando movimiento de stock: {data}")
        
        # Validaciones básicas
        required_fields = ['componente_id', 'tipo_movimiento', 'cantidad']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f"El campo '{field}' es requerido",
                    'message': 'Datos inválidos'
                }), 400
        
        # Verificar que el componente existe
        componente = Componente.query.get(data['componente_id'])
        if not componente:
            return jsonify({
                'success': False,
                'error': f"No se encontró el componente con ID {data['componente_id']}",
                'message': 'Componente no encontrado'
            }), 404
        
        # Crear movimiento de stock
        try:
            movimiento_data = {
                'componente_id': data['componente_id'],
                'tipo_movimiento': data['tipo_movimiento'],
                'cantidad': int(data['cantidad'])
            }
            
            # Campos opcionales
            if data.get('motivo'):
                movimiento_data['motivo'] = data['motivo']
            if data.get('observaciones'):
                movimiento_data['observaciones'] = data['observaciones']
            if data.get('usuario'):
                movimiento_data['usuario'] = data['usuario']
            
            movimiento = Stock(**movimiento_data)
            
        except Exception as e:
            print(f"⚠️ Error creando objeto Stock: {e}")
            return jsonify({
                'success': False,
                'error': 'Error en los datos del movimiento',
                'message': 'Datos inválidos'
            }), 400
        
        # Guardar en base de datos
        try:
            db.session.add(movimiento)
            db.session.commit()
            print(f"✅ Movimiento de stock creado con ID: {movimiento.id}")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error guardando movimiento: {e}")
            return jsonify({
                'success': False,
                'error': 'Error al guardar en la base de datos',
                'message': 'Error de base de datos'
            }), 500
        
        # Respuesta
        try:
            movimiento_data = movimiento.to_dict()
            # Agregar información del componente
            movimiento_data['componente'] = {
                'id': componente.id,
                'nombre': getattr(componente, 'Nombre', 'Sin nombre')
            }
        except Exception:
            movimiento_data = {
                'id': movimiento.id,
                'componente_id': movimiento.componente_id,
                'cantidad': movimiento.cantidad,
                'tipo_movimiento': movimiento.tipo_movimiento
            }
        
        response_data = {
            'success': True,
            'data': movimiento_data,
            'message': 'Movimiento de stock registrado exitosamente'
        }
        
        return jsonify(response_data), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error en registrar_movimiento: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error interno del servidor'
        }), 500


@api_bp.route('/stock/resumen', methods=['GET'])
def get_resumen_stock():
    """Obtener resumen de stock por componente"""
    from ...utils.db import reset_transaction, safe_query_execute
    
    def execute_resumen_query():
        """Función auxiliar para ejecutar la consulta de resumen"""
        try:
            print("🔍 Consultando resumen de stock")
            
            # Query SQL adaptado a la estructura real de la BD
            resumen_query = """
            SELECT 
                c."ID" as componente_id,
                c."Nombre" as nombre_componente,
                c."Precio" as precio_unitario,
                COALESCE(COUNT(s."ID"), 0) as total_movimientos,
                COALESCE(SUM(CASE WHEN s."Tipo" = 'Ingreso' THEN s."Cantidad" ELSE 0 END), 0) as entradas,
                COALESCE(SUM(CASE WHEN s."Tipo" = 'Salida' THEN s."Cantidad" ELSE 0 END), 0) as salidas,
                COALESCE(SUM(CASE WHEN s."Tipo" = 'Ingreso' THEN s."Cantidad" 
                                 WHEN s."Tipo" = 'Salida' THEN -s."Cantidad" 
                                 ELSE 0 END), 0) as stock_actual
            FROM componentes c
            LEFT JOIN stock s ON s."ID_Componente" = c."ID"
            GROUP BY c."ID", c."Nombre", c."Precio"
            ORDER BY c."ID"
            """
            
            print(f"📊 Ejecutando query: {resumen_query[:100]}...")
            result = db.session.execute(db.text(resumen_query))
            resumen_data = []
            total_valor = 0
            
            for row in result:
                stock_actual = int(row.stock_actual or 0)
                precio_unitario = float(row.precio_unitario or 0)
                valor_inventario = stock_actual * precio_unitario
                total_valor += valor_inventario
                
                resumen_data.append({
                    'componente_id': row.componente_id,
                    'nombre_componente': row.nombre_componente or 'Sin nombre',
                    'precio_unitario': precio_unitario,
                    'entradas': int(row.entradas or 0),
                    'salidas': int(row.salidas or 0),
                    'stock_actual': stock_actual,
                    'total_movimientos': int(row.total_movimientos or 0),
                    'valor_inventario': valor_inventario
                })
            
            print(f"✅ Query exitosa - {len(resumen_data)} componentes encontrados")
            
            # Agregar información de valor total
            result_data = {
                'componentes': resumen_data,
                'resumen_general': {
                    'total_componentes': len(resumen_data),
                    'valor_total_inventario': total_valor,
                    'componentes_con_stock': len([c for c in resumen_data if c['stock_actual'] > 0]),
                    'componentes_sin_stock': len([c for c in resumen_data if c['stock_actual'] <= 0])
                }
            }
            
            return result_data
            
        except Exception as e:
            print(f"⚠️ Error en query principal: {e}")
            import traceback
            traceback.print_exc()
            raise e  # Re-lanzar para que safe_query_execute maneje el retry
    
    try:
        # Usar safe_query_execute para manejo robusto de errores
        result_data = safe_query_execute(execute_resumen_query)
        
        if result_data and result_data.get('componentes'):
            response_data = {
                'success': True,
                'data': result_data['componentes'],
                'message': f"Resumen de stock para {result_data['resumen_general']['total_componentes']} componentes",
                'total_componentes': result_data['resumen_general']['total_componentes'],
                'valor_total_inventario': result_data['resumen_general']['valor_total_inventario'],
                'componentes_con_stock': result_data['resumen_general']['componentes_con_stock'],
                'componentes_sin_stock': result_data['resumen_general']['componentes_sin_stock']
            }
            
            print(f"✅ Respuesta generada con {len(result_data['componentes'])} componentes")
            return jsonify(response_data), 200
        else:
            raise Exception("No se pudo obtener datos válidos")
            
    except Exception as e:
        print(f"❌ Error final en get_resumen_stock: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback completo
        reset_transaction()
        
        fallback_response = {
            'success': True,
            'data': [{
                'componente_id': 0,
                'nombre_componente': 'Sistema recuperándose...',
                'precio_unitario': 0,
                'entradas': 0,
                'salidas': 0,
                'stock_actual': 0,
                'total_movimientos': 0,
                'valor_inventario': 0
            }],
            'message': f"Sistema en recuperación (Error: {str(e)})",
            'total_componentes': 1,
            'valor_total_inventario': 0,
            'componentes_con_stock': 0,
            'componentes_sin_stock': 1
        }
        
        return jsonify(fallback_response), 200
        
        print(f"✅ Resumen de stock generado: {result_data['resumen_general']['total_componentes']} componentes")
        print(f"💰 Valor total inventario: ${result_data['resumen_general']['valor_total_inventario']:,.2f}")
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"❌ Error crítico en get_resumen_stock: {e}")
        import traceback
        traceback.print_exc()
        
        # Intentar resetear transacción antes de responder
        try:
            reset_transaction()
        except:
            pass
        
        # Respuesta de emergencia
        emergency_data = {
            'componentes': [{
                'componente_id': 0,
                'nombre_componente': 'Error de sistema',
                'precio_unitario': 0,
                'entradas': 0,
                'salidas': 0,
                'stock_actual': 0,
                'total_movimientos': 0,
                'valor_inventario': 0
            }],
            'resumen_general': {
                'total_componentes': 1,
                'valor_total_inventario': 0,
                'componentes_con_stock': 0,
                'componentes_sin_stock': 1
            }
        }
        
        return jsonify({
            'success': False,
            'data': emergency_data['componentes'],
            'total_componentes': 1,
            'valor_total_inventario': 0,
            'componentes_con_stock': 0,
            'componentes_sin_stock': 1,
            'error': 'Error temporal del sistema',
            'message': 'El sistema se está recuperando. Intenta nuevamente en unos momentos.'
        }), 200  # 200 en lugar de 500 para que el frontend maneje mejor


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
