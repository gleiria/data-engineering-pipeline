""" This module contains the client code to fetch weather data from OpenWeatherMap API. """

import requests
import yaml


ENDPOINT = "https://api.openweathermap.org/data/2.5/weather" 

def load_yaml(path: str) -> dict:
    """Parse content of yaml and return as dict"""
    with open(path, 'r') as f:
        return yaml.safe_load(f)
    
def fetch_weather(city: str, api_key: str, units: str) -> dict:
    """Fetch weather data for a given city using OpenWeatherMap API"""
    params = {
        'q': city,
        'appid': api_key,
        'units': units
    }
    # GET request
    response = requests.get(ENDPOINT, params=params)
    # check success or rise error
    response.raise_for_status()
    # if successful, return json 
    return response.json()

