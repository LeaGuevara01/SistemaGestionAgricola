from app.utils.db import db
from sqlalchemy import Table, Column, Integer, String, Float, DateTime, Boolean

def setup_hybrid_models():
    """Configurar modelos híbridos usando inspector directo"""
    from sqlalchemy import inspect
    from app.models.componente import Componente
    from app.models.proveedor import Proveedor
    from app.models.maquina import Maquina
    from app.models.compra import Compra
    from app.models.stock import Stock
    
    inspector = inspect(db.engine)
    
    hybrid_models = [
        (Componente, 'componentes'),
        (Proveedor, 'proveedores'),
        (Maquina, 'maquinas'),
        (Compra, 'compras'),
        (Stock, 'stock')
    ]
    
    results = []
    
    for model_class, table_name in hybrid_models:
        try:
            # ✅ USAR INSPECTOR DIRECTAMENTE
            columns_info = inspector.get_columns(table_name)
            pk_constraint = inspector.get_pk_constraint(table_name)
            
            print(f"🔍 {model_class.__name__}: {len(columns_info)} columnas encontradas")
            print(f"   Columnas: {[col['name'] for col in columns_info]}")
            print(f"   Primary Key: {pk_constraint.get('constrained_columns', [])}")
            
            # ✅ RECREAR TABLA CON TODAS LAS COLUMNAS
            columns = []
            for col_info in columns_info:
                col_name = col_info['name']
                col_type = col_info['type']
                nullable = col_info['nullable']
                
                # Mapear tipos correctamente
                if 'INTEGER' in str(col_type).upper():
                    sqlalchemy_type = Integer
                elif 'DOUBLE' in str(col_type).upper() or 'FLOAT' in str(col_type).upper():
                    sqlalchemy_type = Float
                elif 'BOOLEAN' in str(col_type).upper():
                    sqlalchemy_type = Boolean
                elif 'DATE' in str(col_type).upper():
                    sqlalchemy_type = DateTime
                else:
                    sqlalchemy_type = String(255)
                
                # Determinar si es primary key
                is_primary = col_name in pk_constraint.get('constrained_columns', [])
                
                column = Column(col_name, sqlalchemy_type, primary_key=is_primary, nullable=nullable)
                columns.append(column)
            
            # ✅ CREAR NUEVA TABLA Y REEMPLAZAR LA EXISTENTE
            new_table = Table(table_name, db.metadata, *columns, extend_existing=True)
            
            # ✅ REEMPLAZAR LA TABLA DEL MODELO
            model_class.__table__ = new_table
            
            # ✅ TAMBIÉN AGREGAR COLUMNAS COMO ATRIBUTOS
            added_attrs = []
            for col in new_table.c:
                if not hasattr(model_class, col.name):
                    setattr(model_class, col.name, col)
                    added_attrs.append(col.name)
            
            print(f"✅ {model_class.__name__} reconstruido: {len(columns)} columnas, {len(added_attrs)} atributos agregados")
            
            # ✅ VERIFICAR QUE FUNCIONA
            try:
                test_count = model_class.query.count()
                print(f"   ✅ Query test: {test_count} registros encontrados")
                
                results.append({
                    'model': model_class.__name__,
                    'table': table_name,
                    'total_columns': len(columns),
                    'added_attributes': added_attrs,
                    'test_count': test_count,
                    'status': 'success'
                })
                
            except Exception as query_error:
                print(f"   ❌ Error en query test: {query_error}")
                results.append({
                    'model': model_class.__name__,
                    'table': table_name,
                    'status': 'query_error',
                    'error': str(query_error)
                })
            
        except Exception as e:
            print(f"❌ Error configurando {model_class.__name__}: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                'model': model_class.__name__,
                'table': table_name,
                'status': 'error',
                'error': str(e)
            })
    
    return results

def get_model_info(model_class):
    """Obtener información de un modelo híbrido"""
    table_name = model_class.__tablename__
    
    if hasattr(model_class, '__table__') and model_class.__table__ is not None:
        table = model_class.__table__
        
        return {
            'model': model_class.__name__,
            'table': table_name,
            'total_columns': len(table.c),
            'column_names': list(table.c.keys()),
            'primary_keys': [col.name for col in table.primary_key.columns],
            'table_object': str(type(table))
        }
    
    return {
        'model': model_class.__name__,
        'table': table_name,
        'status': 'no_table_object'
    }