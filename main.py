# main.py
import os
import pandas as pd
from src.api.github_client import fetch_repositories
from src.data.data_cleaner import save_raw_data
from src.utils.logger import setup_logger

logger = setup_logger("main")

def main():
    logger.info("=== Starting GitHub Data Collection ===")

    # Fetch repositories
    repos = fetch_repositories()

    # Save to CSV
    file_path = save_raw_data(repos)
    logger.info(f"Saved {len(repos)} unique repositories in :{file_path}")
    logger.info("=== GitHub Data Collection Completed ===")

if __name__ == "__main__":
    main()
