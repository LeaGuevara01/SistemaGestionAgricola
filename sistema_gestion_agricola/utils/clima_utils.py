# utils/clima_utils.py
import requests
from flask import current_app

def obtener_datos_clima(coords=None):
    try:
        api_key = current_app.config.get('WEATHER_API_KEY')
        weather_url = current_app.config.get('WEATHER_API_URL')

        if not api_key:
            raise RuntimeError("WEATHER_API_KEY no configurada")
        if not weather_url:
            raise RuntimeError("WEATHER_API_URL no configurada")

        if coords is None:
            coords = (
                current_app.config['COORDENADAS_UCACHA']['lat'],
                current_app.config['COORDENADAS_UCACHA']['lon']
            )

        lat, lon = coords

        current_app.logger.info(f"[CLIMA] Consultando clima para lat={lat}, lon={lon}")

        response = requests.get(
            weather_url,
            params={
                'lat': lat,
                'lon': lon,
                'appid': api_key,
                'units': 'metric',
                'lang': 'es'
            },
            timeout=5
        )

        response.raise_for_status()  # Lanza HTTPError si status != 200
        data = response.json()

        current_app.logger.info(f"[CLIMA] Respuesta API: {data}")

        return {
            'temperatura': round(data['main']['temp']),
            'sensacion_termica': round(data['main']['feels_like']),
            'condicion': data['weather'][0]['description'].capitalize(),
            'icono': mapear_icono_clima(data['weather'][0]['id']),
            'humedad': data['main']['humidity'],
            'viento_kmh': round(data['wind']['speed'] * 3.6),
            'presion': data['main']['pressure'],
            'visibilidad_km': round(data.get('visibility', 0) / 1000, 1)
        }

    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"[CLIMA] Error al obtener datos: {str(e)}")
        return None

    except Exception as e:
        current_app.logger.error(f"[CLIMA] Error inesperado: {str(e)}")
        return None
    
def mapear_icono_clima(weather_id):
    iconos = {
        range(200, 300): "bi-lightning",
        range(300, 400): "bi-cloud-drizzle",
        range(500, 600): "bi-cloud-rain",
        range(600, 700): "bi-snow2",
        range(700, 800): "bi-cloud-fog",
        800: "bi-sun",
        range(801, 805): "bi-cloud-sun"
    }
    
    for key, icon in iconos.items():
        if isinstance(key, range) and weather_id in key:
            return icon
        elif weather_id == key:
            return icon
    return "bi-question-circle"
