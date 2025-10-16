"""from src.api.github_client import fetch_repositories
from src.data.data_cleaner import preprocess_data
from src.recommender.matcher import recommend_projects"""
from src.utils.logger import setup_logger

logger = setup_logger("main")

def main():
    logger.info("Starting recommendation system...")

    # Step 1: Fetch data
    repos = fetch_repositories(topics=["machine-learning", "fastapi"])
    
    # Step 2: Clean and store
    processed = preprocess_data(repos)
    
    # Step 3: Recommend based on sample input
    user_skills = ["python", "fastapi", "nlp"]
    recommendations = recommend_projects(user_skills, processed)
    
    # Step 4: Display
    for r in recommendations[:5]:
        logger.info(f"Recommended: {r['name']} - {r['url']} ({r['score']})")

if __name__ == "__main__":
    main()


