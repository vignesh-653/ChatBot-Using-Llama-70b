from fastapi import FastAPI
import faiss
import json
from sentence_transformers import SentenceTransformer
import numpy as np

app = FastAPI()

# Load FAISS index
index = faiss.read_index(r"C:\Users\vigne\OneDrive\Desktop\Viggu\sem8\mini_proj\cs_embeddings\items_faiss.index")

# Load text mappings
with open(r"C:\Users\vigne\OneDrive\Desktop\Viggu\sem8\mini_proj\cs_embeddings\text_mappings.json", "r", encoding="utf-8") as f:
    id_to_text = json.load(f)

# Load the embedding model used for indexing
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Function to search for the most similar documents
def search_similar_document(query, top_k=5):
    query_embedding = model.encode(query, normalize_embeddings=True)
    query_embedding = np.array([query_embedding]).astype("float32")
    distances, indices = index.search(query_embedding, top_k)
    results = [id_to_text[str(idx)] for idx in indices[0] if str(idx) in id_to_text]
    return results, distances[0]

# API endpoint to retrieve similar menu items
@app.get("/menu/{query_text}")
def get_similar_menu_items(query_text: str):
    results, scores = search_similar_document(query_text, top_k=5)
    response = []
    for doc, score in zip(results, scores):
        response.append({"document": doc, "score": float(score)})
    return {
        "status": "success",
        "query": query_text,
        "results": response
    }
