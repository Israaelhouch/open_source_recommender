from chromadb import PersistentClient
from src.utils.logger import setup_logger
from src.embedder import Embedder  

logger = setup_logger("recommender")

class GitHubRecommender:
    def __init__(self, collection_name="github_repos", persist_dir="data/embeddings/chroma"):
        # connect to Chroma
        self.client = PersistentClient(path=persist_dir)
        self.collection = self.client.get_collection(name=collection_name)
        logger.info(f"Loaded Chroma collection '{collection_name}' for recommendation.")

        # initialize your embedder
        self.embedder = Embedder()

    def recommend(self, user_query, n_results=10, sort_by="stars", filters=None):
        """
        Recommend repositories based on user query.
        sort_by: 'score' (similarity) or 'stars' (GitHub stars)
        """
        # Generate query embedding
        query_embedding = self.embedder.generate_embeddings([user_query])[0]

        # Query Chroma
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results, 
            where=filters
        )

        # Prepare clean recommendation list
        recommendations = []
        for i in range(len(results['ids'][0])):
            metadata = results['metadatas'][0][i]
            distance = results['distances'][0][i]
            recommendations.append({
                "name": metadata.get("name", ""),
                "url": metadata.get("url", ""),
                "description": metadata.get("description", ""),
                "topics": metadata.get("topics", ""),
                "language": metadata.get("language", ""),
                "stars": metadata.get("stars", 0),
                "score": round(1 - distance, 4)
            })

        # Sort results
        if sort_by == "stars":
            recommendations.sort(key=lambda x: x["stars"], reverse=True)
        elif sort_by == "score":
            recommendations.sort(key=lambda x: x["score"], reverse=True)

        logger.info(f"Returned {len(recommendations)} recommendations sorted by {sort_by}.")
        return recommendations
