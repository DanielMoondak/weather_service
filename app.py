import logging
from flask import Flask, jsonify, render_template, send_from_directory
import requests
import os

app = Flask(__name__, static_folder='bg-clima')
app.config['DEBUG'] = True  # Habilitar el modo de depuración
app.logger.setLevel(logging.DEBUG)  # Establecer el nivel de registro a DEBUG

@app.route('/', methods=['GET'])
def home():
    return "El servidor está funcionando correctamente"

@app.route('/weather', methods=['GET'])
def get_weather():
    api_key = os.getenv('OPENWEATHER_API_KEY', 'a62194b9c38c403f56fac7676217dcce')
    city = 'Mexico City'
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=es'

    try:
        response = requests.get(url)
        response.raise_for_status()  # Esto lanzará una excepción para códigos de estado 4xx/5xx
        data = response.json()

        # Obtener la descripción del clima para elegir la imagen de fondo
        weather_description = data['weather'][0]['description'].lower()

        # Mapear la descripción del clima a una imagen de fondo apropiada
        backgrounds = {
            'cielo claro': 'clear_sky.jpg',
            'algo de nubes': 'partly_cloudy.jpg',
            'nubes': 'nubes.jpg',
            'nubes dispersas': 'scattered_clouds.jpg',
            'nublado': 'cloudy.jpg',
            'muy nuboso' : 'very_cloudy.jpg',
            'lluvia ligera': 'light_rain.jpg',
            'lluvia': 'rain.jpg',
            'tormenta eléctrica': 'thunderstorm.jpg',
            'nieve': 'snow.jpg',
            'niebla': 'fog.jpg',
            'humo': 'smoke.jpg',
            'volcánico': 'volcanic.jpg',
            'tornado': 'tornado.jpg',
        }

        # Obtener la URL de la imagen de fondo según la descripción del clima
        background_url = backgrounds.get(weather_description, 'default_background.jpg')

        # Datos del clima para pasar al template
        weather = {
            'city': data['name'],
            'temperature': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'description': data['weather'][0]['description'],
            'wind_speed': data['wind']['speed'],
            'wind_deg': data['wind'].get('deg', 'N/A'),
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure']
        }

        return render_template('weather.html', weather=weather, background_url=background_url)

    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'No se pudo obtener el clima', 'message': str(e)}), 500

@app.route('/bg-clima/<path:filename>')
def custom_static(filename):
    return send_from_directory('bg-clima', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
    # app.run(host='0.0.0.0', port=5000)
