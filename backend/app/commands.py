import click
from flask.cli import with_appcontext
from app.utils.db import db
from app.models import Componente, Maquina, Compra, Proveedor, Stock
import json

@click.command()
@with_appcontext
def init_db():
    """Inicializar base de datos"""
    db.create_all()
    click.echo('✅ Base de datos inicializada.')

@click.command()
@with_appcontext
def drop_db():
    """Eliminar todas las tablas"""
    db.drop_all()
    click.echo('🗑️ Tablas eliminadas.')

@click.command()
@with_appcontext
def reset_db():
    """Reiniciar base de datos"""
    db.drop_all()
    db.create_all()
    click.echo('🔄 Base de datos reiniciada.')

@click.command()
@with_appcontext
def show_tables():
    """Mostrar todas las tablas"""
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    click.echo('📊 Tablas en la base de datos:')
    for table in tables:
        click.echo(f'  - {table}')

@click.command()
@click.argument('table_name')
@with_appcontext
def describe_table(table_name):
    """Describir estructura de una tabla"""
    inspector = db.inspect(db.engine)
    try:
        columns = inspector.get_columns(table_name)
        click.echo(f'📋 Estructura de la tabla "{table_name}":')
        for col in columns:
            nullable = "NULL" if col["nullable"] else "NOT NULL"
            default = f" DEFAULT {col.get('default')}" if col.get('default') else ""
            click.echo(f'  - {col["name"]}: {col["type"]} {nullable}{default}')
    except Exception as e:
        click.echo(f'❌ Error: {e}')

@click.command()
@with_appcontext
def check_models():
    """Verificar si los modelos coinciden con la BD"""
    inspector = db.inspect(db.engine)
    db_tables = set(inspector.get_table_names())
    
    # Modelos definidos
    model_tables = set()
    for model in [Componente, Maquina, Compra, Proveedor, Stock]:
        if hasattr(model, '__tablename__'):
            model_tables.add(model.__tablename__)
    
    click.echo('🔍 Verificación de modelos vs BD:')
    
    # Tablas en modelo pero no en BD
    missing_in_db = model_tables - db_tables
    if missing_in_db:
        click.echo('❌ Tablas definidas en modelos pero NO en BD:')
        for table in missing_in_db:
            click.echo(f'  - {table}')
    
    # Tablas en BD pero no en modelos
    missing_in_models = db_tables - model_tables
    if missing_in_models:
        click.echo('⚠️ Tablas en BD pero NO en modelos:')
        for table in missing_in_models:
            click.echo(f'  - {table}')
    
    # Tablas que coinciden
    matching = model_tables & db_tables
    if matching:
        click.echo('✅ Tablas que coinciden:')
        for table in matching:
            click.echo(f'  - {table}')

@click.command()
@with_appcontext
def sync_models():
    """Sincronizar modelos con BD (crear tablas faltantes)"""
    try:
        db.create_all()
        click.echo('✅ Modelos sincronizados con BD.')
    except Exception as e:
        click.echo(f'❌ Error sincronizando: {e}')

@click.command()
@with_appcontext
def seed_data():
    """Insertar datos de prueba"""
    try:
        # Verificar si ya hay datos
        if Componente.query.count() > 0:
            click.echo('⚠️ Ya existen componentes. Use --force para sobrescribir.')
            return
        
        # Crear componentes de ejemplo
        componentes = [
            Componente(
                nombre='Filtro de aire',
                descripcion='Filtro de aire para tractor',
                numero_parte='FA-001',
                categoria='Filtro',
                precio_unitario=25.50,
                stock_minimo=10,
                stock_actual=15
            ),
            Componente(
                nombre='Aceite hidráulico',
                descripcion='Aceite hidráulico 20L',
                numero_parte='AH-002',
                categoria='Hidráulico',
                precio_unitario=85.00,
                stock_minimo=5,
                stock_actual=8
            ),
            Componente(
                nombre='Neumático 18.4-34',
                descripcion='Neumático trasero para tractor',
                numero_parte='NT-003',
                categoria='Neumático',
                precio_unitario=450.00,
                stock_minimo=2,
                stock_actual=4
            )
        ]
        
        for comp in componentes:
            db.session.add(comp)
        
        db.session.commit()
        click.echo('✅ Datos de prueba insertados correctamente.')
        
    except Exception as e:
        db.session.rollback()
        click.echo(f'❌ Error insertando datos: {e}')

