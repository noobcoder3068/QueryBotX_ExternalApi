import faiss
import numpy as np
import pickle
import os
from typing import List, Tuple

def build_faiss_index(embeddings: List[List[float]]) -> faiss.IndexFlatL2:
    """
    Builds a FAISS index using L2 distance.
    """
    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings).astype("float32"))
    return index

def save_faiss_index(index: faiss.IndexFlatL2, path: str) -> None:
    """
    Saves the FAISS index to disk.
    """
    faiss.write_index(index, path)

def load_faiss_index(path: str) -> faiss.IndexFlatL2:
    """
    Loads the FAISS index from disk.
    """
    return faiss.read_index(path)

def load_metadata(path: str) -> List[str]:
    """
    Loads the metadata (chunk mappings) from disk.
    """
    with open(path, "rb") as f:
        return pickle.load(f)

def load_faiss_resources(index_path: str = "faiss_index.index", metadata_path: str = "metadata.pkl") -> Tuple[faiss.IndexFlatL2, List[str]]:
    """
    Loads both the FAISS index and metadata.
    """
    index = load_faiss_index(index_path)
    metadata = load_metadata(metadata_path)
    return index, metadata

def get_top_k_chunks(index: faiss.IndexFlatL2, query_embedding: List[float], k: int = 5) -> List[int]:
    """
    Searches the index for top-k most similar chunks.
    """
    query_vector = np.array(query_embedding).reshape(1, -1).astype("float32")
    _, indices = index.search(query_vector, k)
    return indices[0].tolist()
