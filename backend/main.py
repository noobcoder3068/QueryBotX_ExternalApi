import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from utils.faiss_handler import load_faiss_index, get_top_k_chunks
from utils.constants import INDEX_PATH, METADATA_PATH
from utils.gemini_generator import generate_answer
from utils.embedder import embed_chunks
from utils.db_config import execute_sql
import pickle
from fastapi.middleware.cors import CORSMiddleware
import logging
import re

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
    k: int = 1

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
    full_prompt = f"""
You are an expert PostgreSQL assistant. Given the schema context and user query, generate an accurate and efficient SQL query.

### Context:
{context}

### User Query:
{query}

### Guidelines:
- Use only the information from the context.
- Do not explain or add comments.
- Only return a syntactically correct SQL query between triple backticks (```) with no additional text.

### SQL Query:
"""
    
    # Step 5: Generate response
    # Step 5: Generate response
    try:
        logger.info("🤖 Sending prompt to Gemini...")
        logger.info(f"\n📤 Full Prompt:\n{full_prompt}\n")
    
        answer = generate_answer(full_prompt)
    
        if not answer:
            logger.warning("⚠️ Gemini returned an empty response.")
            return {"response": "⚠️ No response from Gemini. Please try again."}

        logger.info(f"✅ Gemini Response:\n{answer}")
        match = re.search(r"```sql\s*(.*?)\s*```", answer, re.DOTALL | re.IGNORECASE)
        sql_generated = match.group(1).strip() if match else None

        if sql_generated:
            logger.info(f"🟢 Extracted SQL:\n{sql_generated}")
        else:
            logger.warning("⚠️ Could not extract SQL from the response.")

        sql_response= execute_sql(sql_generated)
        print(sql_response)

        return {
            "response": answer,
            "sql_generated": sql_generated
        }

    except Exception as e:
        logger.error("❌ Error while generating response from Gemini", exc_info=True)
        return {"error": str(e)}


# Server runner
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