@click.command()
@click.argument('table_name')
@click.option('--limit', default=10, help='Número de registros a mostrar')
@with_appcontext
def show_data(table_name, limit):
    """Mostrar datos de una tabla"""
    try:
        if table_name == 'componentes':
            items = Componente.query.limit(limit).all()
            click.echo(f'📋 Últimos {limit} componentes:')
            for item in items:
                click.echo(f'  - {item.id}: {item.nombre} (Precio: ${item.precio or 0})')
        
        elif table_name == 'proveedores':
            items = Proveedor.query.limit(limit).all()
            click.echo(f'📋 Últimos {limit} proveedores:')
            for item in items:
                click.echo(f'  - {item.id}: {item.nombre} - {item.telefono or "Sin teléfono"}')
        
        elif table_name == 'maquinas':
            items = Maquina.query.limit(limit).all()
            click.echo(f'📋 Últimas {limit} máquinas:')
            for item in items:
                click.echo(f'  - {item.id}: {item.codigo} - {item.nombre}')
        
        elif table_name == 'compras':
            items = Compra.query.limit(limit).all()
            click.echo(f'📋 Últimas {limit} compras:')
            for item in items:
                click.echo(f'  - {item.id}: Cant:{item.cantidad} Precio:{item.precio_unitario}')
        
        elif table_name == 'stock':
            items = Stock.query.limit(limit).all()
            click.echo(f'📋 Últimos {limit} movimientos de stock:')
            for item in items:
                click.echo(f'  - {item.id}: {item.tipo} - Cant:{item.cantidad}')
        
        else:
            # ✅ QUERY GENÉRICO MEJORADO
            result = db.session.execute(db.text(f'SELECT * FROM {table_name} LIMIT {limit}'))
            click.echo(f'📋 Datos de {table_name}:')
            
            # Obtener nombres de columnas
            columns = result.keys()
            rows = result.fetchall()
            
            for row in rows:
                # Mostrar solo primeras 3 columnas para no saturar
                row_data = dict(zip(columns, row))
                display_items = list(row_data.items())[:3]
                click.echo(f'  - {dict(display_items)}')
                
    except Exception as e:
        click.echo(f'❌ Error: {e}')

@click.command()
@with_appcontext
def export_schema():
    """Exportar esquema de BD a JSON"""
    try:
        inspector = db.inspect(db.engine)
        schema = {}
        
        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            foreign_keys = inspector.get_foreign_keys(table_name)
            indexes = inspector.get_indexes(table_name)
            
            schema[table_name] = {
                'columns': [
                    {
                        'name': col['name'],
                        'type': str(col['type']),
                        'nullable': col['nullable'],
                        'default': str(col.get('default')) if col.get('default') else None,
                        'primary_key': col.get('primary_key', False)
                    } for col in columns
                ],
                'foreign_keys': foreign_keys,
                'indexes': indexes
            }
        
        with open('db_schema.json', 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)
        
        click.echo('✅ Esquema exportado a db_schema.json')
        
    except Exception as e:
        click.echo(f'❌ Error exportando: {e}')

@click.command()
@with_appcontext
def show_full_schema():
    """Mostrar esquema completo de todas las tablas"""
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    
    click.echo('🗂️ ESQUEMA COMPLETO DE LA BASE DE DATOS:')
    click.echo('=' * 60)
    
    for table_name in sorted(tables):
        try:
            columns = inspector.get_columns(table_name)
            fks = inspector.get_foreign_keys(table_name)
            
            click.echo(f'\n📋 TABLA: {table_name}')
            click.echo('-' * 40)
            
            for col in columns:
                pk = " 🔑 PK" if col.get('primary_key') else ""
                nullable = "NULL" if col["nullable"] else "NOT NULL"
                default = f" DEFAULT {col.get('default')}" if col.get('default') else ""
                click.echo(f'  - {col["name"]}: {col["type"]} {nullable}{default}{pk}')
            
            if fks:
                click.echo('  🔗 FOREIGN KEYS:')
                for fk in fks:
                    click.echo(f'    - {fk["constrained_columns"]} -> {fk["referred_table"]}.{fk["referred_columns"]}')
                    
        except Exception as e:
            click.echo(f'  ❌ Error: {e}')

