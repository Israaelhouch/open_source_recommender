import pandas as pd
import os
from src.utils.logger import setup_logger

logger = setup_logger("data_saver")

def save_data(df, filename="data/raw/github_repos.csv"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    df = pd.DataFrame(df)
    df.to_csv(filename, index=False)
    logger.info(f"Saved processed data in: {filename}")
    
    return filename
