from client import fetch_weather, load_yaml

def run_pipeline():
    secrets = load_yaml('config/secrets.yaml')
    config = load_yaml('config/config.yaml')

    api_key = secrets['openweather_api_key']
    units = config['units']

    for city in config['cities']:
        data = fetch_weather(city, api_key, units)
        print(city)
        print("Temperature:", data['main']['temp'])
        print("Weather:", data['weather'][0]['description'])
        print("-------")
    