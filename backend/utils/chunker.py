def chunk_texts(docs, chunk_size=512, overlap= 10):
    chunks = []
    metadata = []
    for filename, text in docs:
        words = text.split()
        for i in range(0, len(words), chunk_size- overlap):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
            metadata.append({"source": filename, "start": i, "end": i + chunk_size})
    return chunks, metadata
