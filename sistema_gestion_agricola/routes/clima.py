# routes/clima.py
from flask import Blueprint, jsonify, current_app, request
from datetime import datetime
from ..utils.clima_utils import obtener_datos_clima
from ..cache_config import cache

clima_bp = Blueprint('clima', __name__, url_prefix='/api/clima')

@clima_bp.route('/')
@cache.cached(timeout=1800)  # Cache 30 minutos para ubicación fija
def api_clima_default():
    try:
        coords = current_app.config.get('COORDENADAS_UCACHA')
        if not coords or 'lat' not in coords or 'lon' not in coords:
            raise ValueError("Coordenadas por defecto mal configuradas")
        
        # Convertir a tupla de coordenadas
        coordenadas = (coords['lat'], coords['lon'])
        datos = obtener_datos_clima(coordenadas)
        if not datos:
            raise ValueError("Datos climáticos no disponibles")

        respuesta = {
            'status': 'success',
            'data': datos,
            'ultima_actualizacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'ubicacion': coords
        }
        return jsonify(respuesta)
    
    except Exception as e:
        current_app.logger.error(f"Error en API clima: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e), 'data': None}), 500

@clima_bp.route('/buscar')
@cache.cached(timeout=1800, query_string=True)  # Cache según parámetros de query
def api_clima_buscar():
    try:
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)

        if lat is None or lon is None:
            return jsonify({'status': 'error', 'message': 'Parámetros lat y lon son obligatorios', 'data': None}), 400

        coords = (lat, lon)
        datos = obtener_datos_clima(coords)
        if not datos:
            raise ValueError("Datos climáticos no disponibles para la ubicación")

        respuesta = {
            'status': 'success',
            'data': datos,
            'ultima_actualizacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'ubicacion': coords
        }
        return jsonify(respuesta)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e), 'data': None}), 500

from flask import jsonify

@clima_bp.errorhandler(404)
def handle_404(error):
    return jsonify({'status': 'error', 'message': 'Recurso no encontrado', 'data': None}), 404

@clima_bp.errorhandler(500)
def handle_500(error):
    return jsonify({'status': 'error', 'message': 'Error interno del servidor', 'data': None}), 500
