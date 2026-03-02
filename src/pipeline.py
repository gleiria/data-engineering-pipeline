"""this module defines the main function that orchestrates the data fetching and processing
making use of of load_yaml() and fetch_weather() functions from client.py
"""
import logging
import pandas as pd
import os
from datetime import datetime
from client import fetch_weather, load_yaml


logger = logging.getLogger(__name__)

def run_pipeline():
    """Orchestrate the weather data fetching and processing pipeline."""
    logger.info("Pipeline started")
    
    # Load configuration and secrets
    secrets = load_yaml('config/secrets.yaml')
    config = load_yaml('config/config.yaml')

    api_key = secrets['openweather_api_key']
    units = config['units']

    # list to hold weather records
    weather_records = []

    # Fetch weather data for each configured city
    for city in config['cities']:
        try:
            data = fetch_weather(city, api_key, units)
            logger.info(f"{city}: {data['main']['temp']}°C")
            logger.info(f"{city}: {data['weather'][0]['description']}")
            print("-----------------------------")

            # Create weather record with timestamp
            record = {
                'city': city,
                'temperature': data['main']['temp'],
                'description': data['weather'][0]['description'],
                "timestamp": datetime.now().isoformat()
            }
            weather_records.append(record)
            logger.info(f"Record for {city} added to weather_records")
        except Exception as e:
            logger.error(f"Error fetching weather for {city}: {e}")
            continue

    logger.info("Pipeline finished")
    
    # Save collected weather data to parquet file
    if weather_records:
        # Convert records to DataFrame
        df = pd.DataFrame(weather_records)

        # Create output directory and define file path
        output_dir = 'data'
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(output_dir, 'weather_data.parquet')

        # Append to existing data if file exists, otherwise create new file
        if os.path.exists(filename):
            existing_df = pd.read_parquet(filename)
            df = pd.concat([existing_df, df], ignore_index=True)
        df.to_parquet(filename, engine='pyarrow', index=False)
        logger.info(f"Saved {len(df)} records to {filename}")
    else:
        logger.warning("No weather data collected.")

      

    