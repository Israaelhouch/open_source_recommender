import streamlit as st
from src.data_refresher_pipline import data_refresher_pipeline
from src.recommender import GitHubRecommender
from src.utils.config_loader import load_config

st.set_page_config(page_title="GitHub AI Recommender", page_icon="💡", layout="wide")

st.title("💡 Open Source Project Recommender")
st.markdown("Find trending GitHub repositories that match your interests!")

config = load_config()

# Sidebar Filters
st.sidebar.header("🔍 Filters")

languages = config["github"]["languages"]
topics = config["github"]["topics"]

selected_languages = st.sidebar.multiselect("Filter by language(s)", languages)
selected_topics = st.sidebar.multiselect("Filter by topic(s)", topics)
min_stars = st.sidebar.slider("Minimum stars", min_value=50, max_value=50000, value=50, step=300)
n_results = st.sidebar.slider("Number of repositories to display", min_value=5, max_value=50, value=10, step=5)

# --- Display Active Filters ---
st.sidebar.markdown("### 🎯 Active Filters")

active_filters = []
if "Any" not in selected_languages:
    active_filters.append(f"**Languages:** {', '.join(selected_languages)}")
if "Any" not in selected_topics:
    active_filters.append(f"**Topics:** {', '.join(selected_topics)}")
if min_stars > 0:
    active_filters.append(f"**Stars ≥ {min_stars}**")
if n_results:
    active_filters.append(f"**Number of top results:** {n_results}")
if active_filters:
    for f in active_filters:
        st.sidebar.markdown(f"- {f}")
else:
    st.sidebar.info("No filters applied.")

# --- Query Section ---
st.subheader("💬 Describe what you're looking for clearly")
query = st.text_input("e.g. 'awesome PyTorch projects for image classification'")

if query:
    with st.spinner("🔍 Searching repositories..."):
        filters = {}

        # Build filters dynamically
        if selected_languages and "Any" not in selected_languages:
            filters["language"] = {"$in": selected_languages}
        if selected_topics and "Any" not in selected_topics:
            filters["field"] = {"$in": selected_topics}
        if min_stars > 0:
            filters["stars"] = {"$gte": min_stars}

        where_clause = None
        if filters:
            if len(filters) > 1:
                where_clause = {"$and": [{k: v} for k, v in filters.items()]}
            else:
                where_clause = filters

        # Run recommendation
        data_refresher_pipeline(topics=selected_topics, languages=selected_languages, max_repos=n_results)
        recommender = GitHubRecommender()
        results = recommender.recommend(
            query,
            n_results=n_results,
            sort_by="stars",
            filters=where_clause
        )

    # --- Display results ---
    if results:
        st.success(f"Found {len(results)} repositories matching your query!")
        st.caption(f"Displaying top {min(len(results), n_results)} results sorted by number of stars.")
        st.divider()

        for repo in results:
            col1, col2 = st.columns([1, 4])
            with col1:
                avatar_url = repo.get("avatar_url", "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png")
                st.image(avatar_url, width=40)
            with col2:
                st.markdown(f"### [{repo['name']}]({repo['url']}) ⭐ {repo['stars']:,}")
                st.markdown(f"**Language:** {repo.get('language', 'N/A')}")
                st.write(repo.get("description", "_No description available._"))

                topics = repo.get("topics", [])
                if isinstance(topics, (list, str)) and topics:
                    st.caption("🧠 Topics: " + (", ".join(topics) if isinstance(topics, list) else topics))
                st.divider()

    else:
        st.warning("⚠️ No repositories found. Try changing your filters or query.")
else:
    st.info("👆 Enter a query above to get started.")
