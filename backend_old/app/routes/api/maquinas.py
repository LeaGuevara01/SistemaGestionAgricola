from flask import request, jsonify
from werkzeug.exceptions import BadRequest
from . import api_bp
from ...models.maquina import Maquina
from ...utils.db import db, commit_or_rollback
from ...services.file_service import FileService

@api_bp.route('/maquinas', methods=['GET'])
def get_maquinas():
    try:
        search = request.args.get('search', '')
        tipo = request.args.get('tipo', '')
        estado = request.args.get('estado', '')
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        
        # Manejar filtro activo correctamente
        activo_param = request.args.get('activo')
        filter_activo = None
        if activo_param is not None:
            filter_activo = activo_param.lower() == 'true'
            print(f"   🔧 Filtro activo: param='{activo_param}', converted={filter_activo}, type={type(filter_activo)}")
        
        print(f"🔍 Consultando máquinas con filtros: search={search}, tipo={tipo}, estado={estado}, activo={filter_activo}")
        
        query = Maquina.query
        
        # Filtrar por activo si se especifica
        if filter_activo is not None:
            print(f"   🎯 Aplicando filtro: Maquina.activo == {filter_activo}")
            query = query.filter(Maquina.activo == filter_activo)
            
            # Debug: ver qué valores tienen las máquinas
            sample_maquinas = Maquina.query.limit(3).all()
            for m in sample_maquinas:
                print(f"   📋 Muestra máquina {m.id}: activo={m.activo}, type={type(m.activo)}")
                print(f"   ⚖️  Comparación: {m.activo} == {filter_activo} = {m.activo == filter_activo}")
        
        if search:
            query = query.filter(
                db.or_(
                    Maquina.nombre.ilike(f'%{search}%'),
                    Maquina.codigo.ilike(f'%{search}%'),
                    Maquina.marca.ilike(f'%{search}%'),
                    Maquina.modelo.ilike(f'%{search}%')
                )
            )
        
        if tipo:
            query = query.filter(Maquina.tipo.ilike(f'%{tipo}%'))
        
        if estado:
            query = query.filter(Maquina.estado.ilike(f'%{estado}%'))
        
        # Obtener total antes de la paginación
        total = query.count()
        
        # Aplicar paginación y ordenamiento
        maquinas = query.order_by(Maquina.nombre).offset((page - 1) * per_page).limit(per_page).all()
        
        print(f"📊 Total máquinas encontradas: {total}, Página: {page}/{((total - 1) // per_page) + 1 if total > 0 else 1}")
        
        return jsonify({
            'success': True,
            'data': [maquina.to_dict() for maquina in maquinas],
            'total': total,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': ((total - 1) // per_page) + 1 if total > 0 else 1
            },
            'message': f"Se encontraron {total} máquinas"
        })
        
    except Exception as e:
        # En caso de error, hacer rollback para limpiar la transacción
        db.session.rollback()
        print(f"❌ Error en get_maquinas: {e}")
        return jsonify({
            'success': False,
            'error': f'Error obteniendo máquinas: {str(e)}',
            'message': 'Error interno del servidor'
        }), 500

@api_bp.route('/maquinas', methods=['POST'])
def create_maquina():
    try:
        data = request.get_json()
        
        if not data.get('nombre'):
            raise BadRequest("El nombre es requerido")
        
        # Crear máquina con todos los campos disponibles
        maquina = Maquina(
            nombre=data.get('nombre'),
            codigo=data.get('codigo', f"M-{Maquina.query.count() + 1:03d}"),
            marca=data.get('marca'),
            modelo=data.get('modelo'),
            año=data.get('año'),
            estado=data.get('estado'),
            observaciones=data.get('observaciones'),
            tipo=data.get('tipo'),
            horas=data.get('horas_trabajo', 0),
            ubicacion=data.get('ubicacion'),
            activo=data.get('activo', True)
        )
        
        db.session.add(maquina)
        commit_or_rollback()
        
        return jsonify({
            'success': True,
            'data': maquina.to_dict(),
            'message': 'Máquina creada exitosamente'
        }), 201
        
    except BadRequest as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/maquinas/<int:id>', methods=['GET'])
