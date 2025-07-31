from sentence_transformers import SentenceTransformer
import numpy as np

# Load the model once and reuse (for performance)
model = SentenceTransformer("intfloat/e5-base-v2")

def embed_user_query(question: str) -> np.ndarray:
    """
    Embeds the user query using intfloat/e5-base-v2 model.
    Adds 'query:' prefix as required by the model.

    Args:
        question (str): The user input question.

    Returns:
        np.ndarray: The embedded vector of the question.
    """
    formatted = f"query: {question}"
    embedding = model.encode(formatted, convert_to_numpy=True)
    return embedding


# from embed_query import embed_user_query

# query_embedding = embed_user_query("What payment methods do you support?")