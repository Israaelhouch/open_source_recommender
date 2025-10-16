from src.github_repos_fetcher import fetch_repositories
from src.data.data_cleaner import save_data
from src.data_processor import process_pipeline
from src.utils.logger import setup_logger

logger = setup_logger("main")

def main():
    logger.info("=== Starting GitHub Data Collection ===")

    # Fetch repositories
    repos = fetch_repositories()

    # Save to CSV
    raw_data_path = save_data(repos, filename="data/raw/github_repos.csv")
    logger.info(f"Saved {len(repos)} unique repositories in :{raw_data_path}")
    logger.info("=== GitHub Data Collection Completed ===")

    logger.info("=== Starting Data Processing Pipeline ===")
    process_pipeline()
    logger.info("=== Data Processing Pipeline Completed ===")
if __name__ == "__main__":
    main()
