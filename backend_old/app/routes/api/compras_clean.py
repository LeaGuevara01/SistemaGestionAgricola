from flask import request, jsonify
from datetime import datetime
from . import api_bp
from ...models import Compra, Componente, Maquina, Proveedor
from ...utils.db import db


@api_bp.route('/compras', methods=['GET'])
def get_compras():
    """Obtener lista de compras con filtros"""
    try:
        # Parámetros de filtrado
        proveedor_id = request.args.get('proveedor_id')
        componente_id = request.args.get('componente_id') 
        maquina_id = request.args.get('maquina_id')
        estado = request.args.get('estado')
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)
        
        print(f"🔍 Consultando compras con filtros: proveedor={proveedor_id}, componente={componente_id}")
        
        # Query base
        query = Compra.query
        
        # Aplicar filtros
        if proveedor_id:
            query = query.filter(Compra.proveedor_id == proveedor_id)
        if componente_id:
            query = query.filter(Compra.componente_id == componente_id)
        if maquina_id:
            query = query.filter(Compra.maquina_id == maquina_id)
        if estado:
            query = query.filter(Compra.estado == estado)
        
        # Filtros de fecha
        if fecha_desde:
            try:
                fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                if hasattr(Compra, 'fecha_compra'):
                    query = query.filter(Compra.fecha_compra >= fecha_desde_obj)
                elif hasattr(Compra, 'fecha'):
                    query = query.filter(Compra.fecha >= fecha_desde_obj)
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Formato de fecha inválido para fecha_desde (usar YYYY-MM-DD)',
                    'message': 'Formato de fecha inválido'
                }), 400
        
        if fecha_hasta:
            try:
                fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                if hasattr(Compra, 'fecha_compra'):
                    query = query.filter(Compra.fecha_compra <= fecha_hasta_obj)
                elif hasattr(Compra, 'fecha'):
                    query = query.filter(Compra.fecha <= fecha_hasta_obj)
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Formato de fecha inválido para fecha_hasta (usar YYYY-MM-DD)',
                    'message': 'Formato de fecha inválido'
                }), 400
        
        # Ordenamiento
        try:
            if hasattr(Compra, 'fecha_compra'):
                query = query.order_by(Compra.fecha_compra.desc())
            elif hasattr(Compra, 'fecha'):
                query = query.order_by(Compra.fecha.desc())
            else:
                query = query.order_by(Compra.id.desc())
        except Exception:
            query = query.order_by(Compra.id.desc())
        
        # Paginación
        try:
            total = query.count()
            offset = (page - 1) * per_page
            compras = query.offset(offset).limit(per_page).all()
            
            has_next = offset + per_page < total
            has_prev = page > 1
            pages = (total + per_page - 1) // per_page
            
        except Exception as e:
            print(f"❌ Error en paginación de compras: {e}")
            compras = query.limit(50).all()
            total = len(compras)
            has_next = False
            has_prev = False
            pages = 1
            page = 1
            per_page = total
        
        # Convertir a diccionarios con información relacionada
        compras_data = []
        for compra in compras:
            try:
                compra_dict = compra.to_dict()
                
                # Agregar información de relaciones
                try:
                    # Componente
                    if hasattr(compra, 'componente_id') and compra.componente_id:
                        componente = Componente.query.get(compra.componente_id)
                        if componente:
                            compra_dict['componente'] = {
                                'id': componente.id,
                                'nombre': getattr(componente, 'Nombre', 'Sin nombre')
                            }
                    
                    # Proveedor
                    if hasattr(compra, 'proveedor_id') and compra.proveedor_id:
                        proveedor = Proveedor.query.get(compra.proveedor_id)
                        if proveedor:
                            compra_dict['proveedor'] = {
                                'id': proveedor.id,
                                'nombre': getattr(proveedor, 'Nombre', 'Sin nombre')
                            }
                    
                    # Máquina
                    if hasattr(compra, 'maquina_id') and compra.maquina_id:
                        maquina = Maquina.query.get(compra.maquina_id)
                        if maquina:
                            compra_dict['maquina'] = {
                                'id': maquina.id,
                                'nombre': getattr(maquina, 'Nombre', 'Sin nombre')
                            }
                            
                except Exception as e:
                    print(f"⚠️ Error obteniendo relaciones para compra {compra.id}: {e}")
                
                compras_data.append(compra_dict)
                
            except Exception as e:
                print(f"⚠️ Error serializando compra {compra.id}: {e}")
                # Fallback manual
                compras_data.append({
                    'id': compra.id,
                    'proveedor_id': getattr(compra, 'proveedor_id', None),
                    'componente_id': getattr(compra, 'componente_id', None),
                    'cantidad': getattr(compra, 'cantidad', 0),
                    'precio': getattr(compra, 'precio_total', 0)
                })
        
        response_data = {
            'success': True,
            'data': {
                'compras': compras_data,
                'pagination': {
                    'page': page,
                    'pages': pages,
                    'per_page': per_page,
                    'total': total,
                    'has_next': has_next,
                    'has_prev': has_prev
                }
            },
            'message': f"Se encontraron {total} compras"
        }
        
        print(f"✅ Compras consultadas: {total} encontradas")
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"❌ Error en get_compras: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error interno del servidor'
        }), 500


