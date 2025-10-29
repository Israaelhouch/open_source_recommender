from src.utils.helpers import clean_data, extract_features, save_data
from src.utils.logger import setup_logger

logger = setup_logger("data_processing")

def process_pipeline(df):
    """Full data processing pipeline"""
    if df is None:
        return
    df = clean_data(df)
    df = extract_features(df)
    save_data(df, filename="data/processed/processed_data.csv")
    return df

