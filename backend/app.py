#!/usr/bin/env python3
"""
Sistema de Gestión Agrícola - Backend Principal
Servidor Flask con datos simulados para desarrollo rápido
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
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Datos de prueba simulados - Expandidos y más realistas
MOCK_DATA = {
    'componentes': [
        {
            'id': 1,
            'nombre': 'Filtro de Aceite',
            'numero_parte': 'FA-001',
            'categoria': 'Motor',
            'marca': 'Mahle',
            'modelo': 'OC90',
            'precio_unitario': 25.50,
            'moneda': 'USD',
            'stock_actual': 15,
            'stock_minimo': 5,
            'stock_maximo': 50,
            'proveedor_id': 1,
            'descripcion': 'Filtro de aceite para motores diesel',
            'especificaciones': 'Rosca: 3/4"-16 UNF, Diámetro: 93mm',
            'foto': 'filtro_aceite.jpg',
            'documentos': ['manual_FA001.pdf'],
            'activo': True,
            'created_at': '2024-01-15T10:30:00',
            'updated_at': '2024-07-30T14:20:00'
        },
        {
            'id': 2,
            'nombre': 'Correa Dentada',
            'numero_parte': 'CD-002',
            'categoria': 'Transmision',
            'marca': 'Gates',
            'modelo': 'T125',
            'precio_unitario': 85.00,
            'moneda': 'USD',
            'stock_actual': 3,
            'stock_minimo': 5,
            'stock_maximo': 20,
            'proveedor_id': 2,
            'descripcion': 'Correa dentada para sistema de transmisión',
            'especificaciones': 'Longitud: 1250mm, Ancho: 25mm, 100 dientes',
            'foto': 'correa_dentada.jpg',
            'documentos': ['especificaciones_CD002.pdf'],
            'activo': True,
            'created_at': '2024-02-20T09:15:00',
            'updated_at': '2024-07-30T14:20:00'
        },
        {
            'id': 3,
            'nombre': 'Batería 12V',
            'numero_parte': 'BAT-003',
            'categoria': 'Electrico',
            'marca': 'Bosch',
            'modelo': 'S4025',
            'precio_unitario': 180.00,
            'moneda': 'USD',
            'stock_actual': 8,
            'stock_minimo': 3,
            'stock_maximo': 15,
            'proveedor_id': 1,
            'descripcion': 'Batería 12V 60Ah para arranque',
            'especificaciones': '60Ah, 540A, 242x175x190mm',
            'foto': 'bateria_12v.jpg',
            'documentos': [],
            'activo': True,
            'created_at': '2024-03-10T11:45:00',
            'updated_at': '2024-07-30T14:20:00'
        }
    ],
    'maquinas': [
        {
            'id': 1,
            'codigo': 'JD6130-001',
            'nombre': 'Tractor John Deere 6130',
            'tipo': 'Tractor',
            'modelo': '6130',
            'marca': 'John Deere',
            'año': 2018,
            'horas_uso': 2450,
            'ultimo_mantenimiento': '2024-06-15T08:00:00',
            'proximo_mantenimiento': '2024-09-15T08:00:00',
            'estado': 'Operativo',
            'ubicacion': 'Campo Norte',
            'observaciones': 'Mantenimiento preventivo al día',
            'foto': 'tractor_jd6130.jpg',
            'activo': True,
            'created_at': '2018-03-10T00:00:00',
            'updated_at': '2024-07-30T14:20:00'
        },
        {
            'id': 2,
            'codigo': 'NH-T7040',
            'nombre': 'Tractor New Holland T7040',
            'tipo': 'Tractor',
            'modelo': 'T7040',
            'marca': 'New Holland',
            'año': 2020,
            'horas_uso': 1200,
            'ultimo_mantenimiento': '2024-07-01T09:00:00',
            'proximo_mantenimiento': '2024-10-01T09:00:00',
            'estado': 'Operativo',
            'ubicacion': 'Campo Sur',
            'observaciones': 'Nuevo, en garantía',
            'foto': 'tractor_nh_t7040.jpg',
            'activo': True,
            'created_at': '2020-05-15T00:00:00',
            'updated_at': '2024-07-30T14:20:00'
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
            'localidad': 'Buenos Aires',
            'rubro': 'Repuestos',
            'calificacion': 4.5,
            'observaciones': 'Proveedor principal, muy confiable',
            'activo': True,
            'created_at': '2023-01-10T00:00:00',
            'updated_at': '2024-07-30T14:20:00'
        },
        {
            'id': 2,
            'nombre': 'Transmisiones del Sur',
            'tipo': 'Especializado',
            'contacto': 'María González',
            'telefono': '+54 11 6666-7777',
            'email': 'maria@transmisionessur.com',
            'direccion': 'Calle Industrial 567, La Plata',
            'localidad': 'La Plata',
            'rubro': 'Transmisiones',
            'calificacion': 4.8,
            'observaciones': 'Especialistas en transmisiones',
            'activo': True,
            'created_at': '2023-03-15T00:00:00',
            'updated_at': '2024-07-30T14:20:00'
        },
        {
            'id': 3,
            'nombre': 'ElectroAgro SRL',
            'tipo': 'Electricidad',
            'contacto': 'Carlos López',
            'telefono': '+54 11 5555-3333',
            'email': 'carlos@electroagro.com',
            'direccion': 'Av. Industria 890, Córdoba',
            'localidad': 'Córdoba',
            'rubro': 'Componentes Eléctricos',
            'calificacion': 4.2,
            'observaciones': 'Buenos precios en componentes eléctricos',
            'activo': True,
            'created_at': '2023-06-20T00:00:00',
            'updated_at': '2024-07-30T14:20:00'
        }
    ],
    'compras': [
        {
            'id': 1,
            'numero_compra': 'COMP-001',
            'numero_factura': 'FAC-2024-001',
            'proveedor_id': 1,
            'componente_id': 1,
            'cantidad': 10,
            'precio_unitario': 25.50,
            'total': 255.00,
            'moneda': 'USD',
            'fecha_compra': '2024-07-25T10:00:00',
            'fecha_entrega_esperada': '2024-08-01T10:00:00',
            'fecha_entrega_real': None,
            'estado': 'pendiente',
            'observacion': 'Pedido urgente para mantenimiento',
            'created_at': '2024-07-25T10:00:00',
            'updated_at': '2024-07-30T14:20:00'
        },
        {
            'id': 2,
            'numero_compra': 'COMP-002',
            'numero_factura': 'FAC-2024-002',
            'proveedor_id': 2,
            'componente_id': 2,
            'cantidad': 3,
            'precio_unitario': 85.00,
            'total': 255.00,
            'moneda': 'USD',
            'fecha_compra': '2024-07-20T14:30:00',
            'fecha_entrega_esperada': '2024-07-27T14:30:00',
            'fecha_entrega_real': '2024-07-26T16:00:00',
            'estado': 'completada',
            'observacion': 'Entrega adelantada',
            'created_at': '2024-07-20T14:30:00',
            'updated_at': '2024-07-26T16:00:00'
        },
        {
            'id': 3,
            'numero_compra': 'COMP-003',
            'numero_factura': 'FAC-2024-003',
            'proveedor_id': 3,
            'componente_id': 3,
            'cantidad': 2,
            'precio_unitario': 180.00,
            'total': 360.00,
            'moneda': 'USD',
            'fecha_compra': '2024-07-28T09:15:00',
            'fecha_entrega_esperada': '2024-08-05T09:15:00',
            'fecha_entrega_real': None,
            'estado': 'en_proceso',
            'observacion': 'En preparación para envío',
            'created_at': '2024-07-28T09:15:00',
            'updated_at': '2024-07-29T11:30:00'
        }
    ],
    'stock': [
        {
            'id': 1,
            'componente_id': 1,
            'cantidad': 15,
            'precio_promedio': 25.50,
            'valor_total': 382.50,
            'ultima_actualizacion': '2024-07-30T14:20:00',
            'tipo_movimiento': 'entrada',
            'observacion': 'Stock inicial'
        },
        {
            'id': 2,
            'componente_id': 2,
            'cantidad': 3,
            'precio_promedio': 85.00,
            'valor_total': 255.00,
            'ultima_actualizacion': '2024-07-30T14:20:00',
            'tipo_movimiento': 'entrada',
            'observacion': 'Últimas unidades'
        },
        {
            'id': 3,
            'componente_id': 3,
            'cantidad': 8,
            'precio_promedio': 180.00,
            'valor_total': 1440.00,
            'ultima_actualizacion': '2024-07-30T14:20:00',
            'tipo_movimiento': 'entrada',
            'observacion': 'Stock regular'
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
            'name': 'Sistema de Gestión Agrícola - Backend Principal',
            'version': '2.1.0',
            'status': 'running',
            'ambiente': 'development',
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
            'documentation': 'Backend con datos simulados para desarrollo rápido'
        })
    
    # HTML response mejorada
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sistema de Gestión Agrícola - Backend</title>
        <style>
            body { font-family: 'Segoe UI', sans-serif; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
            .container { max-width: 900px; margin: 40px auto; background: white; border-radius: 15px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); overflow: hidden; }
            .header { background: linear-gradient(135deg, #4CAF50 0%, #2c5530 100%); color: white; padding: 30px; text-align: center; }
            .header h1 { margin: 0; font-size: 2.5rem; font-weight: 300; }
            .header p { margin: 10px 0 0 0; opacity: 0.9; }
            .status { background: #e8f5e8; padding: 20px; margin: 20px; border-radius: 10px; border-left: 4px solid #4CAF50; }
            .endpoints { padding: 20px; }
            .endpoint-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin: 20px 0; }
            .endpoint { background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #007bff; transition: transform 0.2s; }
            .endpoint:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
            .endpoint a { color: #2c5530; text-decoration: none; font-family: 'Courier New', monospace; font-weight: bold; }
            .endpoint a:hover { text-decoration: underline; }
            .badge { background: #4CAF50; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; }
            .test-section { background: linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%); padding: 20px; margin: 20px; border-radius: 10px; }
            .test-links { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 15px; }
            .test-link { padding: 8px 16px; background: #007bff; color: white; text-decoration: none; border-radius: 25px; font-size: 14px; transition: background 0.3s; }
            .test-link:hover { background: #0056b3; }
            .footer { background: #f8f9fa; padding: 20px; text-align: center; color: #666; margin-top: 20px; }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 15px; margin: 20px; }
            .stat { background: white; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .stat-number { font-size: 2rem; font-weight: bold; color: #4CAF50; }
            .stat-label { color: #666; font-size: 0.9rem; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌾 Sistema de Gestión Agrícola</h1>
                <p>Backend Principal - Versión 2.1.0</p>
            </div>
            
            <div class="status">
                <strong>🚀 Estado del Sistema:</strong> <span class="badge">OPERATIVO</span><br>
                <strong>🌐 Entorno:</strong> Desarrollo<br>
                <strong>📊 Base de datos:</strong> Mock Data (Simulada)<br>
                <strong>🔗 CORS:</strong> Habilitado para frontend
            </div>
            
            <div class="stats">
                <div class="stat">
                    <div class="stat-number">18</div>
                    <div class="stat-label">Endpoints</div>
                </div>
                <div class="stat">
                    <div class="stat-number">3</div>
                    <div class="stat-label">Componentes</div>
                </div>
                <div class="stat">
                    <div class="stat-number">2</div>
                    <div class="stat-label">Máquinas</div>
                </div>
                <div class="stat">
                    <div class="stat-number">3</div>
                    <div class="stat-label">Proveedores</div>
                </div>
            </div>
            
            <div class="endpoints">
                <h2 style="color: #2c5530;">📋 Endpoints Disponibles</h2>
                <div class="endpoint-grid">
                    <div class="endpoint">
                        <h4>🔍 Sistema</h4>
                        <div><a href="/health">Health Check</a></div>
                        <div><a href="/api/test">API Test</a></div>
                    </div>
                    <div class="endpoint">
                        <h4>🔧 Componentes</h4>
                        <div><a href="/api/v1/componentes">Lista completa</a></div>
                        <div><a href="/api/v1/componentes/categorias">Categorías</a></div>
                        <div><a href="/api/v1/componentes/stock-bajo">Stock bajo</a></div>
                    </div>
                    <div class="endpoint">
                        <h4>🚜 Máquinas</h4>
                        <div><a href="/api/v1/maquinas">Lista completa</a></div>
                        <div><a href="/api/v1/maquinas/tipos">Tipos</a></div>
                    </div>
                    <div class="endpoint">
                        <h4>🏢 Proveedores</h4>
                        <div><a href="/api/v1/proveedores">Lista completa</a></div>
                        <div><a href="/api/v1/proveedores/tipos">Tipos</a></div>
                    </div>
                    <div class="endpoint">
                        <h4>🛒 Compras</h4>
                        <div><a href="/api/v1/compras">Lista completa</a></div>
                        <div><a href="/api/v1/compras/estados">Estados</a></div>
                    </div>
                    <div class="endpoint">
                        <h4>📦 Stock</h4>
                        <div><a href="/api/v1/stock">Inventario</a></div>
                    </div>
                    <div class="endpoint">
                        <h4>📊 Estadísticas</h4>
                        <div><a href="/api/v1/estadisticas/dashboard">Dashboard</a></div>
                    </div>
                </div>
            </div>
            
            <div class="test-section">
                <h3>🧪 Pruebas Rápidas</h3>
                <p>Enlaces directos para probar los endpoints:</p>
                <div class="test-links">
                    <a href="/api/v1/componentes" class="test-link">Ver Componentes</a>
                    <a href="/api/v1/componentes/1" class="test-link">Componente #1</a>
                    <a href="/api/v1/maquinas" class="test-link">Ver Máquinas</a>
                    <a href="/api/v1/proveedores" class="test-link">Ver Proveedores</a>
                    <a href="/api/v1/compras" class="test-link">Ver Compras</a>
                    <a href="/api/v1/stock" class="test-link">Ver Stock</a>
                    <a href="/api/v1/estadisticas/dashboard" class="test-link">Dashboard</a>
                </div>
            </div>
            
            <div class="footer">
                <p><strong>Sistema de Gestión Agrícola</strong><br>
                Backend con Flask • Datos simulados • CORS habilitado<br>
                <em>Listo para conectar con frontend React</em></p>
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
        'database': 'mock_data_ok',
        'environment': 'development',
        'version': '2.1.0',
        'timestamp': datetime.now().isoformat(),
        'data_counts': {
            'componentes': len(MOCK_DATA['componentes']),
            'maquinas': len(MOCK_DATA['maquinas']),
            'proveedores': len(MOCK_DATA['proveedores']),
            'compras': len(MOCK_DATA['compras']),
            'stock': len(MOCK_DATA['stock'])
        }
    })

@app.route('/api/test')
def api_test():
    """Endpoint de prueba de API"""
    return jsonify({
        'message': 'API funcionando correctamente',
        'timestamp': datetime.now().isoformat(),
        'environment': 'development',
        'version': '2.1.0',
        'status': 'success',
        'cors_enabled': True
    })

# ================== API COMPONENTES ==================

@app.route('/api/v1/componentes', methods=['GET'])
def get_componentes():
    """Obtener lista de componentes"""
    # Parámetros de filtro
    categoria = request.args.get('categoria')
    stock_bajo = request.args.get('stock_bajo', type=bool)
    search = request.args.get('search')
    activo = request.args.get('activo', type=bool, default=True)
    
    # Paginación
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    componentes = MOCK_DATA['componentes'].copy()
    
    # Aplicar filtros
    if categoria:
        componentes = [c for c in componentes if c['categoria'].lower() == categoria.lower()]
    
    if stock_bajo:
        componentes = [c for c in componentes if c['stock_actual'] <= c['stock_minimo']]
    
    if search:
        search_lower = search.lower()
        componentes = [c for c in componentes if 
                      search_lower in c['nombre'].lower() or 
                      search_lower in c['numero_parte'].lower() or
                      search_lower in c['descripcion'].lower()]
    
    if activo is not None:
        componentes = [c for c in componentes if c['activo'] == activo]
    
    # Simular paginación
    total = len(componentes)
    start = (page - 1) * per_page
    end = start + per_page
    componentes_page = componentes[start:end]
    
    return jsonify({
        'success': True,
        'data': componentes_page,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        },
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
        'data': sorted(categorias),
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
    activo = request.args.get('activo', type=bool, default=True)
    search = request.args.get('search')
    
    maquinas = MOCK_DATA['maquinas'].copy()
    
    if tipo:
        maquinas = [m for m in maquinas if m['tipo'].lower() == tipo.lower()]
    
    if estado:
        maquinas = [m for m in maquinas if m['estado'].lower() == estado.lower()]
    
    if activo is not None:
        maquinas = [m for m in maquinas if m['activo'] == activo]
    
    if search:
        search_lower = search.lower()
        maquinas = [m for m in maquinas if 
                   search_lower in m['nombre'].lower() or 
                   search_lower in m['codigo'].lower() or
                   search_lower in m['marca'].lower()]
    
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
        'data': sorted(tipos),
        'message': 'Tipos de máquinas obtenidos exitosamente'
    })

# ================== API PROVEEDORES ==================

@app.route('/api/v1/proveedores', methods=['GET'])
def get_proveedores():
    """Obtener lista de proveedores"""
    tipo = request.args.get('tipo')
    activo = request.args.get('activo', type=bool, default=True)
    search = request.args.get('search')
    
    proveedores = MOCK_DATA['proveedores'].copy()
    
    if tipo:
        proveedores = [p for p in proveedores if p['tipo'].lower() == tipo.lower()]
    
    if activo is not None:
        proveedores = [p for p in proveedores if p['activo'] == activo]
    
    if search:
        search_lower = search.lower()
        proveedores = [p for p in proveedores if 
                      search_lower in p['nombre'].lower() or 
                      search_lower in p['contacto'].lower() or
                      search_lower in p['email'].lower()]
    
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
        'data': sorted(tipos),
        'message': 'Tipos de proveedores obtenidos exitosamente'
    })

# ================== API COMPRAS ==================

@app.route('/api/v1/compras', methods=['GET'])
def get_compras():
    """Obtener lista de compras"""
    estado = request.args.get('estado')
    proveedor_id = request.args.get('proveedor_id', type=int)
    componente_id = request.args.get('componente_id', type=int)
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')
    
    compras = MOCK_DATA['compras'].copy()
    
    if estado:
        compras = [c for c in compras if c['estado'].lower() == estado.lower()]
    
    if proveedor_id:
        compras = [c for c in compras if c['proveedor_id'] == proveedor_id]
    
    if componente_id:
        compras = [c for c in compras if c['componente_id'] == componente_id]
    
    # Aquí se podrían aplicar filtros de fecha si fuera necesario
    
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
    estados = ['pendiente', 'en_proceso', 'completada', 'cancelada']
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
    tipo_movimiento = request.args.get('tipo_movimiento')
    
    stock = MOCK_DATA['stock'].copy()
    
    if componente_id:
        stock = [s for s in stock if s['componente_id'] == componente_id]
    
    if tipo_movimiento:
        stock = [s for s in stock if s['tipo_movimiento'].lower() == tipo_movimiento.lower()]
    
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
    
    # Calcular estadísticas reales de los datos mock
    total_componentes = len(MOCK_DATA['componentes'])
    total_maquinas = len(MOCK_DATA['maquinas'])
    total_proveedores = len(MOCK_DATA['proveedores'])
    total_compras = len(MOCK_DATA['compras'])
    
    compras_pendientes = len([c for c in MOCK_DATA['compras'] if c['estado'] == 'pendiente'])
    componentes_stock_bajo = len([c for c in MOCK_DATA['componentes'] if c['stock_actual'] <= c['stock_minimo']])
    valor_total_stock = sum(s['valor_total'] for s in MOCK_DATA['stock'])
    maquinas_activas = len([m for m in MOCK_DATA['maquinas'] if m['activo']])
    
    dashboard = {
        'resumen': {
            'total_componentes': total_componentes,
            'total_maquinas': total_maquinas,
            'total_proveedores': total_proveedores,
            'total_compras': total_compras,
            'compras_pendientes': compras_pendientes,
            'componentes_stock_bajo': componentes_stock_bajo,
            'valor_total_stock': valor_total_stock,
            'maquinas_activas': maquinas_activas
        },
        'graficos': {
            'stock_por_categoria': {
                'Motor': 15,
                'Transmision': 3,
                'Electrico': 8
            },
            'compras_por_estado': {
                'pendiente': compras_pendientes,
                'en_proceso': len([c for c in MOCK_DATA['compras'] if c['estado'] == 'en_proceso']),
                'completada': len([c for c in MOCK_DATA['compras'] if c['estado'] == 'completada']),
                'cancelada': len([c for c in MOCK_DATA['compras'] if c['estado'] == 'cancelada'])
            },
            'compras_ultimo_mes': {
                'labels': ['Semana 1', 'Semana 2', 'Semana 3', 'Semana 4'],
                'valores': [1, 1, 1, 0]
            }
        },
        'alertas': []
    }
    
    # Generar alertas dinámicas
    for componente in MOCK_DATA['componentes']:
        if componente['stock_actual'] <= componente['stock_minimo']:
            dashboard['alertas'].append({
                'tipo': 'warning',
                'mensaje': f"{componente['nombre']} tiene stock bajo ({componente['stock_actual']} unidades)",
                'timestamp': datetime.now().isoformat(),
                'componente_id': componente['id']
            })
    
    return jsonify({
        'success': True,
        'data': dashboard,
        'message': 'Dashboard obtenido exitosamente'
    })

@app.route('/api/v1/estadisticas/metricas', methods=['GET'])
def get_metricas():
    """Obtener métricas generales"""
    total_componentes = len(MOCK_DATA['componentes'])
    total_maquinas = len(MOCK_DATA['maquinas'])
    total_compras = len(MOCK_DATA['compras'])
    valor_total_stock = sum(s['valor_total'] for s in MOCK_DATA['stock'])
    
    return jsonify({
        'success': True,
        'data': {
            'totalComponentes': total_componentes,
            'totalMaquinas': total_maquinas,
            'totalCompras': total_compras,
            'valorTotalStock': valor_total_stock
        }
    })

@app.route('/api/v1/estadisticas/graficos', methods=['GET'])
def get_graficos():
    """Obtener datos para gráficos"""
    return jsonify({
        'success': True,
        'data': {
            'comprasPorMes': [
                {'mes': 'Enero', 'cantidad': 5, 'valor': 1250},
                {'mes': 'Febrero', 'cantidad': 3, 'valor': 850},
                {'mes': 'Marzo', 'cantidad': 7, 'valor': 1800},
                {'mes': 'Abril', 'cantidad': 4, 'valor': 1100},
                {'mes': 'Mayo', 'cantidad': 6, 'valor': 1500},
                {'mes': 'Junio', 'cantidad': 2, 'valor': 600},
                {'mes': 'Julio', 'cantidad': 3, 'valor': 870}
            ],
            'componentesPorCategoria': [
                {'categoria': 'Motor', 'cantidad': 15, 'valor': 382.5},
                {'categoria': 'Transmision', 'cantidad': 3, 'valor': 255},
                {'categoria': 'Electrico', 'cantidad': 8, 'valor': 1440}
            ],
            'stockPorProveedor': [
                {'proveedor': 'Repuestos del Campo SA', 'valor': 1077.5},
                {'proveedor': 'Transmisiones del Sur', 'valor': 255},
                {'proveedor': 'ElectroAgro SRL', 'valor': 1440}
            ]
        }
    })

@app.route('/api/v1/estadisticas/generales', methods=['GET'])
def get_estadisticas_generales():
    """Obtener estadísticas generales"""
    return jsonify({
        'success': True,
        'data': {
            'resumen': {
                'total_componentes': len(MOCK_DATA['componentes']),
                'total_maquinas': len(MOCK_DATA['maquinas']),
                'total_proveedores': len(MOCK_DATA['proveedores']),
                'valor_inventario': sum(s['valor_total'] for s in MOCK_DATA['stock'])
            }
        }
    })

@app.route('/api/v1/estadisticas/movimientos-recientes', methods=['GET'])
def get_movimientos_recientes():
    """Obtener movimientos recientes de stock"""
    return jsonify({
        'success': True,
        'data': [
            {
                'id': 1,
                'componente': 'Filtro de Aceite',
                'tipo': 'entrada',
                'cantidad': 10,
                'fecha': '2024-07-29T10:00:00',
                'observacion': 'Compra regular'
            },
            {
                'id': 2,
                'componente': 'Correa Dentada',
                'tipo': 'salida',
                'cantidad': 2,
                'fecha': '2024-07-28T15:30:00',
                'observacion': 'Instalación en tractor'
            }
        ]
    })

@app.route('/api/v1/estadisticas/graficos-stock', methods=['GET'])
def get_graficos_stock():
    """Obtener gráficos específicos de stock"""
    return jsonify({
        'success': True,
        'data': {
            'stock_por_categoria': {
                'Motor': 15,
                'Transmision': 3,
                'Electrico': 8
            },
            'rotacion_stock': [
                {'componente': 'Filtro de Aceite', 'rotacion': 85},
                {'componente': 'Correa Dentada', 'rotacion': 60},
                {'componente': 'Batería 12V', 'rotacion': 40}
            ]
        }
    })

# ================== API STOCK ADICIONAL ==================

@app.route('/api/v1/stock/resumen', methods=['GET'])
def get_stock_resumen():
    """Obtener resumen de stock"""
    total_componentes = len(MOCK_DATA['componentes'])
    componentes_stock_bajo = len([c for c in MOCK_DATA['componentes'] if c['stock_actual'] <= c['stock_minimo']])
    valor_total = sum(s['valor_total'] for s in MOCK_DATA['stock'])
    
    return jsonify({
        'success': True,
        'data': {
            'total_componentes': total_componentes,
            'componentes_stock_bajo': componentes_stock_bajo,
            'valor_total_stock': valor_total,
            'ultimo_movimiento': '2024-07-30T14:20:00'
        }
    })

@app.route('/api/v1/stock/bajo-stock', methods=['GET'])
def get_bajo_stock():
    """Obtener componentes con stock bajo"""
    componentes_bajo = [c for c in MOCK_DATA['componentes'] if c['stock_actual'] <= c['stock_minimo']]
    return jsonify({
        'success': True,
        'data': componentes_bajo,
        'total': len(componentes_bajo)
    })

@app.route('/api/v1/stock/movimiento', methods=['POST'])
def registrar_movimiento_stock():
    """Registrar movimiento de stock"""
    data = request.get_json()
    
    # Simular registro de movimiento
    nuevo_movimiento = {
        'id': len(MOCK_DATA['stock']) + 1,
        'componente_id': data.get('componente_id'),
        'tipo_movimiento': data.get('tipo'),
        'cantidad': data.get('cantidad'),
        'observacion': data.get('observacion', ''),
        'fecha': datetime.now().isoformat()
    }
    
    return jsonify({
        'success': True,
        'data': nuevo_movimiento,
        'message': 'Movimiento registrado exitosamente'
    })

# ================== API PAGOS ==================

@app.route('/api/v1/pagos/resumen', methods=['GET'])
def get_pagos_resumen():
    """Obtener resumen de pagos"""
    return jsonify({
        'success': True,
        'data': {
            'total_pendiente': 1250.00,
            'total_pagado_mes': 2100.00,
            'pagos_vencidos': 1,
            'proximos_vencimientos': 2
        }
    })

@app.route('/api/v1/estadisticas/resumen-general', methods=['GET'])
def get_resumen_general():
    """Obtener resumen general de estadísticas"""
    return jsonify({
        'success': True,
        'data': {
            'totalComponentes': len(MOCK_DATA['componentes']),
            'totalMaquinas': len(MOCK_DATA['maquinas']),
            'totalCompras': len(MOCK_DATA['compras']),
            'valorInventario': sum(s['valor_total'] for s in MOCK_DATA['stock']),
            'ventasUltimoMes': 15420.00,
            'crecimientoMensual': 12.5,
            'componentesVendidos': 45,
            'alertasActivas': 3
        }
    })

@app.route('/api/v1/estadisticas/compras-periodo', methods=['GET'])
def get_compras_periodo():
    """Obtener estadísticas de compras por período"""
    periodo = request.args.get('periodo', 'mes')
    
    if periodo == 'semana':
        data = {
            'totalCompras': 3,
            'montoTotal': 750.00,
            'compraPromedio': 250.00,
            'crecimiento': 15.2
        }
    elif periodo == 'mes':
        data = {
            'totalCompras': 12,
            'montoTotal': 3200.00,
            'compraPromedio': 266.67,
            'crecimiento': 8.5
        }
    else:  # año
        data = {
            'totalCompras': 148,
            'montoTotal': 38500.00,
            'compraPromedio': 260.14,
            'crecimiento': 22.3
        }
    
    return jsonify({
        'success': True,
        'data': data
    })

@app.route('/api/v1/estadisticas/stock-critico', methods=['GET'])
def get_stock_critico():
    """Obtener componentes con stock crítico"""
    componentes_criticos = [c for c in MOCK_DATA['componentes'] if c['stock_actual'] <= c['stock_minimo']]
    return jsonify({
        'success': True,
        'data': componentes_criticos
    })

@app.route('/api/v1/estadisticas/alertas', methods=['GET'])
def get_alertas():
    """Obtener alertas del sistema"""
    alertas = []
    
    # Generar alertas de stock bajo
    for componente in MOCK_DATA['componentes']:
        if componente['stock_actual'] <= componente['stock_minimo']:
            alertas.append({
                'id': len(alertas) + 1,
                'tipo': 'stock_bajo',
                'prioridad': 'alta' if componente['stock_actual'] == 0 else 'media',
                'titulo': f'Stock bajo: {componente["nombre"]}',
                'descripcion': f'Solo quedan {componente["stock_actual"]} unidades',
                'fecha': datetime.now().isoformat(),
                'leida': False
            })
    
    # Agregar algunas alertas adicionales
    alertas.extend([
        {
            'id': len(alertas) + 1,
            'tipo': 'pago_vencido',
            'prioridad': 'alta',
            'titulo': 'Pago vencido',
            'descripcion': 'Factura #1002 está vencida desde hace 5 días',
            'fecha': datetime.now().isoformat(),
            'leida': False
        },
        {
            'id': len(alertas) + 2,
            'tipo': 'mantenimiento',
            'prioridad': 'media',
            'titulo': 'Mantenimiento programado',
            'descripcion': 'Tractor John Deere requiere mantenimiento en 3 días',
            'fecha': datetime.now().isoformat(),
            'leida': False
        }
    ])
    
    return jsonify({
        'success': True,
        'data': alertas
    })

@app.route('/api/v1/estadisticas/top-proveedores', methods=['GET'])
def get_top_proveedores():
    """Obtener los mejores proveedores por período"""
    periodo = request.args.get('periodo', 'mes')
    
    proveedores = [
        {
            'id': 1,
            'nombre': 'Repuestos del Campo SA',
            'totalCompras': 8,
            'montoTotal': 2150.00,
            'promedio': 268.75,
            'crecimiento': 15.2
        },
        {
            'id': 2,
            'nombre': 'Transmisiones del Sur',
            'totalCompras': 3,
            'montoTotal': 850.00,
            'promedio': 283.33,
            'crecimiento': -5.1
        },
        {
            'id': 3,
            'nombre': 'ElectroAgro SRL',
            'totalCompras': 5,
            'montoTotal': 1200.00,
            'promedio': 240.00,
            'crecimiento': 22.8
        }
    ]
    
    return jsonify({
        'success': True,
        'data': proveedores
    })

@app.route('/api/v1/estadisticas/compras', methods=['GET'])
def get_estadisticas_compras():
    """Obtener estadísticas de compras con filtros"""
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    return jsonify({
        'success': True,
        'data': {
            'totalGastado': 3200.00,
            'cantidadCompras': 12,
            'promedioPorCompra': 266.67,
            'comprasPorMes': [
                {'mes': 'Enero', 'cantidad': 5, 'valor': 1250},
                {'mes': 'Febrero', 'cantidad': 3, 'valor': 850},
                {'mes': 'Marzo', 'cantidad': 4, 'valor': 1100}
            ]
        }
    })

if __name__ == '__main__':
    print("🌾 Sistema de Gestión Agrícola - Backend Principal")
    print("=" * 60)
    print("🚀 Servidor iniciado en: http://127.0.0.1:5000/")
    print("✅ Estado: OPERATIVO")
    print("📊 Base de datos: Mock Data (Simulada)")
    print("🔗 CORS: Habilitado para frontend")
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
