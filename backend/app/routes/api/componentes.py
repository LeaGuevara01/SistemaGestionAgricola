from flask import request, jsonify
from werkzeug.exceptions import BadRequest
from werkzeug.utils import secure_filename
import os
from flask import current_app
from app.routes.api import api_bp
from app.models.componente import Componente
from app.utils.db import db

@api_bp.route('/componentes', methods=['GET'])
def get_componentes():
    try:
        print("🚀 GET /api/v1/componentes llamado")
        
        # Parámetros de filtrado
        categoria = request.args.get('categoria')
        search = request.args.get('search', '').strip()
        
        print(f"📋 Parámetros: categoria={categoria}, search='{search}'")
        
        # ✅ QUERY SIMPLE SIN FILTRO 'activo'
        query = Componente.query
        
        # ✅ FILTRAR POR TIPO SI SE PROPORCIONA CATEGORIA
        if categoria and categoria.strip():
            query = query.filter(Componente.tipo == categoria)
        
        if search:
            query = query.filter(
                db.or_(
                    Componente.nombre.ilike(f'%{search}%'),
                    Componente.descripcion.ilike(f'%{search}%')
                )
            )
        
        componentes = query.order_by(Componente.nombre).limit(50).all()
        
        print(f"📊 Encontrados {len(componentes)} componentes")
        
        result = {
            'success': True,
            'data': [comp.to_dict() for comp in componentes],
            'total': len(componentes)
        }
        
        print(f"✅ Enviando respuesta: {len(result['data'])} items")
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Error en get_componentes: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/componentes/test', methods=['GET'])
def test_componentes():
    """Endpoint de prueba simple"""
    try:
        # Query muy simple
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
                'message': 'Conexión OK pero no hay datos en modelos SQLAlchemy',
                'total': 0,
                'note': 'Pero flask show-data componentes sí mostró datos'
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error de conexión: {str(e)}'
        }), 500

@api_bp.route('/debug/sql')
def debug_sql():
    """Verificar SQL directo vs SQLAlchemy"""
    try:
        # 1. Query SQL directo
        result = db.session.execute(db.text('SELECT * FROM componentes LIMIT 3'))
        sql_data = [dict(row._mapping) for row in result]
        
        # 2. Query SQLAlchemy
        componentes = Componente.query.limit(3).all()
        sqlalchemy_data = [comp.to_dict() for comp in componentes]
        
        # 3. Info de la tabla
        inspector = db.inspect(db.engine)
        table_info = inspector.get_columns('componentes')
        pk_constraint = inspector.get_pk_constraint('componentes')
        
        return jsonify({
            'sql_direct': {
                'count': len(sql_data),
                'data': sql_data
            },
            'sqlalchemy': {
                'count': len(sqlalchemy_data),
                'data': sqlalchemy_data
            },
            'table_info': {
                'columns': [col['name'] for col in table_info],
                'primary_key': pk_constraint
            }
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        })

@api_bp.route('/componentes/<int:id>', methods=['GET'])
def get_componente(id):
    """Obtener un componente específico"""
    try:
        componente = Componente.query.get_or_404(id)
        
        result = {
            'success': True,
            'data': componente.to_dict()
        }
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Error en get_componente: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/componentes', methods=['POST'])
def create_componente():
    """Crear un nuevo componente"""
    try:
        data = request.get_json()
        
        componente = Componente(
            nombre=data.get('nombre'),
            descripcion=data.get('descripcion'),
            numero_parte=data.get('numero_parte'),
            tipo=data.get('tipo'),
            precio_unitario=data.get('precio_unitario', 0),
            stock_actual=data.get('stock_actual', 0),
            stock_minimo=data.get('stock_minimo', 0)
        )
        
        db.session.add(componente)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': componente.to_dict(),
            'message': 'Componente creado exitosamente'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error en create_componente: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/componentes/<int:id>', methods=['PUT'])
def update_componente(id):
    """Actualizar un componente"""
    try:
        componente = Componente.query.get_or_404(id)
        data = request.get_json()
        
        # Actualizar campos
        if 'nombre' in data:
            componente.nombre = data['nombre']
        if 'descripcion' in data:
            componente.descripcion = data['descripcion']
        if 'numero_parte' in data:
            componente.numero_parte = data['numero_parte']
        if 'tipo' in data:
            componente.tipo = data['tipo']
        if 'precio_unitario' in data:
            componente.precio_unitario = data['precio_unitario']
        if 'stock_actual' in data:
            componente.stock_actual = data['stock_actual']
        if 'stock_minimo' in data:
            componente.stock_minimo = data['stock_minimo']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': componente.to_dict(),
            'message': 'Componente actualizado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error en update_componente: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/componentes/<int:id>/eliminar', methods=['POST'])
def eliminar_componente(id):
    """Eliminar un componente"""
    try:
        print(f"🗑️ Eliminando componente ID: {id}")
        
        componente = Componente.query.get_or_404(id)
        
        # Verificar si el componente está siendo usado en otras tablas
        # (puedes agregar más validaciones aquí)
        
        db.session.delete(componente)
        db.session.commit()
        
        print(f"✅ Componente {id} eliminado exitosamente")
        
        return jsonify({
            'success': True,
            'message': f'Componente {componente.nombre} eliminado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error en eliminar_componente: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/componentes/categorias', methods=['GET'])
def get_categorias():
    """Obtener lista de categorías de componentes"""
    try:
        # Obtener categorías únicas de la base de datos
        categorias = db.session.query(Componente.tipo).distinct().filter(Componente.tipo.isnot(None)).all()
        categorias_list = [cat[0] for cat in categorias if cat[0]]
        
        return jsonify({
            'success': True,
            'data': sorted(categorias_list)
        })
        
    except Exception as e:
        print(f"❌ Error en get_categorias: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/componentes/<int:id>/upload-photo', methods=['POST'])
def upload_photo(id):
    """Subir foto de componente"""
    try:
        print(f"📸 Subiendo foto para componente ID: {id}")
        
        componente = Componente.query.get_or_404(id)
        
        if 'photo' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No se encontró archivo en la petición'
            }), 400
        
        file = request.files['photo']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No se seleccionó archivo'
            }), 400
        
        if file:
            # Generar nombre seguro
            filename = secure_filename(f"componente_{id}.{file.filename.rsplit('.', 1)[1].lower()}")
            
            # Crear directorio si no existe
            upload_folder = os.path.join(current_app.root_path, '..', 'static', 'fotos')
            os.makedirs(upload_folder, exist_ok=True)
            
            # Guardar archivo
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            
            # Actualizar componente
            componente.foto = filename
            db.session.commit()
            
            print(f"✅ Foto guardada: {filename}")
            
            return jsonify({
                'success': True,
                'message': 'Foto subida exitosamente',
                'data': {
                    'foto': filename,
                    'componente': componente.to_dict()
                }
            })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error en upload_photo: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500