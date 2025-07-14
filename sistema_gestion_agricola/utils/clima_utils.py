# utils/clima_utils.py
import requests
from flask import current_app

def obtener_datos_clima():
    try:
        api_key = current_app.config['WEATHER_API_KEY']
        current_app.logger.info(f"API Key usada: {api_key}")  # Para verificar que se lee
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                'lat': current_app.config['COORDENADAS_UCACHA']['lat'],
                'lon': current_app.config['COORDENADAS_UCACHA']['lon'],
                'appid': api_key,
                'units': 'metric',
                'lang': 'es'
            },
            timeout=5
        )
        response.raise_for_status()
        data = response.json()

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
        current_app.logger.error(f"Error al obtener datos del clima: {str(e)}")
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
