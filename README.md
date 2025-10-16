
## project structure

``` 
open_source_recommender/
│
├── config/
│   ├── config.yaml               # All settings: API keys, filters, model paths
│   └── __init__.py
│
├── data/
│   ├── raw/                      # Raw GitHub data (JSON/CSV)
│   ├── processed/                # Cleaned + transformed data
│   └── db.sqlite3                # Optional: SQLite database
│
├── notebooks/
│   └── exploration.ipynb         # Data exploration, testing queries
│
├── src/
│   ├── __init__.py
│   ├── api/
│   │   ├── github_client.py      # Fetch repos using GitHub API
│   │   ├── github_scraper.py     # (optional fallback: scraping trending)
│   │   └── __init__.py
│   │
│   ├── data/
│   │   ├── data_cleaner.py       # Preprocess + store repos
│   │   ├── db_handler.py         # Save/load data from database
│   │   └── __init__.py
│   │
│   ├── recommender/
│   │   ├── skill_vectorizer.py   # Convert skills to vectors (TF-IDF / Embeddings)
│   │   ├── matcher.py            # Match skills ↔ project descriptions
│   │   ├── ranker.py             # Rank results by score + filters
│   │   └── __init__.py
│   │
│   ├── interface/
│   │   ├── app.py                # Streamlit / FastAPI app
│   │   └── cli.py                # Optional CLI version
│   │
│   └── utils/
│       ├── logger.py             # Project-wide logging setup
│       ├── helpers.py            # Small shared utility functions
│       └── __init__.py
│
├── tests/
│   ├── test_github_api.py
│   ├── test_matcher.py
│   └── __init__.py
│
├── .env                          # API keys (GitHub token)
├── .gitignore
├── requirements.txt
├── README.md
└── main.py                       # Entry point to run full pipeline
```
