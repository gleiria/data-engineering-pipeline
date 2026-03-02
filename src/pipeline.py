"""this module defines the main function that orchestrates the data fetching and processing
making use of of load_yaml() and fetch_weather() functions from client.py
"""

from client import fetch_weather, load_yaml

def run_pipeline():
    secrets = load_yaml('config/secrets.yaml')
    config = load_yaml('config/config.yaml')

    api_key = secrets['openweather_api_key']
    units = config['units']

    for city in config['cities']:
        try:
            data = fetch_weather(city, api_key, units)
              # just checking for now
            print(city)
            print("Temperature:", data['main']['temp'])
            print("Weather:", data['weather'][0]['description'])
            print("-------")
        except Exception as e:
            print(f"Error fetching weather for {city}: {e}")
            continue
      

# to add: 
# 1) explicit error handling (file existence, key, network),
# 2) logging instead of print
# 3) saving data to parquet file

    