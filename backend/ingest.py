import json
from sentence_transformers import SentenceTransformer
import chromadb

model = SentenceTransformer('intfloat/multilingual-e5-small')
chroma_client = chromadb.PersistentClient(path="backend/chroma_db")  # persisted, not in-memory
collection = chroma_client.get_or_create_collection("campus_assistant")

def ingest():
    with open("data/processed/chunks.json", encoding='utf-8') as f:
        chunks = json.load(f)

    docs = [c["text"] for c in chunks]
    metadatas = [{"source": c["source"], "type": c["type"]} for c in chunks]
    ids = [str(i) for i in range(len(chunks))]

    embeddings = model.encode(docs).tolist()
    collection.add(documents=docs, embeddings=embeddings, metadatas=metadatas, ids=ids)
    print(f"Ingested {len(chunks)} chunks into vector DB")

if __name__ == "__main__":
    ingest()