import datetime
import requests
import os
import pandas as pd
import time
from dotenv import load_dotenv
from src.utils.config_loader import load_config
from src.utils.logger import setup_logger

load_dotenv()
logger = setup_logger("github_fetcher")


def fetch_repositories(topics=None, languages=None, max_repos=None, overfetch_factor=2):
    """
    Fetch trending GitHub repositories based on topics and languages.
    
    Overfetching: fetches more than max_repos (controlled by overfetch_factor)
    Handles pagination and 1000-result GitHub limit
    Rate limit aware (sleeps & retries)
    Deduplicates and filters results
    """
    start_time = time.time()
    config = load_config()
    token = os.getenv("GITHUB_TOKEN") or config["github"]["token"]
    headers = {"Authorization": f"token {token}"} if token else {}

    # Configurable values
    topics = topics or config["github"]["topics"]
    languages = languages or config["github"]["languages"]
    max_repos_per_query = max_repos or config["github"]["max_repos"]
    per_page = min(config["github"]["per_page"], 100)
    sort = config["github"]["sort"]
    order = config["github"]["order"]
    rate_limit_wait = config["github"]["rate_limit_wait"]
    min_stars = config["github"].get("min_stars", 50)

    # Fetch more than needed to allow later filtering
    overfetch_limit = max_repos_per_query * overfetch_factor
    all_repos = []

    logger.info(f"Starting GitHub fetch (topics={len(topics)}, languages={len(languages)})")

    for topic in topics:
        for language in languages:
            query_repos = []
            page = 1
            query = f"topic:{topic}+language:{language}"

            logger.info(f"Fetching repos for {query} (target: {overfetch_limit})")

            while len(query_repos) < overfetch_limit:
                if page * per_page > 1000:
                    logger.warning(f"Reached 1000-result GitHub API limit for {query}")
                    break

                url = f"https://api.github.com/search/repositories?q={query}&sort={sort}&order={order}&page={page}&per_page={per_page}"
                response = requests.get(url, headers=headers)

                # --- Error handling ---
                if response.status_code == 403:  # rate limit
                    reset_time = response.headers.get("X-RateLimit-Reset")
                    if reset_time:
                        wait_for = int(reset_time) - int(time.time()) + 10
                        logger.warning(f"Rate limit hit. Waiting {wait_for}s before retry.")
                        time.sleep(max(wait_for, rate_limit_wait))
                        continue
                    else:
                        time.sleep(rate_limit_wait)
                        continue
                elif response.status_code != 200:
                    logger.error(f"GitHub API error {response.status_code}: {response.text}")
                    break

                items = response.json().get("items", [])
                if not items:
                    break

                # --- Add fetched repos ---
                for repo in items:
                    if repo.get("stargazers_count", 0) < min_stars:
                        continue
                    query_repos.append({
                        "name": repo["name"],
                        "full_name": repo["full_name"],
                        "url": repo["html_url"],
                        "description": repo["description"],
                        "stars": repo["stargazers_count"],
                        "field": topic,
                        "language": repo["language"],
                        "topics": repo.get("topics", []),
                        "updated_at": repo["updated_at"],
                        "avatar_url": repo["owner"]["avatar_url"] if "owner" in repo else None
                    })

                logger.info(f"Page {page}: {len(items)} fetched ({len(query_repos)} total for this query)")
                page += 1
                time.sleep(rate_limit_wait)

                if len(items) < per_page:
                    break

            logger.info(f" Finished query: {query} — {len(query_repos)} repos")
            all_repos.extend(query_repos[:overfetch_limit])

    # --- Deduplicate by full_name ---
    unique_repos = list({repo["full_name"]: repo for repo in all_repos}.values())

    # --- Sort & Filter ---
    df = pd.DataFrame(unique_repos)
    if not df.empty:
        df = df[df["stars"] >= min_stars]
        df = df.sort_values(by="stars", ascending=False).reset_index(drop=True)

    duration = round(time.time() - start_time, 2)
    logger.info(f"Total unique repos collected: {len(df)} in {duration}s at {datetime.datetime.now():%Y-%m-%d %H:%M:%S}")

    return df
