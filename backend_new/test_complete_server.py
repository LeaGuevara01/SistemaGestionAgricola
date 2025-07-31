#!/usr/bin/env python3
"""
Servidor de prueba completo para verificar todas las rutas
"""

from flask import Flask, jsonify, request, Response, send_from_directory
from flask_cors import CORS
import os
import json
from datetime import datetime

app = Flask(__name__)

# Configurar CORS para permitir peticiones desde el frontend
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Datos de prueba simulados
MOCK_DATA = {
    'componentes': [
        {
            'id': 1,
            'nombre': 'Filtro de Aceite',
            'categoria': 'Motor',
            'precio': 25.50,
            'stock_actual': 15,
            'stock_minimo': 5,
            'proveedor_id': 1,
            'descripcion': 'Filtro de aceite para motores diesel',
            'fecha_creacion': '2024-01-15T10:30:00',
            'fecha_actualizacion': '2024-07-30T14:20:00'
        },
        {
            'id': 2,
            'nombre': 'Correa Dentada',
            'categoria': 'Transmision',
            'precio': 85.00,
            'stock_actual': 3,
            'stock_minimo': 5,
            'proveedor_id': 2,
            'descripcion': 'Correa dentada para sistema de transmisión',
            'fecha_creacion': '2024-02-20T09:15:00',
            'fecha_actualizacion': '2024-07-30T14:20:00'
        }
    ],
    'maquinas': [
        {
            'id': 1,
            'nombre': 'Tractor John Deere 6130',
            'tipo': 'Tractor',
            'modelo': '6130',
            'marca': 'John Deere',
            'año': 2018,
            'horas_trabajo': 2450,
            'ultimo_mantenimiento': '2024-06-15T08:00:00',
            'proximo_mantenimiento': '2024-09-15T08:00:00',
            'estado': 'Operativo',
            'fecha_adquisicion': '2018-03-10T00:00:00'
        }
    ],
    'proveedores': [
        {
            'id': 1,
            'nombre': 'Repuestos del Campo SA',
            'tipo': 'Repuestos',
            'contacto': 'Juan Pérez',
            'telefono': '+54 11 4444-5555',
            'email': 'juan@repuestoscampo.com',
            'direccion': 'Av. Rural 1234, Buenos Aires',
            'calificacion': 4.5,
            'activo': True
        },
        {
            'id': 2,
            'nombre': 'Transmisiones del Sur',
            'tipo': 'Especializado',
            'contacto': 'María González',
            'telefono': '+54 11 6666-7777',
            'email': 'maria@transmisionessur.com',
            'direccion': 'Calle Industrial 567, La Plata',
            'calificacion': 4.8,
            'activo': True
        }
    ],
    'compras': [
        {
            'id': 1,
            'proveedor_id': 1,
            'fecha_pedido': '2024-07-25T10:00:00',
            'fecha_entrega_esperada': '2024-08-01T10:00:00',
            'estado': 'Pendiente',
            'total': 510.00,
            'observaciones': 'Pedido urgente para mantenimiento',
            'items': [
                {'componente_id': 1, 'cantidad': 10, 'precio_unitario': 25.50},
                {'componente_id': 2, 'cantidad': 3, 'precio_unitario': 85.00}
            ]
        }
    ],
    'stock': [
        {
            'id': 1,
            'componente_id': 1,
            'cantidad': 15,
            'precio_promedio': 25.50,
            'ultima_actualizacion': '2024-07-30T14:20:00'
        },
        {
            'id': 2,
            'componente_id': 2,
            'cantidad': 3,
            'precio_promedio': 85.00,
            'ultima_actualizacion': '2024-07-30T14:20:00'
        }
    ]
}

# ================== RUTAS PRINCIPALES ==================

