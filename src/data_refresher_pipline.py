from datetime import datetime
from src.github_repos_fetcher import fetch_repositories
from src.data_processing_pipline import process_pipeline
from src.embedder import Embedder
from src.chroma_store import ChromaStore
from src.utils.logger import setup_logger
import time

logger = setup_logger("data_refresher")

def data_refresher_pipeline(topics=None, languages=None, max_repos=None):
    """Fetch → preprocess → embed → refresh vector store"""
    start_time = time.time()
    logger.info("Starting GitHub Data Collection and Vector Store Refresh")

    try:
        repos = fetch_repositories(topics=topics, languages=languages, max_repos=max_repos)
        if repos.empty:
            logger.warning("No repositories fetched. Skipping update.")
            return

        repos_df = process_pipeline(repos)

        embedder = Embedder()
        embeddings = embedder.generate_embeddings(repos_df['combined_text'].tolist())

        store = ChromaStore()
        store.reset_collection()
        store.add_documents(repos_df, embeddings)

    except Exception as e:
        logger.exception(f"Pipeline failed: {e}")

    finally:
        duration = round(time.time() - start_time, 2)
        logger.info(f"Pipeline completed in {duration}s at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

