import argparse
from src.data_refresher_pipline import data_refresher_pipeline
#from src.utils.ensure_existence import ensure_data_exists
from src.utils.logger import setup_logger

logger = setup_logger("main")


def run_recommender(query, sort_by="score", n_results=5):
    from src.recommender import GitHubRecommender

    recommender = GitHubRecommender()

    logger.info(f"Running recommender for query: {query}")
    recommendations = recommender.recommend(
        user_query=query,
        n_results=n_results,
        sort_by=sort_by
    )

    print(f"\nTop {n_results} recommendations sorted by {sort_by}:\n")
    for i, repo in enumerate(recommendations, 1):
        print(f"{i}. {repo['name']} ({repo['stars']} stars) - Score: {repo['score']}")
        print(f"   URL: {repo['url']}")
        print(f"   Description: {repo['description']}\n")



def main():
    parser = argparse.ArgumentParser(description="GitHub Open Source Project Recommender")
    parser.add_argument("--query", type=str, help="User search query", required=False)
    parser.add_argument("--sort", type=str, default="score", choices=["score", "stars"], help="Sort results by field")
    parser.add_argument("--top", type=int, default=5, help="Number of results to display")

    args = parser.parse_args()
    #ensure_data_exists()
    query = args.query or input("💬 Enter your interests: ")
    data_refresher_pipeline(topics=["machine-learning", "deep-learning"], languages=["python"], max_repos=None)
    run_recommender(query, sort_by=args.sort, n_results=args.top)

if __name__ == "__main__":
    main()
