""" This module contains the client code to fetch weather data from OpenWeatherMap API. """

import requests
import yaml


ENDPOINT = "https://api.openweathermap.org/data/2.5/weather" #endpoint

def load_yaml(path: str) -> dict:
    """ Load a YAML file and return its contents as a dictionary. 
        This is to load secrets and config files."""
    with open(path, 'r') as f:
        return yaml.safe_load(f)
    
def fetch_weather(city: str, api_key: str, units: str) -> dict:
    """ Fetch weather data for a given city using OpenWeatherMap API"""
    params = {
        'q': city,
        'appid': api_key,
        'units': units
    }
    response = requests.get(ENDPOINT, params=params)
    response.raise_for_status()
    return response.json()

