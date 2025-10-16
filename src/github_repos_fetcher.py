import requests
import os
import pandas as pd
import time
import yaml
from dotenv import load_dotenv
from src.utils.logger import setup_logger

load_dotenv()
logger = setup_logger("github_fetcher")

def load_config():
    """Load configuration from config.yaml"""
    with open("config/config.yaml", "r") as f:
        return yaml.safe_load(f)

def fetch_repositories(topics=None, languages=None):
    """
    Fetch repositories per topic+language, limited to max_repos_per_query.
    Handles GitHub 1000-result limit and pagination.
    """
    config = load_config()
    token = os.getenv("GITHUB_TOKEN") or config["github"]["token"]
    headers = {"Authorization": f"token {token}"} if token else {}

    topics = topics or config["github"]["search_topics"]
    languages = languages or config["github"]["search_languages"]

    max_repos_per_query = config["github"]["max_repos"]
    per_page = min(config["github"]["per_page"], max_repos_per_query)
    sort = config["github"]["sort"]
    order = config["github"]["order"]
    rate_limit_wait = config["github"]["rate_limit_wait"]
    

    all_repos = []

    for topic in topics:
        for language in languages:
            query_repos = []
            page = 1
            query = f"topic:{topic}+language:{language}"
            logger.info(f"Fetching repositories for query: {query}")

            while len(query_repos) < max_repos_per_query:
                if page * per_page > 1000:
                    logger.warning(f"Reached GitHub 1000 search result limit for query: {query}")
                    break

                url = f"https://api.github.com/search/repositories?q={query}&sort={sort}&order={order}&page={page}&per_page={per_page}"
                response = requests.get(url, headers=headers)

                if response.status_code != 200:
                    logger.error(f"GitHub API Error {response.status_code}: {response.text}")
                    break

                items = response.json().get("items", [])
                if not items:
                    break

                for repo in items:
                    query_repos.append({
                        "name": repo["name"],
                        "full_name": repo["full_name"],
                        "url": repo["html_url"],
                        "description": repo["description"],
                        "stars": repo["stargazers_count"],
                        "field": topic,
                        "language": repo["language"],
                        "topics": repo.get("topics", []),
                        "updated_at": repo["updated_at"]
                    })

                logger.info(f"Fetched page {page} ({len(query_repos)} total for this query)")
                page += 1
                time.sleep(rate_limit_wait)

                if len(items) < per_page:
                    break
            logger.info(f"Finally; Fetched {len(query_repos)} total for this query")
            # Only keep up to max_repos_per_query
            all_repos.extend(query_repos[:max_repos_per_query])

    # Deduplicate by full_name across all queries
    unique_repos = list({repo['full_name']: repo for repo in all_repos}.values())
    logger.info(f"Total unique repos collected: {len(unique_repos)}")

    df = pd.DataFrame(unique_repos)
    return df
