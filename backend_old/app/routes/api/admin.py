from flask import request, jsonify
from . import api_bp
from ...utils.db import db
from ...models import Componente

@api_bp.route('/admin/db/info', methods=['GET'])
def get_db_info():
    """Información de la base de datos"""
    try:
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        db_info = {
            'engine': str(db.engine.url),
            'tables': []
        }
        
        for table_name in tables:
            columns = inspector.get_columns(table_name)
            table_info = {
                'name': table_name,
                'columns': [
                    {
                        'name': col['name'],
                        'type': str(col['type']),
                        'nullable': col['nullable'],
                        'default': col.get('default')
                    } for col in columns
                ]
            }
            
            # Contar registros
            try:
                if table_name == 'componentes':
                    count = Componente.query.count()
                    table_info['row_count'] = count
            except:
                table_info['row_count'] = 'N/A'
                
            db_info['tables'].append(table_info)
        
        return jsonify({
            'success': True,
            'data': db_info
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/admin/db/query', methods=['POST'])
def execute_query():
    """Ejecutar query SQL (solo para desarrollo)"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query requerido'
            }), 400
        
        # Solo permitir SELECT para seguridad
        if not query.upper().startswith('SELECT'):
            return jsonify({
                'success': False,
                'error': 'Solo se permiten consultas SELECT'
            }), 400
        
        result = db.session.execute(db.text(query))
        
        # Convertir resultado a lista de diccionarios
        rows = []
        if result.returns_rows:
            columns = result.keys()
            for row in result:
                rows.append(dict(zip(columns, row)))
        
        return jsonify({
            'success': True,
            'data': rows,
            'columns': list(result.keys()) if result.returns_rows else []
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500