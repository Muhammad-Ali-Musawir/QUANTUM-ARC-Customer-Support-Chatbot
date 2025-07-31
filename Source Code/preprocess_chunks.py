import json
from pathlib import Path

# === File Paths ===
FAQS_PATH = Path("Source Code/Assets/faqs.json")
PRODUCTS_PATH = Path("Source Code/Assets/products.json")
POLICIES_PATH = Path("Source Code/Assets/policies.json")
OUTPUT_PATH = Path("Source Code/Assets/chunks.json")

# === Step 1: Load JSON files ===
def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

faqs = load_json(FAQS_PATH)
products = load_json(PRODUCTS_PATH)
policies = load_json(POLICIES_PATH)

# === Step 2: Process into chunks ===
chunks = []

# --- Process FAQs ---
for item in faqs:
    chunk = {
        "type": "faq",
        "section": item.get("category", "General"),
        "question": item["question"],
        "answer": item["answer"],
        "content": f"Q: {item['question']}\nA: {item['answer']}"
    }
    chunks.append(chunk)

# --- Process Products ---
for item in products:
    features = "\n- " + "\n- ".join(item["key_features"])
    chunk = {
        "type": "product",
        "category": item["category"],
        "name": item["name"],
        "brand": item["brand"],
        "model": item["model"],
        "price_usd": item["price_usd"],
        "content": (
            f"Product: {item['name']}\n"
            f"Brand: {item['brand']}\n"
            f"Category: {item['category']}\n"
            f"Model: {item['model']}\n"
            f"Price: ${item['price_usd']}\n"
            f"Key Features:{features}"
        )
    }
    chunks.append(chunk)

# --- Process Policies ---
for key, section in policies.items():
    chunk = {
        "type": "policy",
        "section": section["title"],
        "policy": section["policy"],
        "content": f"{section['title']}:\n{section['policy']}"
    }
    chunks.append(chunk)

# === Step 3: Save to chunks.json ===
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(chunks, f, indent=2, ensure_ascii=False)

print(f"✅ Successfully created {len(chunks)} chunks and saved to {OUTPUT_PATH}")

