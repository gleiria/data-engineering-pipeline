"""this module defines the main function that orchestrates the data fetching and processing
making use of of load_yaml() and fetch_weather() functions from client.py
"""
import logging
import pandas as pd
import os
from datetime import datetime
from src.client import fetch_weather, load_yaml

#create module specific logger
logger = logging.getLogger(__name__)

def run_pipeline():
    """Orchestrate the weather data fetching and processing pipeline."""
    logger.info("Pipeline started")
    
    # Load configuration and api_key from secrets.yaml and config.yaml
    secrets = load_yaml('config/secrets.yaml')
    config = load_yaml('config/config.yaml')
    #api_key
    api_key = secrets['openweather_api_key']
    #units
    units = config['units']

    # lissto for weather records
    weather_records = []

    # grab weather data for each city in config 
    for city in config['cities']:
        try:
            data = fetch_weather(city, api_key, units)
            logger.info(f"{city}: {data['main']['temp']}°C")
            logger.info(f"{city}: {data['weather'][0]['description']}")
            logger.info(f"{city}: Observation time: {datetime.fromtimestamp(data['dt']).isoformat()}")
            logger.info(f"{city}: Ingestion time: {datetime.now().isoformat()}")
            logger.info(f"{city}: Humidity: {data['main']['humidity']}%")
            logger.info(f"{city}: Pressure: {data['main']['pressure']} hPa")
            logger.info(f"{city}: Weather data fetched successfully")

            print("-----------------------------")

            # Create weather record with ingestionn time as well
            record = {
                'city': city,
                "temperature": data['main']['temp'],
                "humidity": data['main']['humidity'],
                "pressure": data['main']['pressure'],
                "description": data['weather'][0]['description'],
                "observation_time": datetime.fromtimestamp(data["dt"]).isoformat(),
                "ingestion_time": datetime.now().isoformat()
            }
            # Append record to list
            weather_records.append(record)
            logger.info(f"Record for {city} added to weather_records")
        # catch and log any errors during fetching
        except Exception as e:
            logger.error(f"Error fetching weather for {city}: {e}")
            continue

    logger.info("Pipeline finished")

    # --------- Store data in parquet file -----------

    #if list not empty
    if weather_records:
        # each dicrtionary in the list becomes a row in the dataframe, keys become column names
        df = pd.DataFrame(weather_records)

        # define outout dir
        output_dir = 'data'
        # if it doesn't exist, create
        os.makedirs(output_dir, exist_ok=True)
        # full file path
        filename = os.path.join(output_dir, 'weather_data.parquet')

        # ------- Append instead of overwriting -------
        # check if file exists, if yes, read existing data and concatenate with new data, then save
        if os.path.exists(filename):
            existing_df = pd.read_parquet(filename)
            # combine vertically
            df = pd.concat([existing_df, df], ignore_index=True)
        # save combined df to parquet with pyarrow
        df.to_parquet(filename, engine='pyarrow', index=False)
        logger.info(f"Saved {len(df)} records to {filename}")
    else:
        # warning if list is empty -> no data collected
        logger.warning("No weather data collected.")

      

    