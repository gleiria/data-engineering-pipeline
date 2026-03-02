"""Entry point for the pipeline."""

import logging
from pipeline import run_pipeline

# configuring logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

logger.info("Starting weather pipeline...")

if __name__ == "__main__":
    run_pipeline()

logger.info("Pipeline finished.")