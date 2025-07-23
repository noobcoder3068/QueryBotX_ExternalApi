from utils.chunker import chunk_texts
from utils.embedder import embed_chunks
from utils.faiss_handler import build_faiss_index, save_faiss_index
from utils.constants import SOURCE_DIR, INDEX_PATH, METADATA_PATH

import pickle
import os

def load_documents(directory):
    documents = []
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            path = os.path.join(directory, filename)
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
                print(f"📄 {filename}: {len(text)} chars | {len(text.split())} words")
                print("--- Preview ---")
                print(text[:500])  # Preview the first 500 characters
                print("--------------")
                documents.append((filename, text))
    return documents

def main():
    print("🔹 Loading source documents...")
    docs = load_documents(SOURCE_DIR)

    print("🔹 Chunking texts...")
    chunks, metadata = chunk_texts(docs)

    print("🔹 Generating embeddings...")
    embeddings = embed_chunks(chunks)

    print("🔹 Building FAISS index...")
    index = build_faiss_index(embeddings)

    print("🔹 Saving index and metadata...")
    save_faiss_index(index, INDEX_PATH)
    with open(METADATA_PATH, "wb") as f:
        pickle.dump(metadata, f)

    print("✅ Preparation complete. You’re ready to query.")

    # 🔍 Display chunks after saving
    with open("all_chunks_output.txt", "w", encoding="utf-8") as out:
        for i, meta in enumerate(metadata):
            source = meta["source"]
            start = meta["start"]
            end = meta["end"]

            with open(os.path.join(SOURCE_DIR, source), "r", encoding="utf-8") as f:
                full_text = f.read()

            words = full_text.split()
            chunk_text = " ".join(words[start:end])

            out.write(f"\n🔹 Chunk {i + 1}\n")
            out.write(f"📄 Source: {source}\n")
            out.write(f"📍 Start: {start}  End: {end}\n")
            out.write(f"📝 Content:\n{chunk_text}\n")
            out.write("-" * 100 + "\n")

if __name__ == "__main__":
    main()
