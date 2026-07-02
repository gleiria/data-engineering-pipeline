"""this module defines the main function that orchestrates the data fetching and processing
making use of load_yaml() and fetch_weather() functions from client.py
"""

import logging
import pandas as pd
import os
from datetime import datetime
from src.client import fetch_weather, load_yaml
from azure.storage.blob import BlobServiceClient

# create module specific logger
logger = logging.getLogger(__name__)


def run_pipeline():
    """Orchestrate the weather data fetching and processing pipeline."""
    logger.info("Pipeline started")

    # Load configuration and api_key from secrets.yaml and config.yaml
    # secrets = load_yaml('config/secrets.yaml')
    config = load_yaml("config/config.yaml")
    # cloud run
    api_key = os.environ.get("OPENWEATHER_API_KEY")

    # local run
    if not api_key:
        secrets = load_yaml("config/secrets.yaml")
        api_key = secrets["openweather_api_key"]
    # units
    units = config["units"]

    # lissto for weather records
    weather_records = []

    # grab weather data for each city in config 
    for city in config["cities"]:
        try:
            data = fetch_weather(city, api_key, units)
            logger.info(f"{city}: {data['main']['temp']}°C")
            logger.info(f"{city}: {data['weather'][0]['description']}")
            logger.info(
                f"{city}: Observation time: {datetime.fromtimestamp(data['dt']).isoformat()}"
            )
            logger.info(f"{city}: Ingestion time: {datetime.now().isoformat()}")
            logger.info(f"{city}: Humidity: {data['main']['humidity']}%")
            logger.info(f"{city}: Pressure: {data['main']['pressure']} hPa")
            logger.info(f"{city}: Weather data fetched successfully")

            print("-----------------------------")

            # Create weather record with ingestionn time as well
            record = {
                "city": city,
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "description": data["weather"][0]["description"],
                "observation_time": datetime.fromtimestamp(data["dt"]).isoformat(),
                "ingestion_time": datetime.now().isoformat(),
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


    if weather_records:
        df = pd.DataFrame(weather_records)

        blob_connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
        container_name = os.environ.get("AZURE_CONTAINER_NAME", "weather-data")

        # ------- OPTION A: RUNNING IN AZURE -------
        if blob_connection_string:
            logger.info(
                "Azure connection string found, attempting to sync with Azure Blob Storage"
            )
            blob_service_client = BlobServiceClient.from_connection_string(
                blob_connection_string
            )
            blob_client = blob_service_client.get_blob_client(
                container=container_name, blob="weather_data.parquet"
            )

            # 1. Handle downloading and merging if old data exists
            if blob_client.exists():
                logger.info("Blob exists, downloading existing data for appending")
                with open("temp_weather_data.parquet", "wb") as f:
                    download_stream = blob_client.download_blob()
                    f.write(download_stream.readall())

                existing_df = pd.read_parquet("temp_weather_data.parquet")
                df = pd.concat([existing_df, df], ignore_index=True)
                logger.info(
                    f"Combined new data with existing data, total records: {len(df)}"
                )

            # 2. SAVE the combined dataframe to a local temp file
            df.to_parquet("temp_weather_data.parquet", engine="pyarrow", index=False)

            # 3. UPLOAD the file to Azure Blob Storage (This was missing!)
            with open("temp_weather_data.parquet", "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            logger.info(
                f"Successfully uploaded {len(df)} total records to Azure Blob Storage."
            )

            # Clean up the temp file inside the container
            if os.path.exists("temp_weather_data.parquet"):
                os.remove("temp_weather_data.parquet")

        # ------- OPTION B: RUNNING LOCALLY -------
        else:
            logger.info("No Azure connection string found, saving data locally")
            output_dir = "data"
            os.makedirs(output_dir, exist_ok=True)
            filename = os.path.join(output_dir, "weather_data.parquet")

            if os.path.exists(filename):
                existing_df = pd.read_parquet(filename)
                df = pd.concat([existing_df, df], ignore_index=True)

            df.to_parquet(filename, engine="pyarrow", index=False)
            logger.info(f"Saved {len(df)} records locally to {filename}")

    # This else goes with "if weather_records:" 
    else:
        logger.warning("No weather data collected.")
