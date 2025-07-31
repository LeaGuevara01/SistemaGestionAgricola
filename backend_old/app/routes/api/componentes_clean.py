from flask import request, jsonify
from werkzeug.utils import secure_filename
import os
from . import api_bp
from ...models.componente import Componente
from ...utils.db import db


@api_bp.route('/componentes', methods=['GET'])
def get_componentes():
    """Obtener lista de componentes con filtros y paginación"""
    try:
        # Parámetros de filtrado
        search = request.args.get('q', '').strip()
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        sort_by = request.args.get('sort_by', 'Nombre')
        sort_order = request.args.get('sort_order', 'asc')
        
        print(f"🔍 Búsqueda de componentes: q='{search}', page={page}, per_page={per_page}")
        
        # Query base
        query = Componente.query
        
        # Filtrar por búsqueda si se proporciona
        if search:
            search_term = f"%{search}%"
            try:
                query = query.filter(
                    db.or_(
                        Componente.Nombre.ilike(search_term),
                        getattr(Componente, 'Descripcion', Componente.Nombre).ilike(search_term)
                    )
                )
            except Exception as e:
                print(f"⚠️ Error en filtro, usando nombre: {e}")
                query = query.filter(Componente.Nombre.ilike(search_term))
        
        # Ordenamiento básico
        try:
            if hasattr(Componente, sort_by):
                column = getattr(Componente, sort_by)
                if sort_order == 'desc':
                    query = query.order_by(column.desc())
                else:
                    query = query.order_by(column.asc())
            else:
                query = query.order_by(Componente.Nombre.asc())
        except Exception:
            query = query.order_by(Componente.id.asc())
        
        # Paginación simple
        try:
            total = query.count()
            offset = (page - 1) * per_page
            componentes = query.offset(offset).limit(per_page).all()
            
            has_next = offset + per_page < total
            has_prev = page > 1
            pages = (total + per_page - 1) // per_page
            
        except Exception as e:
            print(f"❌ Error en paginación: {e}")
            # Fallback sin paginación
            componentes = query.limit(50).all()
            total = len(componentes)
            has_next = False
            has_prev = False
            pages = 1
            page = 1
            per_page = total
        
        # Convertir a diccionarios
        componentes_data = []
        for comp in componentes:
            try:
                componentes_data.append(comp.to_dict())
            except Exception as e:
                print(f"⚠️ Error serializando componente {comp.id}: {e}")
                # Fallback manual
                componentes_data.append({
                    'id': comp.id,
                    'nombre': getattr(comp, 'Nombre', 'Sin nombre'),
                    'precio': getattr(comp, 'precio_unitario', 0)
                })
        
        response_data = {
            'success': True,
            'data': {
                'componentes': componentes_data,
                'pagination': {
                    'page': page,
                    'pages': pages,
                    'per_page': per_page,
                    'total': total,
                    'has_next': has_next,
                    'has_prev': has_prev
                }
            },
            'message': f"Se encontraron {total} componentes"
        }
        
        print(f"✅ Respuesta exitosa: {total} componentes encontrados")
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"❌ Error en get_componentes: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error interno del servidor'
        }), 500


@api_bp.route('/componentes/<int:id>', methods=['GET'])
def get_componente(id):
    """Obtener un componente específico por ID"""
    try:
        print(f"🔍 Buscando componente con ID: {id}")
        
        componente = Componente.query.get(id)
        
        if not componente:
            return jsonify({
                'success': False,
                'error': f'Componente con ID {id} no encontrado',
                'message': 'Componente no encontrado'
            }), 404
        
        # Convertir a diccionario
        try:
            componente_data = componente.to_dict()
        except Exception as e:
            print(f"⚠️ Error serializando componente: {e}")
            # Fallback manual
            componente_data = {
                'id': componente.id,
                'nombre': getattr(componente, 'Nombre', 'Sin nombre'),
                'precio': getattr(componente, 'precio_unitario', 0)
            }
        
        response_data = {
            'success': True,
            'data': componente_data,
            'message': 'Componente encontrado'
        }
        
        print(f"✅ Componente encontrado: {componente_data.get('nombre', 'N/A')}")
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"❌ Error en get_componente: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error interno del servidor'
        }), 500


