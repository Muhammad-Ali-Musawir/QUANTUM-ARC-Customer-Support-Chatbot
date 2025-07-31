import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path

# === Load embedded chunks from disk ===
EMBEDDED_CHUNKS_PATH = Path("Assets/embedded_chunks.pkl")
with open(EMBEDDED_CHUNKS_PATH, "rb") as f:
    embedded_chunks = pickle.load(f)

def get_top_chunks(query_embedding: np.ndarray, top_k: int = 3) -> list:
    """
    Compares query embedding with all chunk embeddings and returns top-k relevant chunks.

    Args:
        query_embedding (np.ndarray): The embedding of the user question.
        top_k (int): Number of top relevant chunks to return.

    Returns:
        list of dicts: Top-k most relevant chunks (including content, type, section, etc.)
    """
    # Extract just the vectors from embedded chunks
    chunk_vectors = np.array([chunk["embedding"] for chunk in embedded_chunks])

    # Compute cosine similarity
    similarities = cosine_similarity([query_embedding], chunk_vectors)[0]

    # Rank chunks by similarity
    top_indices = similarities.argsort()[-top_k:][::-1]

    # Get the actual top chunks
    top_chunks = [embedded_chunks[i] for i in top_indices]

    return top_chunks
