import json
import pickle
from pathlib import Path
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

# === Paths ===
CHUNKS_PATH = Path("Assets/chunks.json")
EMBEDDINGS_PATH = Path("Assets/embedded_chunks.pkl")

# === Load chunks ===
with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
    chunks = json.load(f)

# === Load the embedding model ===
print("🔄 Loading model: intfloat/e5-base-v2 ...")
model = SentenceTransformer("intfloat/e5-base-v2")
print("✅ Model loaded.")

# === Prepare texts for embedding ===
texts_to_embed = [f"passage: {chunk['content']}" for chunk in chunks]

# === Generate embeddings ===
print(f"🔍 Generating embeddings for {len(texts_to_embed)} chunks...")
embeddings = model.encode(texts_to_embed, show_progress_bar=True, convert_to_numpy=True)

# === Attach embeddings to chunks (cleaner version) ===
embedded_chunks = []
for chunk, embedding in zip(chunks, embeddings):
    embedded_chunks.append({
        "type": chunk.get("type", ""),
        "section": chunk.get("section", ""),
        "content": chunk["content"],
        "embedding": embedding
    })

# === Save to .pkl ===
EMBEDDINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(EMBEDDINGS_PATH, "wb") as f:
    pickle.dump(embedded_chunks, f)

print(f"✅ Embedded chunks saved to {EMBEDDINGS_PATH}")
