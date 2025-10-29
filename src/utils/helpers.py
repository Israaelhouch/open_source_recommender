import os
import pandas as pd
from datetime import datetime
from datetime import datetime, timezone
from src.utils.logger import setup_logger


logger = setup_logger("helpers")

def save_data(df, filename="data/raw/github_repos.csv"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    df = pd.DataFrame(df)
    df.to_csv(filename, index=False)
    logger.info(f"Saved processed data in: {filename}")
    
    return filename

def clean_data(df):
    """Clean and normalize raw data"""
    df['description'] = df['description'].fillna('')
    df['language'] = df['language'].fillna('Unknown')
    df['stars'] = df['stars'].fillna(0).astype(int)
    df['updated_at'] = pd.to_datetime(df['updated_at'], errors='coerce')

    df = df.dropna(subset=['updated_at'])
    logger.info(f"After cleaning: {len(df)} valid repositories")
    return df

def extract_features(df):
    """Add derived features for recommender"""

    df['days_since_update'] = (datetime.now(timezone.utc) - df['updated_at']).dt.days 
    
    df['combined_text'] = (
        df['description'].fillna('') + ' ' +
        df['topics'].apply(safe_join) + ' ' +
        df['field'].fillna('') + ' ' +
        df['language'].fillna('')
    )
    
    logger.info("Feature extraction complete: added 'days_since_update' and 'combined_text'")
    return df

def safe_join(x):
    if isinstance(x, list):
        return ','.join(x)
    return ''



