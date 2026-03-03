FROM python:3.12-slim

# setting working directory
WORKDIR /app

# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy source code and config files
COPY src ./src
COPY config ./config

# create data directory for storing results
RUN mkdir -p data

# run the application
CMD ["python", "-m", "src.main"]