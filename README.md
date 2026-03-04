# Data Engineering Pipeline
---
## Overview
This project implements a Dockerised Python data pipeline that collects weather data from the OpenWeather public API and stores it in Parquet format for downstream analytical use.

**The pipeline:**

* Fetches weather data for a configurable list of cities
* Extracts structured analytical fields
* Stores results as a Parquet dataset
* Logs execution events
* Runs reproducibly inside Docker

---

## Architecture

**Project File Structure**

```
weather_pipeline/
│
├── config/
│   ├── config.yaml
│   ├── secrets_example.yaml
│   └── secrets.yaml (not committed)
│
├── data/
│
├── src/
│   ├── client.py
│   ├── pipeline.py
│   └── main.py
│
├── tests/
├── Dockerfile
├── requirements.txt
└── README.md 
```

## Component Responsibilities

`client.py`
* Handles communication with the external API
* Loads YAML configuration
* Returns structured JSON responses

`pipeline.py`

* Orchestrates the pipeline workflow
* Loads configuration and secrets
* Fetches data for each configured city
* Transforms JSNON responses into tabular format
* Persists results as Parquet

`main.py`

* Application entry point
* Configures logging
* Starts pipeline execution
 ---
## Data Model

**The pipeline extracts the folowing fields:**

| Field            | Source                | Description                  |
| ---------------- | --------------------- | ---------------------------- |
| city             | `name`                | City name                    |
| temperature      | `main.temp`           | Temperature (°C when metric) |
| humidity         | `main.humidity`       | Humidity (%)                 |
| pressure         | `main.pressure`       | Atmospheric pressure (hPa)   |
| description      | `weather.description` | Weather condition            |
| observation_time | `dt`                  | API event timestamp          |
| ingestion_time   | pipeline              | Timestamp when stored        |

---

## Design Decisions

1. Modular architecture. Clear separation of concerns to improve maintainability and testing.

    * API communication
    * Orchestration
    * Entry point

2. Configuration driven design
    * Cities and units defined in:
    ```config/config.yaml```

3. Secrets management
    * API keys stored in:
    ```config/secrets.yaml``` file added to .gitignore
    * template provided:
    ```config/secrets_example.yaml```

4. Parquet for storage
    * Preserves data types (float, datetime)
    * Optimised for analytics workloads
    * Efficient for columnar queries

5. Dockerised execution
    * Reproducibility
    * Dependency isolation
    * Easy to execute

    Data persistence is handled via Docker Volumes. Folder in host file system is mounted into the virtual file system of Docker:
    ``` bash
        docker run \
        -v $(pwd)/config:/app/config \
        -v $(pwd)/data:/app/data \
        weather-pipeline
    ```
6. Logging 
    * Execution visibility
    * Structured operational output 
    * Error and warning reporting

7. Resilience and fault tolerance
    * Per-city try/except isolation to ensure failure for one city does not stop pipeline

8. Testing
    * Unit tests to validate:
        * YAML loading
        * API client behavior 

9. Continuous Integration

    * I did setup a minimal GitHub Actions workflow that runs tests on every push to dev_branch on remote.

    Minimal workflow:

    1. Develop locally on dev_branch
    2. Commit and push changes
    3. CI runs unit tests automatically
    4. Merge into main only after tests pass
    5. Sync local main
    6. Continue development on dev_branch

---

## Assumptions and Consumer Centric Design

Assignment instructions state that the primary consumers are Data Scientists performing hypothesis testing. The following assumptions guided some of my implementation decisions.

1. Structured, typed data. Parquet guarantees schema integrity and immediate analytical usability:
    ```python
    import pandas as pd
    df = pd.read_parquet("data/weather_data.parquet")
    ```

2. Historical data required for hypothesis testing. The pipeline appends data rather than overwriting.

3. Event time vs ingestion time integrated to support:
    * Latency analysis
    * Pipeline failures
    * Important to know when event occured vs when the system processed it

4. Data Volume is moderate
    * The list of records approach assumes a configurable but reasonably bounded number of cities
    * Keeps solution simple and sufficient for expected scale

5. Reliability prioritised over infrastructure complexity
    * I aimed for a solution aligned with some production patterns wihtout overengineering infrastructure or unnecessary services

## How to run

1. Clone Repository
```bash
git clone https://github.com/gleiria/data-engineering-pipeline.git
cd data-engineering-pipeline
```

2. Create secrets file
```bash
cp config/secrets_example.yaml config/secrets.yaml
```
edit:
```YAML
openweather_api_key: "YOUR_API_KEY"
```
Obtain a free key from: https://openweathermap.org/

3. Build Docker image
```bash
docker build -t weather-pipeline .
```

4. Run pipeline
```bash
docker run \
-v $(pwd)/config:/app/config \
-v $(pwd)/data:/app/data \
weather-pipeline
```
----

## Output
Data stored in:
```bash
data/weather_data.parquet
```

Inspect with:

```python
import pandas as pd
df = pd.read_parquet("data/weather_data.parquet")
print(df.head())
```




    