@api_bp.route('/compras/<int:id>', methods=['GET'])
def get_compra(id):
    """Obtener una compra específica"""
    try:
        print(f"🔍 Buscando compra con ID: {id}")
        
        compra = Compra.query.get(id)
        
        if not compra:
            return jsonify({
                'success': False,
                'error': f'Compra con ID {id} no encontrada',
                'message': 'Compra no encontrada'
            }), 404
        
        # Convertir a diccionario con relaciones
        try:
            compra_data = compra.to_dict()
            
            # Agregar información de relaciones
            if hasattr(compra, 'componente_id') and compra.componente_id:
                componente = Componente.query.get(compra.componente_id)
                if componente:
                    compra_data['componente'] = componente.to_dict()
            
            if hasattr(compra, 'proveedor_id') and compra.proveedor_id:
                proveedor = Proveedor.query.get(compra.proveedor_id)
                if proveedor:
                    compra_data['proveedor'] = proveedor.to_dict()
            
            if hasattr(compra, 'maquina_id') and compra.maquina_id:
                maquina = Maquina.query.get(compra.maquina_id)
                if maquina:
                    compra_data['maquina'] = maquina.to_dict()
                    
        except Exception as e:
            print(f"⚠️ Error serializando compra: {e}")
            # Fallback manual
            compra_data = {
                'id': compra.id,
                'proveedor_id': getattr(compra, 'proveedor_id', None),
                'componente_id': getattr(compra, 'componente_id', None),
                'cantidad': getattr(compra, 'cantidad', 0),
                'precio': getattr(compra, 'precio_total', 0)
            }
        
        response_data = {
            'success': True,
            'data': compra_data,
            'message': 'Compra encontrada'
        }
        
        print(f"✅ Compra encontrada: ID {id}")
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"❌ Error en get_compra: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error interno del servidor'
        }), 500


@api_bp.route('/compras', methods=['POST'])
def create_compra():
    """Crear nueva compra"""
    try:
        data = request.get_json() or {}
        print(f"📝 Creando compra con datos: {data}")
        
        # Validaciones básicas
        required_fields = ['proveedor_id', 'cantidad', 'precio_unitario']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f"El campo '{field}' es requerido",
                    'message': 'Datos inválidos'
                }), 400
        
        # Verificar que el proveedor existe
        proveedor = Proveedor.query.get(data['proveedor_id'])
        if not proveedor:
            return jsonify({
                'success': False,
                'error': f"No se encontró el proveedor con ID {data['proveedor_id']}",
                'message': 'Proveedor no encontrado'
            }), 404
        
        # Verificar componente si se especifica
        if data.get('componente_id'):
            componente = Componente.query.get(data['componente_id'])
            if not componente:
                return jsonify({
                    'success': False,
                    'error': f"No se encontró el componente con ID {data['componente_id']}",
                    'message': 'Componente no encontrado'
                }), 404
        
        # Crear compra
        try:
            compra_data = {
                'proveedor_id': data['proveedor_id'],
                'cantidad': int(data['cantidad']),
                'precio_unitario': float(data['precio_unitario']),
                'precio_total': int(data['cantidad']) * float(data['precio_unitario'])
            }
            
            # Campos opcionales
            if data.get('componente_id'):
                compra_data['componente_id'] = data['componente_id']
            if data.get('maquina_id'):
                compra_data['maquina_id'] = data['maquina_id']
            if data.get('estado'):
                compra_data['estado'] = data['estado']
            if data.get('descripcion'):
                compra_data['descripcion'] = data['descripcion']
            if data.get('fecha_compra'):
                try:
                    compra_data['fecha_compra'] = datetime.strptime(data['fecha_compra'], '%Y-%m-%d').date()
                except ValueError:
                    compra_data['fecha_compra'] = datetime.now().date()
            else:
                compra_data['fecha_compra'] = datetime.now().date()
            
            compra = Compra(**compra_data)
            
        except Exception as e:
            print(f"⚠️ Error creando objeto Compra: {e}")
            return jsonify({
                'success': False,
                'error': 'Error en los datos de la compra',
                'message': 'Datos inválidos'
            }), 400
        
        # Guardar en base de datos
        try:
            db.session.add(compra)
            db.session.commit()
            print(f"✅ Compra creada con ID: {compra.id}")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error guardando compra: {e}")
            return jsonify({
                'success': False,
                'error': 'Error al guardar en la base de datos',
                'message': 'Error de base de datos'
            }), 500
        
        # Respuesta con información de relaciones
        try:
            compra_data = compra.to_dict()
            compra_data['proveedor'] = {
                'id': proveedor.id,
                'nombre': getattr(proveedor, 'Nombre', 'Sin nombre')
            }
            
            if data.get('componente_id'):
                componente = Componente.query.get(data['componente_id'])
                if componente:
                    compra_data['componente'] = {
                        'id': componente.id,
                        'nombre': getattr(componente, 'Nombre', 'Sin nombre')
                    }
        except Exception:
            compra_data = {
                'id': compra.id,
                'proveedor_id': compra.proveedor_id,
                'cantidad': compra.cantidad,
                'precio_total': compra.precio_total
            }
        
        response_data = {
            'success': True,
            'data': compra_data,
            'message': 'Compra creada exitosamente'
        }
        
        return jsonify(response_data), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error en create_compra: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error interno del servidor'
        }), 500


@api_bp.route('/compras/test', methods=['GET'])
def test_compras():
    """Endpoint de prueba para compras"""
    try:
        total_compras = Compra.query.count()
        total_proveedores = Proveedor.query.count()
        
        sample_data = {}
        if total_compras > 0:
            primera_compra = Compra.query.first()
            sample_data['sample_compra'] = primera_compra.to_dict()
        
        return jsonify({
            'success': True,
            'message': f'Compras API funcionando. {total_compras} compras, {total_proveedores} proveedores',
            'data': sample_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error en compras: {str(e)}'
        }), 500
