import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_EMBED_URL = "https://generativelanguage.googleapis.com/v1beta/models/embedding-001:embedContent"

def embed_chunks(chunks: list[str], delay: float = 0.5) -> list[list[float]]:
    """
    Embeds a list of text chunks using Gemini Embedding API.
    Returns a list of embedding vectors.
    """
    embeddings = []
    for chunk in chunks:
        try:
            res = requests.post(
                f"{GEMINI_EMBED_URL}?key={API_KEY}",
                headers={"Content-Type": "application/json"},
                json={"content": {"parts": [{"text": chunk}]}}
            )
            res.raise_for_status()
            embeddings.append(res.json()["embedding"]["values"])
            time.sleep(delay)  # to prevent rate-limiting
        except Exception as e:
            print(f"Error embedding chunk: {e}")
            embeddings.append([])  # preserve index
    return embeddings

def embed_query(query: str) -> list[float]:
    """
    Embeds a single user query. Wraps embed_chunks and returns a single vector.
    """
    return embed_chunks([query])[0]
