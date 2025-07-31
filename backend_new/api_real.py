"""
APIs simplificadas que usan los modelos reales de la base de datos
"""
from flask import Blueprint, jsonify, request
from models_db_real import ComponenteDB, ProveedorDB, CompraDB, MaquinaDB, StockDB
from extensions import db

# Blueprint para las APIs
api_real_bp = Blueprint('api_real', __name__)

@api_real_bp.route('/componentes', methods=['GET'])
def get_componentes():
    """Obtener todos los componentes"""
    try:
        componentes = ComponenteDB.get_all_active()
        return jsonify({
            'success': True,
            'data': [comp.to_dict() for comp in componentes],
            'total': len(componentes)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_real_bp.route('/componentes/<int:id>', methods=['GET'])
def get_componente(id):
    """Obtener un componente por ID"""
    try:
        componente = ComponenteDB.get_by_id(id)
        if not componente:
            return jsonify({'success': False, 'error': 'Componente no encontrado'}), 404
        
        return jsonify({
            'success': True,
            'data': componente.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_real_bp.route('/proveedores', methods=['GET'])
def get_proveedores():
    """Obtener todos los proveedores"""
    try:
        proveedores = ProveedorDB.get_all_active()
        return jsonify({
            'success': True,
            'data': [prov.to_dict() for prov in proveedores],
            'total': len(proveedores)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_real_bp.route('/proveedores/<int:id>', methods=['GET'])
def get_proveedor(id):
    """Obtener un proveedor por ID"""
    try:
        proveedor = ProveedorDB.get_by_id(id)
        if not proveedor:
            return jsonify({'success': False, 'error': 'Proveedor no encontrado'}), 404
        
        return jsonify({
            'success': True,
            'data': proveedor.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_real_bp.route('/maquinas', methods=['GET'])
def get_maquinas():
    """Obtener todas las máquinas"""
    try:
        maquinas = MaquinaDB.get_all_active()
        return jsonify({
            'success': True,
            'data': [maq.to_dict() for maq in maquinas],
            'total': len(maquinas)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_real_bp.route('/maquinas/<int:id>', methods=['GET'])
def get_maquina(id):
    """Obtener una máquina por ID"""
    try:
        maquina = MaquinaDB.get_by_id(id)
        if not maquina:
            return jsonify({'success': False, 'error': 'Máquina no encontrada'}), 404
        
        return jsonify({
            'success': True,
            'data': maquina.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_real_bp.route('/compras', methods=['GET'])
def get_compras():
    """Obtener todas las compras"""
    try:
        compras = CompraDB.get_all()
        return jsonify({
            'success': True,
            'data': [compra.to_dict() for compra in compras],
            'total': len(compras)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_real_bp.route('/compras/<int:id>', methods=['GET'])
def get_compra(id):
    """Obtener una compra por ID"""
    try:
        compra = CompraDB.get_by_id(id)
        if not compra:
            return jsonify({'success': False, 'error': 'Compra no encontrada'}), 404
        
        return jsonify({
            'success': True,
            'data': compra.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_real_bp.route('/stock', methods=['GET'])
def get_stock():
    """Obtener todos los registros de stock"""
    try:
        stocks = StockDB.get_all()
        return jsonify({
            'success': True,
            'data': [stock.to_dict() for stock in stocks],
            'total': len(stocks)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_real_bp.route('/stock/componente/<int:componente_id>', methods=['GET'])
def get_stock_componente(componente_id):
    """Obtener stock de un componente específico"""
    try:
        stocks = StockDB.get_by_componente(componente_id)
        return jsonify({
            'success': True,
            'data': [stock.to_dict() for stock in stocks],
            'total': len(stocks)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_real_bp.route('/estadisticas/dashboard', methods=['GET'])
def get_dashboard_stats():
    """Estadísticas básicas del dashboard"""
    try:
        # Contadores básicos
        total_componentes = db.session.query(ComponenteDB).count()
        total_proveedores = db.session.query(ProveedorDB).count()
        total_maquinas = db.session.query(MaquinaDB).count()
        total_compras = db.session.query(CompraDB).count()
        
        return jsonify({
            'success': True,
            'data': {
                'total_componentes': total_componentes,
                'total_proveedores': total_proveedores,
                'total_maquinas': total_maquinas,
                'total_compras': total_compras,
                'componentes_stock_bajo': 0,  # Simplificado
                'valor_inventario': 0,  # Simplificado
                'maquinas_activas': total_maquinas,
                'compras_mes': total_compras
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
