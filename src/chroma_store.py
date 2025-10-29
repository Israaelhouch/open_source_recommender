from chromadb import PersistentClient
from src.utils.helpers import safe_join
from src.utils.logger import setup_logger

logger = setup_logger("vector_store_builder")

class ChromaStore:
    def __init__(self, collection_name="github_repos", persist_dir="data/embeddings/chroma"):
        self.collection_name = collection_name
        self.persist_dir = persist_dir
        self.client = PersistentClient(path=self.persist_dir)
        self.collection = self.client.get_or_create_collection(name=self.collection_name)
        logger.info(f"Chroma collection '{self.collection_name}' loaded at {self.persist_dir}")

    def reset_collection(self):
        logger.warning(f"Deleting collection '{self.collection_name}' for reset.")
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.get_or_create_collection(name=self.collection_name)
        logger.info(f"Collection '{self.collection_name}' reset.")

    def add_documents(self, df, embeddings):
        existing = set(self.collection.get()["ids"])
        new_docs = df[~df.index.astype(str).isin(existing)]

        if new_docs.empty:
            logger.info("No new documents to add.")
            return

        new_embeddings = [
            embeddings[i] for i, (idx, _) in enumerate(df.iterrows())
            if str(idx) not in existing
        ]

        for (idx, row), emb in zip(new_docs.iterrows(), new_embeddings):
            self.collection.add(
                ids=[str(idx)],
                embeddings=[emb.tolist()],
                documents=[row['combined_text']],
                metadatas=[{
                    "name": row['name'],
                    "url": row['url'],
                    "description": row['description'],
                    "topics": safe_join(row['topics']),
                    "language": row['language'],
                    "stars": int(row['stars']),
                    "field": row['field']
                }]
            )

        logger.info(f"Added {len(new_docs)} new documents to collection.")


    def query(self, query_embedding, n_results=5, filters=None):
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filters
        )
