import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from utils.faiss_handler import load_faiss_index, get_top_k_chunks
from utils.constants import INDEX_PATH, METADATA_PATH
from utils.gemini_generator import generate_answer
from utils.embedder import embed_chunks
import pickle
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="QueryBotX API",
    description="Natural language to SQL using Gemini + FAISS",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os
from utils.constants import SOURCE_DIR

def materialize_chunk(meta):
    with open(os.path.join(SOURCE_DIR, meta["source"]), "r", encoding="utf-8") as f:
        text = f.read()
    words = text.split()
    return " ".join(words[meta["start"]:meta["end"]])


# Load FAISS index and metadata on startup
faiss_index = load_faiss_index(INDEX_PATH)
with open(METADATA_PATH, 'rb') as f:
    metadata = pickle.load(f)

# Request model
class QueryRequest(BaseModel):
    query: str
    k: int = 2

# Endpoint
@app.post("/ask")
def handle_query(request: QueryRequest):
    query = request.query
    k = request.k

    # Step 1: Embed the query
    query_embedding = embed_chunks([query])[0]

    # Step 2: Search top-k similar chunks
    top_k_indices = get_top_k_chunks(faiss_index, query_embedding, k)

    # Step 3: Retrieve the matching chunks
    top_k_chunks = [metadata[i] for i in top_k_indices]

    logger.info(f"🔍 Incoming Query: {query}")
    logger.info(f"🔢 Top-{k} Indices: {top_k_indices}")

    logger.info("📚 Retrieved Chunks:")
    for i, chunk in enumerate(top_k_chunks):
        chunk_text = materialize_chunk(chunk)
        logger.info(f"\n--- Chunk {i+1} ---\n{chunk_text}\n")

    # Step 4: Construct prompt
    context = "\n".join([materialize_chunk(chunk) for chunk in top_k_chunks])
    full_prompt = f"""Context:\n{context}\n\nAnswer the following user query by building a SQL query based on the above context:\n\nQuery: {query}"""

    # Step 5: Generate response
    answer = generate_answer(full_prompt)

    return {"response": answer}

# Server runner
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