@api_bp.route('/componentes', methods=['POST'])
def create_componente():
    """Crear un nuevo componente"""
    try:
        data = request.get_json() or {}
        print(f"📝 Creando componente con datos: {data}")
        
        # Validar datos básicos
        if not data.get('nombre'):
            return jsonify({
                'success': False,
                'error': 'El nombre del componente es obligatorio',
                'message': 'Datos inválidos'
            }), 400
        
        # Verificar si ya existe
        existing = None
        try:
            existing = Componente.query.filter_by(Nombre=data.get('nombre')).first()
        except Exception:
            try:
                existing = Componente.query.filter_by(nombre=data.get('nombre')).first()
            except Exception as e:
                print(f"⚠️ Error verificando duplicados: {e}")
        
        if existing:
            return jsonify({
                'success': False,
                'error': f'Ya existe un componente con el nombre "{data.get("nombre")}"',
                'message': 'Componente duplicado'
            }), 409
        
        # Crear componente con mapeo flexible
        try:
            componente_data = {}
            
            # Mapear campos básicos
            if hasattr(Componente, 'Nombre'):
                componente_data['Nombre'] = data.get('nombre')
            else:
                componente_data['nombre'] = data.get('nombre')
            
            if hasattr(Componente, 'precio_unitario'):
                componente_data['precio_unitario'] = data.get('precio_unitario', 0)
            elif hasattr(Componente, 'precio'):
                componente_data['precio'] = data.get('precio_unitario', 0)
            
            # Campos opcionales
            if data.get('descripcion') and hasattr(Componente, 'Descripcion'):
                componente_data['Descripcion'] = data.get('descripcion')
            if data.get('numero_parte') and hasattr(Componente, 'ID_Componente'):
                componente_data['ID_Componente'] = data.get('numero_parte')
            if data.get('categoria') and hasattr(Componente, 'Tipo'):
                componente_data['Tipo'] = data.get('categoria')
            if data.get('fabricante') and hasattr(Componente, 'Marca'):
                componente_data['Marca'] = data.get('fabricante')
            if data.get('modelo') and hasattr(Componente, 'Modelo'):
                componente_data['Modelo'] = data.get('modelo')
            
            componente = Componente(**componente_data)
            
        except Exception as e:
            print(f"⚠️ Error creando objeto Componente: {e}")
            # Fallback básico
            componente = Componente()
            componente.Nombre = data.get('nombre')
            if hasattr(componente, 'precio_unitario'):
                componente.precio_unitario = data.get('precio_unitario', 0)
        
        # Guardar en base de datos
        try:
            db.session.add(componente)
            db.session.commit()
            print(f"✅ Componente creado con ID: {componente.id}")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error guardando en BD: {e}")
            return jsonify({
                'success': False,
                'error': 'Error al guardar en la base de datos',
                'message': 'Error de base de datos'
            }), 500
        
        # Respuesta
        try:
            componente_data = componente.to_dict()
        except Exception:
            componente_data = {
                'id': componente.id,
                'nombre': getattr(componente, 'Nombre', data.get('nombre')),
                'precio': getattr(componente, 'precio_unitario', 0)
            }
        
        response_data = {
            'success': True,
            'data': componente_data,
            'message': 'Componente creado exitosamente'
        }
        
        return jsonify(response_data), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error en create_componente: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error interno del servidor'
        }), 500


@api_bp.route('/componentes/<int:id>', methods=['PUT'])
def update_componente(id):
    """Actualizar un componente existente"""
    try:
        data = request.get_json() or {}
        print(f"📝 Actualizando componente {id} con datos: {data}")
        
        componente = Componente.query.get(id)
        if not componente:
            return jsonify({
                'success': False,
                'error': f'Componente con ID {id} no encontrado',
                'message': 'Componente no encontrado'
            }), 404
        
        # Actualizar campos
        if data.get('nombre'):
            if hasattr(componente, 'Nombre'):
                componente.Nombre = data.get('nombre')
            else:
                componente.nombre = data.get('nombre')
        
        if 'precio_unitario' in data:
            if hasattr(componente, 'precio_unitario'):
                componente.precio_unitario = data.get('precio_unitario', 0)
            elif hasattr(componente, 'precio'):
                componente.precio = data.get('precio_unitario', 0)
        
        # Campos opcionales
        if data.get('descripcion') and hasattr(componente, 'Descripcion'):
            componente.Descripcion = data.get('descripcion')
        if data.get('categoria') and hasattr(componente, 'Tipo'):
            componente.Tipo = data.get('categoria')
        if data.get('fabricante') and hasattr(componente, 'Marca'):
            componente.Marca = data.get('fabricante')
        if data.get('modelo') and hasattr(componente, 'Modelo'):
            componente.Modelo = data.get('modelo')
        
        db.session.commit()
        
        try:
            componente_data = componente.to_dict()
        except Exception:
            componente_data = {
                'id': componente.id,
                'nombre': getattr(componente, 'Nombre', 'Sin nombre'),
                'precio': getattr(componente, 'precio_unitario', 0)
            }
        
        return jsonify({
            'success': True,
            'data': componente_data,
            'message': 'Componente actualizado exitosamente'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error en update_componente: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error interno del servidor'
        }), 500


@api_bp.route('/componentes/<int:id>', methods=['DELETE'])
def delete_componente(id):
    """Eliminar un componente"""
    try:
        componente = Componente.query.get(id)
        if not componente:
            return jsonify({
                'success': False,
                'error': f'Componente con ID {id} no encontrado',
                'message': 'Componente no encontrado'
            }), 404
        
        nombre = getattr(componente, 'Nombre', f'ID {id}')
        
        db.session.delete(componente)
        db.session.commit()
        
        print(f"✅ Componente eliminado: {nombre}")
        
        return jsonify({
            'success': True,
            'message': f'Componente "{nombre}" eliminado exitosamente'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error en delete_componente: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error interno del servidor'
        }), 500


@api_bp.route('/componentes/test', methods=['GET'])
def test_componentes():
    """Endpoint de prueba simple"""
    try:
        total = Componente.query.count()
        
        if total > 0:
            primer_componente = Componente.query.first()
            return jsonify({
                'success': True,
                'message': f'Conexión OK. {total} componentes encontrados',
                'sample': primer_componente.to_dict()
            })
        else:
            return jsonify({
                'success': True,
                'message': 'Conexión OK pero no hay componentes',
                'total': 0
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error de conexión: {str(e)}'
        }), 500


@api_bp.route('/componentes/categorias', methods=['GET'])
def get_categorias():
    """Obtener lista de categorías de componentes"""
    try:
        # Obtener categorías únicas si el campo existe
        if hasattr(Componente, 'Tipo'):
            categorias = db.session.query(Componente.Tipo).distinct().filter(
                Componente.Tipo.isnot(None),
                Componente.Tipo != ''
            ).all()
            categorias_list = [cat[0] for cat in categorias if cat[0]]
        else:
            categorias_list = []
        
        return jsonify({
            'success': True,
            'data': sorted(categorias_list),
            'message': f'Se encontraron {len(categorias_list)} categorías'
        })
        
    except Exception as e:
        print(f"❌ Error obteniendo categorías: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error interno del servidor'
        }), 500
