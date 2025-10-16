import pandas as pd
import os

def save_raw_data(repos, filename="data/raw/github_repos.csv"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    df = pd.DataFrame(repos)
    df.to_csv(filename, index=False)
    return filename
