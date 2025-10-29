from sentence_transformers import SentenceTransformer
import numpy as np
from tqdm import tqdm

class Embedder:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L12-v2"):
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(self, texts):
        embeddings = []
        for text in tqdm(texts, desc="Generating embeddings"):
            emb = self.model.encode(text)
            embeddings.append(emb)
        return np.array(embeddings)
