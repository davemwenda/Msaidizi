def chunk_text(text, source, chunk_size=400, overlap=80):
    """Split text into overlapping word-based chunks, tagged with source."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)
        chunks.append({
            "text": chunk_text,
            "source": source,
            "type": "handbook"
        })
        start += chunk_size - overlap
    return chunks


def faqs_to_chunks(path="data/raw/faqs.md"):
    with open(path, encoding='utf-8') as f:
        content = f.read()
    entries = content.split("\n\n")
    return [{"text": e.strip(), "source": "faqs", "type": "faq"} for e in entries if e.strip()]