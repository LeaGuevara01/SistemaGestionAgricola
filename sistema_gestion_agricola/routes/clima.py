# routes/clima.py
from flask import Blueprint, jsonify, current_app
from datetime import datetime
from ..utils.clima_utils import obtener_datos_clima
from ..cache_config import cache

clima_bp = Blueprint('clima', __name__, url_prefix='/api/clima')

@clima_bp.route('/')
@cache.cached(timeout=1800)
def api_clima():
    try:
        datos = obtener_datos_clima()
        if not datos:
            raise ValueError("Datos climáticos no disponibles")
        
        return jsonify({
            'status': 'success',
            'data': datos,
            'ultima_actualizacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'ubicacion': current_app.config['COORDENADAS_UCACHA'] # Coordenadas fijas de Ucacha
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'data': None
        }), 500