@app.route('/')
def index():
    """Página principal del backend"""
    accept_header = request.headers.get('Accept', '')
    is_json_request = (
        request.args.get('format') == 'json' or
        'application/json' in accept_header and 'text/html' not in accept_header or
        request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    )
    
    if is_json_request:
        return jsonify({
            'name': 'Sistema de Gestión Agrícola - Backend',
            'version': '2.0.0',
            'status': 'running',
            'endpoints': {
                'health': '/health',
                'api_test': '/api/test',
                'components': '/api/v1/componentes',
                'machines': '/api/v1/maquinas',
                'suppliers': '/api/v1/proveedores',
                'purchases': '/api/v1/compras',
                'stock': '/api/v1/stock',
                'dashboard': '/api/v1/estadisticas/dashboard'
            },
            'documentation': 'Ver BACKEND_REIMPLEMENTADO.md para documentación completa'
        })
    
    # HTML response
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sistema de Gestión Agrícola - Backend</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c5530; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }
            .status { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .endpoints { background: #f8f9fa; padding: 20px; border-radius: 5px; }
            .endpoint { margin: 8px 0; }
            .endpoint a { color: #2c5530; text-decoration: none; font-family: monospace; }
            .endpoint a:hover { text-decoration: underline; }
            .badge { background: #4CAF50; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px; }
            .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #666; }
            .test-section { background: #f0f8ff; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .test-link { display: inline-block; margin: 5px; padding: 5px 10px; background: #007bff; color: white; text-decoration: none; border-radius: 3px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌾 Sistema de Gestión Agrícola</h1>
            <div class="status">
                <strong>Estado:</strong> <span class="badge">FUNCIONANDO</span><br>
                <strong>Versión:</strong> 2.0.0<br>
                <strong>Entorno:</strong> development
            </div>
            
            <h2>📋 Endpoints Disponibles</h2>
            <div class="endpoints">
                <div class="endpoint">🔍 <a href="/health">Health Check</a> - Estado del sistema</div>
                <div class="endpoint">🧪 <a href="/api/test">API Test</a> - Prueba de conectividad</div>
                <div class="endpoint">🔧 <a href="/api/v1/componentes">Componentes</a> - Gestión de repuestos</div>
                <div class="endpoint">🚜 <a href="/api/v1/maquinas">Máquinas</a> - Equipos agrícolas</div>
                <div class="endpoint">🏢 <a href="/api/v1/proveedores">Proveedores</a> - Gestión de proveedores</div>
                <div class="endpoint">🛒 <a href="/api/v1/compras">Compras</a> - Órdenes de compra</div>
                <div class="endpoint">📦 <a href="/api/v1/stock">Stock</a> - Inventario y movimientos</div>
                <div class="endpoint">📊 <a href="/api/v1/estadisticas/dashboard">Dashboard</a> - Estadísticas principales</div>
            </div>
            
            <div class="test-section">
                <h3>🧪 Enlaces de Prueba Rápida</h3>
                <a href="/api/v1/componentes" class="test-link">Listar Componentes</a>
                <a href="/api/v1/componentes/1" class="test-link">Ver Componente 1</a>
                <a href="/api/v1/maquinas" class="test-link">Listar Máquinas</a>
                <a href="/api/v1/proveedores" class="test-link">Listar Proveedores</a>
                <a href="/api/v1/compras" class="test-link">Listar Compras</a>
                <a href="/api/v1/stock" class="test-link">Ver Stock</a>
                <a href="/api/v1/estadisticas/dashboard" class="test-link">Dashboard</a>
            </div>
            
            <h2>📚 Documentación</h2>
            <p>Para documentación completa, consulta el archivo <code>BACKEND_REIMPLEMENTADO.md</code> en el repositorio.</p>
            
            <div class="footer">
                <p>Backend reimplementado con Flask • Base de datos: PostgreSQL • CORS habilitado</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/favicon.ico')
def favicon():
    """Servir favicon"""
    static_dir = os.path.join(app.root_path, 'static')
    favicon_svg = os.path.join(static_dir, 'favicon.svg')
    if os.path.exists(favicon_svg):
        return send_from_directory(static_dir, 'favicon.svg', mimetype='image/svg+xml')
    return Response(status=204)

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'database': 'mock_db_ok',
        'environment': 'development',
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/test')
def api_test():
    """Endpoint de prueba de API"""
    return jsonify({
        'message': 'API funcionando correctamente',
        'timestamp': datetime.now().isoformat(),
        'environment': 'development',
        'status': 'success'
    })

# ================== API COMPONENTES ==================

@app.route('/api/v1/componentes', methods=['GET'])
def get_componentes():
    """Obtener lista de componentes"""
    # Simular filtros
    categoria = request.args.get('categoria')
    stock_bajo = request.args.get('stock_bajo', type=bool)
    
    componentes = MOCK_DATA['componentes'].copy()
    
    if categoria:
        componentes = [c for c in componentes if c['categoria'].lower() == categoria.lower()]
    
    if stock_bajo:
        componentes = [c for c in componentes if c['stock_actual'] <= c['stock_minimo']]
    
    return jsonify({
        'success': True,
        'data': componentes,
        'total': len(componentes),
        'message': 'Componentes obtenidos exitosamente'
    })

@app.route('/api/v1/componentes/<int:id>', methods=['GET'])
def get_componente(id):
    """Obtener componente por ID"""
    componente = next((c for c in MOCK_DATA['componentes'] if c['id'] == id), None)
    if not componente:
        return jsonify({'success': False, 'message': 'Componente no encontrado'}), 404
    
    return jsonify({
        'success': True,
        'data': componente,
        'message': 'Componente obtenido exitosamente'
    })

@app.route('/api/v1/componentes/categorias', methods=['GET'])
def get_categorias():
    """Obtener categorías de componentes"""
    categorias = list(set(c['categoria'] for c in MOCK_DATA['componentes']))
    return jsonify({
        'success': True,
        'data': categorias,
        'message': 'Categorías obtenidas exitosamente'
    })

@app.route('/api/v1/componentes/stock-bajo', methods=['GET'])
def get_componentes_stock_bajo():
    """Obtener componentes con stock bajo"""
    componentes_bajo = [c for c in MOCK_DATA['componentes'] if c['stock_actual'] <= c['stock_minimo']]
    return jsonify({
        'success': True,
        'data': componentes_bajo,
        'total': len(componentes_bajo),
        'message': 'Componentes con stock bajo obtenidos exitosamente'
    })

# ================== API MÁQUINAS ==================

@app.route('/api/v1/maquinas', methods=['GET'])
def get_maquinas():
    """Obtener lista de máquinas"""
    tipo = request.args.get('tipo')
    estado = request.args.get('estado')
    
    maquinas = MOCK_DATA['maquinas'].copy()
    
    if tipo:
        maquinas = [m for m in maquinas if m['tipo'].lower() == tipo.lower()]
    
    if estado:
        maquinas = [m for m in maquinas if m['estado'].lower() == estado.lower()]
    
    return jsonify({
        'success': True,
        'data': maquinas,
        'total': len(maquinas),
        'message': 'Máquinas obtenidas exitosamente'
    })

@app.route('/api/v1/maquinas/<int:id>', methods=['GET'])
def get_maquina(id):
    """Obtener máquina por ID"""
    maquina = next((m for m in MOCK_DATA['maquinas'] if m['id'] == id), None)
    if not maquina:
        return jsonify({'success': False, 'message': 'Máquina no encontrada'}), 404
    
    return jsonify({
        'success': True,
        'data': maquina,
        'message': 'Máquina obtenida exitosamente'
    })

@app.route('/api/v1/maquinas/tipos', methods=['GET'])
def get_tipos_maquinas():
    """Obtener tipos de máquinas"""
    tipos = list(set(m['tipo'] for m in MOCK_DATA['maquinas']))
    return jsonify({
        'success': True,
        'data': tipos,
        'message': 'Tipos de máquinas obtenidos exitosamente'
    })

# ================== API PROVEEDORES ==================

@app.route('/api/v1/proveedores', methods=['GET'])
def get_proveedores():
    """Obtener lista de proveedores"""
    tipo = request.args.get('tipo')
    activo = request.args.get('activo', type=bool)
    
    proveedores = MOCK_DATA['proveedores'].copy()
    
    if tipo:
        proveedores = [p for p in proveedores if p['tipo'].lower() == tipo.lower()]
    
    if activo is not None:
        proveedores = [p for p in proveedores if p['activo'] == activo]
    
    return jsonify({
        'success': True,
        'data': proveedores,
        'total': len(proveedores),
        'message': 'Proveedores obtenidos exitosamente'
    })

@app.route('/api/v1/proveedores/<int:id>', methods=['GET'])
def get_proveedor(id):
    """Obtener proveedor por ID"""
    proveedor = next((p for p in MOCK_DATA['proveedores'] if p['id'] == id), None)
    if not proveedor:
        return jsonify({'success': False, 'message': 'Proveedor no encontrado'}), 404
    
    return jsonify({
        'success': True,
        'data': proveedor,
        'message': 'Proveedor obtenido exitosamente'
    })

@app.route('/api/v1/proveedores/tipos', methods=['GET'])
def get_tipos_proveedores():
    """Obtener tipos de proveedores"""
    tipos = list(set(p['tipo'] for p in MOCK_DATA['proveedores']))
    return jsonify({
        'success': True,
        'data': tipos,
        'message': 'Tipos de proveedores obtenidos exitosamente'
    })

# ================== API COMPRAS ==================

@app.route('/api/v1/compras', methods=['GET'])
def get_compras():
    """Obtener lista de compras"""
    estado = request.args.get('estado')
    proveedor_id = request.args.get('proveedor_id', type=int)
    
    compras = MOCK_DATA['compras'].copy()
    
    if estado:
        compras = [c for c in compras if c['estado'].lower() == estado.lower()]
    
    if proveedor_id:
        compras = [c for c in compras if c['proveedor_id'] == proveedor_id]
    
    return jsonify({
        'success': True,
        'data': compras,
        'total': len(compras),
        'message': 'Compras obtenidas exitosamente'
    })

@app.route('/api/v1/compras/<int:id>', methods=['GET'])
def get_compra(id):
    """Obtener compra por ID"""
    compra = next((c for c in MOCK_DATA['compras'] if c['id'] == id), None)
    if not compra:
        return jsonify({'success': False, 'message': 'Compra no encontrada'}), 404
    
    return jsonify({
        'success': True,
        'data': compra,
        'message': 'Compra obtenida exitosamente'
    })

@app.route('/api/v1/compras/estados', methods=['GET'])
def get_estados_compras():
    """Obtener estados de compras"""
    estados = ['Pendiente', 'En Proceso', 'Entregado', 'Cancelado']
    return jsonify({
        'success': True,
        'data': estados,
        'message': 'Estados de compras obtenidos exitosamente'
    })

# ================== API STOCK ==================

@app.route('/api/v1/stock', methods=['GET'])
def get_stock():
    """Obtener lista de stock"""
    componente_id = request.args.get('componente_id', type=int)
    
    stock = MOCK_DATA['stock'].copy()
    
    if componente_id:
        stock = [s for s in stock if s['componente_id'] == componente_id]
    
    return jsonify({
        'success': True,
        'data': stock,
        'total': len(stock),
        'message': 'Stock obtenido exitosamente'
    })

@app.route('/api/v1/stock/<int:id>', methods=['GET'])
def get_stock_item(id):
    """Obtener item de stock por ID"""
    item = next((s for s in MOCK_DATA['stock'] if s['id'] == id), None)
    if not item:
        return jsonify({'success': False, 'message': 'Item de stock no encontrado'}), 404
    
    return jsonify({
        'success': True,
        'data': item,
        'message': 'Item de stock obtenido exitosamente'
    })

# ================== API ESTADÍSTICAS ==================

@app.route('/api/v1/estadisticas/dashboard', methods=['GET'])
def get_dashboard():
    """Obtener estadísticas del dashboard"""
    dashboard = {
        'resumen': {
            'total_componentes': len(MOCK_DATA['componentes']),
            'total_maquinas': len(MOCK_DATA['maquinas']),
            'total_proveedores': len(MOCK_DATA['proveedores']),
            'compras_pendientes': len([c for c in MOCK_DATA['compras'] if c['estado'] == 'Pendiente']),
            'componentes_stock_bajo': len([c for c in MOCK_DATA['componentes'] if c['stock_actual'] <= c['stock_minimo']]),
            'valor_total_stock': sum(s['cantidad'] * s['precio_promedio'] for s in MOCK_DATA['stock'])
        },
        'graficos': {
            'stock_por_categoria': {
                'Motor': 15,
                'Transmision': 3
            },
            'compras_ultimo_mes': {
                'labels': ['Semana 1', 'Semana 2', 'Semana 3', 'Semana 4'],
                'valores': [2, 1, 3, 1]
            }
        },
        'alertas': [
            {
                'tipo': 'warning',
                'mensaje': 'Correa Dentada tiene stock bajo (3 unidades)',
                'timestamp': datetime.now().isoformat()
            }
        ]
    }
    
    return jsonify({
        'success': True,
        'data': dashboard,
        'message': 'Dashboard obtenido exitosamente'
    })

if __name__ == '__main__':
    print("🌾 Iniciando servidor completo de pruebas...")
    print("=" * 60)
    print("📋 Endpoints disponibles:")
    print("   - Página principal: http://127.0.0.1:5000/")
    print("   - Health check: http://127.0.0.1:5000/health")
    print("   - API test: http://127.0.0.1:5000/api/test")
    print("   - Componentes: http://127.0.0.1:5000/api/v1/componentes")
    print("   - Máquinas: http://127.0.0.1:5000/api/v1/maquinas")
    print("   - Proveedores: http://127.0.0.1:5000/api/v1/proveedores")
    print("   - Compras: http://127.0.0.1:5000/api/v1/compras")
    print("   - Stock: http://127.0.0.1:5000/api/v1/stock")
    print("   - Dashboard: http://127.0.0.1:5000/api/v1/estadisticas/dashboard")
    print("=" * 60)
    
    app.run(host='127.0.0.1', port=5000, debug=True)
