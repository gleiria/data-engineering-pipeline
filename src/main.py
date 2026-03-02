"""Entry point for the pipeline."""

import logging
from src.pipeline import run_pipeline

# configuring logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

logger.info("Starting weather pipeline...")
print("------------------------------")

if __name__ == "__main__":
    run_pipeline()

print("------------------------------")
logger.info("Pipeline finished.")