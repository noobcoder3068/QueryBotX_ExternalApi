import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.join(BASE_DIR, "..", "data")
INDEX_PATH = os.path.join(BASE_DIR, "..", "index", "faiss.index")
METADATA_PATH = os.path.join(BASE_DIR, "..", "index", "metadata.pkl")
