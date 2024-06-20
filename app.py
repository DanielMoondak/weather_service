import logging
from flask import Flask, jsonify, render_template, send_from_directory
import requests
import os

app = Flask(__name__, static_folder='bg-clima')
app.config['DEBUG'] = True  # Habilitar el modo de depuración
app.logger.setLevel(logging.DEBUG)  # Establecer el nivel de registro a DEBUG

# Claves de API (puedes usar variables de entorno o configurarlas aquí directamente)
weather_api_key = os.getenv('WEATHER_API_KEY', '71ae90ac47ef4ede91a192818242006')
openweather_api_key = os.getenv('OPENWEATHER_API_KEY', 'a62194b9c38c403f56fac7676217dcce')

@app.route('/', methods=['GET'])
def home():
    return "El servidor está funcionando correctamente"

@app.route('/weather', methods=['GET'])
def get_weather():
    city = 'Mexico City'

    try:
        # Obtener datos del clima desde Weather API
        weather_url = f'http://api.weatherapi.com/v1/current.json?key={weather_api_key}&q={city}&lang=es'
        weather_response = requests.get(weather_url)
        weather_response.raise_for_status()
        weather_data = weather_response.json()

        # Obtener la descripción del clima para elegir la imagen de fondo
        weather_description = weather_data['current']['condition']['text'].lower()

        # Mapear la descripción del clima a una imagen de fondo apropiada
        backgrounds = {
            'despejado': 'clear_sky.jpg',
            'parcialmente nublado': 'partly_cloudy.jpg',
            'Parcialmente Nublado': 'partly_cloudy.jpg',
            'nublado': 'cloudy.jpg',
            'cielo cubierto': 'cloudy.jpg',
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

        # Datos del clima desde Weather API
        weather = {
            'city': weather_data['location']['name'],
            'temperature': weather_data['current']['temp_c'],
            'feels_like': weather_data['current']['feelslike_c'],
            'description': weather_data['current']['condition']['text'],
            'wind_speed': weather_data['current']['wind_kph'],
            'wind_deg': weather_data['current']['wind_dir'],
            'humidity': weather_data['current']['humidity'],
            'pressure': weather_data['current']['pressure_mb']
        }

        # Obtener el índice UV
        uv_index = weather_data['current']['uv']

    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'No se pudo obtener el clima desde WeatherAPI', 'message': str(e)}), 500

    # Obtener datos del clima desde OpenWeatherMap API
    openweather_url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={openweather_api_key}&units=metric&lang=es'
    try:
        openweather_response = requests.get(openweather_url)
        openweather_response.raise_for_status()
        openweather_data = openweather_response.json()

        # Datos del clima desde OpenWeatherMap API
        openweather = {
            'temperature': openweather_data['main']['temp'],
            'feels_like': openweather_data['main']['feels_like'],
            'description': openweather_data['weather'][0]['description'],
            'wind_speed': openweather_data['wind']['speed'],
            'wind_deg': openweather_data['wind'].get('deg', 'N/A'),
            'humidity': openweather_data['main']['humidity'],
            'pressure': openweather_data['main']['pressure']
        }

    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'No se pudo obtener el clima desde OpenWeatherMap', 'message': str(e)}), 500

    return render_template('weather.html', weather=weather, openweather=openweather, uv_index=uv_index, background_url=background_url)
   
@app.route('/bg-clima/<path:filename>')
def custom_static(filename):
    return send_from_directory('bg-clima', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
