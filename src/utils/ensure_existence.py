import os
from src.scripts.data_refresher import data_refresher_pipeline
from src.utils.logger import setup_logger
logger = setup_logger("helpers")

def ensure_data_exists(persist_dir="data/embeddings/chroma"):
    """Check if Chroma data exists; refresh if not."""
    if not os.path.exists(persist_dir) or not os.listdir(persist_dir):
        logger.warning("No Chroma data found. Running data refresh pipeline...")
        data_refresher_pipeline()
    else:
        logger.info("Chroma data found. Proceeding with recommendations.")