def get_maquina(id):
    try:
        maquina = Maquina.query.get_or_404(id)
        include_relations = request.args.get('include_relations', 'false').lower() == 'true'
        
        return jsonify({
            'success': True,
            'data': maquina.to_dict(include_relations=include_relations)
        })
        
    except Exception as e:
        # En caso de error, hacer rollback para limpiar la transacción
        db.session.rollback()
        print(f"❌ Error en get_maquina: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/maquinas/<int:id>', methods=['PUT'])
def update_maquina(id):
    try:
        maquina = Maquina.query.get_or_404(id)
        data = request.get_json()
        
        print(f"🔧 Actualizando máquina ID: {id}")
        print(f"📝 Datos recibidos: {data}")
        
        # Mapeo directo de campos frontend a campos del modelo
        field_mapping = {
            'nombre': 'nombre',
            'codigo': 'codigo', 
            'marca': 'marca',
            'modelo': 'modelo',
            'año': 'año',
            'estado': 'estado',
            'observaciones': 'observaciones',
            'tipo': 'tipo',
            'horas_trabajo': 'horas',
            'ubicacion': 'ubicacion',
            'activo': 'activo'
        }
        
        updated_fields = []
        
        # Actualizar campos disponibles
        for frontend_field, model_field in field_mapping.items():
            if frontend_field in data:
                value = data[frontend_field]
                
                # Skip campos vacíos para evitar sobrescribir con valores vacíos
                if value == '' or value is None:
                    print(f"   ⚠️  Saltando campo vacío {frontend_field}")
                    continue
                
                print(f"   🔄 Actualizando {frontend_field} -> {model_field} = {value}")
                setattr(maquina, model_field, value)
                updated_fields.append(frontend_field)
        
        # Manejar campo que no existe en BD
        if 'numero_serie' in data and data['numero_serie']:
            print(f"   ⚠️  Ignorando campo numero_serie (no existe en BD): {data['numero_serie']}")
        
        commit_or_rollback()
        
        print(f"✅ Máquina {id} actualizada exitosamente")
        
        return jsonify({
            'success': True,
            'data': maquina.to_dict(),
            'message': 'Máquina actualizada exitosamente',
            'metadata': {
                'updated_fields': updated_fields,
                'ignored_fields': ['numero_serie'] if 'numero_serie' in data else []
            }
        })
        
    except BadRequest as e:
        print(f"❌ Error BadRequest: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        print(f"❌ Error en update_maquina: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/maquinas/<int:id>/upload-photo', methods=['POST'])
def upload_maquina_photo(id):
    """Subir foto de máquina"""
    try:
        print(f"📸 Subiendo foto para máquina ID: {id}")
        
        maquina = Maquina.query.get_or_404(id)
        
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
        
        # Verificar que el archivo tiene extensión válida
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        if '.' not in file.filename:
            return jsonify({
                'success': False,
                'error': 'Archivo sin extensión válida'
            }), 400
            
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        if file_extension not in allowed_extensions:
            return jsonify({
                'success': False,
                'error': f'Formato no permitido. Use: {", ".join(allowed_extensions)}'
            }), 400
        
        if file:
            # Importar las funciones necesarias
            from werkzeug.utils import secure_filename
            from flask import current_app
            import os
            
            # Generar nombre seguro
            filename = secure_filename(f"maquina_{id}.{file_extension}")
            
            # Crear directorio si no existe (guardar en raíz de fotos como el listado)
            upload_folder = os.path.join(current_app.root_path, '..', 'static', 'fotos')
            os.makedirs(upload_folder, exist_ok=True)
            
            # Guardar archivo
            filepath = os.path.join(upload_folder, filename)
            
            # Eliminar foto anterior si existe
            old_filename = maquina.foto
            if old_filename:
                old_filepath = os.path.join(upload_folder, old_filename)
                if os.path.exists(old_filepath):
                    try:
                        os.remove(old_filepath)
                        print(f"🗑️ Foto anterior eliminada: {old_filename}")
                    except Exception as e:
                        print(f"⚠️ No se pudo eliminar foto anterior: {e}")
            
            # Guardar nueva foto
            file.save(filepath)
            
            # Actualizar máquina con el nuevo nombre de foto
            maquina.foto = filename
            db.session.commit()
            
            print(f"✅ Foto guardada: {filename}")
            
            return jsonify({
                'success': True,
                'message': 'Foto subida exitosamente',
                'data': {
                    'foto': filename,
                    'maquina': maquina.to_dict()
                }
            })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error en upload_maquina_photo: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Las importaciones ya están al inicio del archivo
# No necesitamos importaciones duplicadas

# NUEVAS RUTAS PARA IMPORTACIÓN
@api_bp.route('/maquinas/import', methods=['POST'])
def import_maquinas():
    """Importar máquinas desde CSV"""
    try:
        if 'csvFile' not in request.files:
            raise BadRequest('No se proporcionó archivo CSV')
        
        file = request.files['csvFile']
        if file.filename == '':
            raise BadRequest('No se seleccionó archivo')
        
        # Usar el FileService existente
        try:
            filepath = FileService.save_import_file(file, 'imports/maquinas')
            if not filepath:
                raise BadRequest('Tipo de archivo no permitido. Solo CSV, XLS, XLSX')
        except ValueError as e:
            raise BadRequest(str(e))
        
        # Importar datos
        from ...services.import_service import ImportService
        result = ImportService.import_maquinas_from_csv(filepath)
        
        # Limpiar archivo temporal
        FileService.cleanup_temp_file(filepath)
        
        return jsonify({
            'success': True,
            'imported': result['imported'],
            'errors': result['errors'],
            'total': result['total']
        })
        
    except BadRequest as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error en la importación: {str(e)}'}), 500

@api_bp.route('/maquinas/import/template', methods=['GET'])
def get_maquinas_template():
    """Descargar plantilla CSV para máquinas"""
    try:
        from ...services.import_service import ImportService
        return ImportService.get_maquinas_template()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/maquinas/metadata', methods=['GET'])
def get_maquinas_metadata():
    """Obtener metadatos de campos para formularios dinámicos"""
    try:
        from ...services.field_metadata_service import FieldMetadataService
        metadata = FieldMetadataService.get_maquinas_metadata()
        
        return jsonify({
            'success': True,
            'data': metadata,
            'message': 'Metadatos obtenidos exitosamente'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/maquinas/stats', methods=['GET'])
def get_maquinas_stats():
    """Estadísticas de máquinas"""
    try:
        total = Maquina.query.count()
        activas = Maquina.query.filter(Maquina.activo == True).count()
        inactivas = total - activas
        
        # Estadísticas por estado
        operativo = Maquina.query.filter(Maquina.estado == 'operativo').count()
        operativa = Maquina.query.filter(Maquina.estado == 'Operativa').count()
        mantenimiento = Maquina.query.filter(Maquina.estado == 'mantenimiento').count()
        fuera_servicio = Maquina.query.filter(Maquina.estado == 'fuera_servicio').count()
        
        # Estadísticas por tipo
        tipos_query = db.session.query(
            Maquina.tipo, 
            db.func.count(Maquina.id)
        ).filter(Maquina.tipo.isnot(None)).group_by(Maquina.tipo)
        
        tipos = tipos_query.all()
        
        return jsonify({
            'success': True,
            'data': {
                'total': total,
                'activas': activas,
                'inactivas': inactivas,
                'operativo': operativo + operativa,  # Combinar variaciones
                'mantenimiento': mantenimiento,
                'fuera_servicio': fuera_servicio,
                'por_tipo': [{'tipo': tipo[0] or 'Sin tipo', 'cantidad': tipo[1]} for tipo in tipos]
            }
        })
    except Exception as e:
        # En caso de error, hacer rollback para limpiar la transacción
        db.session.rollback()
        print(f"❌ Error en get_maquinas_stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500