@click.command('insert-test-data')
@with_appcontext
def insert_test_data():
    """Insertar datos de prueba"""
    from app.models.componente import Componente
    from app.models.maquina import Maquina
    from app.models.proveedor import Proveedor
    from app.models.stock import Stock
    from app.utils.db import db
    
    try:
        # ✅ VERIFICAR si ya hay datos
        existing_componentes = Componente.query.count()
        existing_maquinas = Maquina.query.count()
        
        click.echo(f"📊 Datos existentes: {existing_componentes} componentes, {existing_maquinas} máquinas")
        
        if existing_componentes > 0:
            click.echo("✅ Ya hay componentes en la BD")
        else:
            # ✅ INSERTAR COMPONENTES DE PRUEBA
            componentes_prueba = [
                {
                    'nombre': 'Filtro de aire',
                    'precio': 42000.0,
                    'descripcion': 'Filtro de aire para motor diésel',
                    'tipo': 'Filtros',
                    'marca': 'Mann',
                    'modelo': 'C25114/1'
                },
                {
                    'nombre': 'Aceite hidráulico',
                    'precio': 7000.0,
                    'descripcion': 'Aceite hidráulico ISO 68',
                    'tipo': 'Lubricantes',
                    'marca': 'Shell',
                    'modelo': 'Tellus S2 V68'
                },
                {
                    'nombre': 'Batería 12V 150Ah',
                    'precio': 38000.0,
                    'descripcion': 'Batería de arranque 12V 150Ah',
                    'tipo': 'Eléctrico',
                    'marca': 'Willard',
                    'modelo': 'UB-12150'
                }
            ]
            
            for comp_data in componentes_prueba:
                comp = Componente(**comp_data)
                db.session.add(comp)
                
            click.echo(f"✅ {len(componentes_prueba)} componentes insertados")
        
        if existing_maquinas > 0:
            click.echo("✅ Ya hay máquinas en la BD")
        else:
            # ✅ INSERTAR MÁQUINAS DE PRUEBA
            maquinas_prueba = [
                {
                    'nombre': 'Cosechadora John Deere',
                    'codigo': 'JD001',
                    'marca': 'John Deere',
                    'modelo': 'S670',
                    'año': 2020,
                    'estado': 'operativo'
                },
                {
                    'nombre': 'Tractor Case IH',
                    'codigo': 'CIH001',
                    'marca': 'Case IH',
                    'modelo': 'Maxxum 125',
                    'año': 2019,
                    'estado': 'operativo'
                }
            ]
            
            for maq_data in maquinas_prueba:
                maq = Maquina(**maq_data)
                db.session.add(maq)
                
            click.echo(f"✅ {len(maquinas_prueba)} máquinas insertadas")
        
        db.session.commit()
        click.echo("🎯 Datos de prueba insertados exitosamente")
        
    except Exception as e:
        click.echo(f"❌ Error insertando datos: {e}")
        db.session.rollback()
        import traceback
        traceback.print_exc()

def init_app(app):
    """Registrar comandos en la app"""
    app.cli.add_command(init_db)
    app.cli.add_command(drop_db)
    app.cli.add_command(reset_db)
    app.cli.add_command(show_tables)
    app.cli.add_command(describe_table)
    app.cli.add_command(check_models)
    app.cli.add_command(sync_models)
    app.cli.add_command(seed_data)
    app.cli.add_command(show_data)
    app.cli.add_command(export_schema)
    app.cli.add_command(show_full_schema)
    app.cli.add_command(insert_test_data)