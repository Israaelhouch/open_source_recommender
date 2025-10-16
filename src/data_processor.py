import os
import pandas as pd
from datetime import datetime
from src.data.data_cleaner import save_data
from src.utils.logger import setup_logger
from datetime import datetime, timezone

logger = setup_logger("data_processing")

def load_data(file_path="data/raw/github_repos.csv"):
    """Load raw GitHub repo data"""
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None
    df = pd.read_csv(file_path)
    logger.info(f"Loaded {len(df)} repositories from {file_path}")
    return df

def clean_data(df):
    """Clean and normalize raw data"""
    df['description'] = df['description'].fillna('')
    df['language'] = df['language'].fillna('Unknown')
    df['stars'] = df['stars'].fillna(0).astype(int)
    df['updated_at'] = pd.to_datetime(df['updated_at'], errors='coerce')
    
    # Drop rows with invalid dates
    df = df.dropna(subset=['updated_at'])
    logger.info(f"After cleaning: {len(df)} valid repositories")
    return df

def extract_features(df):
    """Add derived features for recommender"""
    # Recency in days
    df['days_since_update'] = (datetime.now(timezone.utc) - df['updated_at']).dt.days 
    
    # Optional: Normalize stars (0-1)
    if len(df['stars']) > 0:
        df['stars_normalized'] = df['stars'] / df['stars'].max()
    else:
        df['stars_normalized'] = 0
    
    logger.info("Feature extraction complete: added 'days_since_update' and 'stars_normalized'")
    return df


def process_pipeline(input_file="data/raw/github_repos.csv"):
    df = load_data(input_file)
    if df is None:
        return
    df = clean_data(df)
    df = extract_features(df)
    save_data(df, filename="data/processed/processed_data.csv")

