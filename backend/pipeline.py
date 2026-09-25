import os, time
from dotenv import load_dotenv
from google import genai
from sentence_transformers import SentenceTransformer
import chromadb

load_dotenv()
model = SentenceTransformer('intfloat/multilingual-e5-small')
chroma_client = chromadb.PersistentClient(path="backend/chroma_db")
collection = chroma_client.get_or_create_collection("campus_assistant")
gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

MODEL_FALLBACKS = ["gemini-3.1-flash-lite", "gemini-2.5-flash-lite", "gemini-3.8-flash"]

def detect_query_type(query):
    q = query.lower()
    if any(w in q for w in ["exam", "mtihani", "sit exam", "exam date"]):
        return "exam"
    if any(w in q for w in ["class", "lecture", "session", "somo"]):
        return "timetable"
    return None  # no strong signal, search everything

def answer(query, retries=2):
    q_type = detect_query_type(query)
    q_emb = model.encode([query]).tolist()

    where_filter = {"type": q_type} if q_type else None
    results = collection.query(query_embeddings=q_emb, n_results=3, where=where_filter)
    context = "\n".join(results['documents'][0])
    prompt = (
    f"Answer ONLY using the context below. If the context does not contain "
    f"the answer, say clearly that you don't have that information — "
    f"do not guess or make up dates, venues, or names.\n\n"
    f"Context:\n{context}\n\nQuestion: {query}"
    )
    for model_name in MODEL_FALLBACKS:
        for attempt in range(retries):
            try:
                response = gemini_client.models.generate_content(model=model_name, contents=prompt)
                return response.text
            except Exception as e:
                print(f"{model_name} attempt {attempt + 1} failed: {e}")
                time.sleep(5 * (attempt + 1))
    return "Sorry, I'm having trouble reaching the AI service right now."

if __name__ == "__main__":
    # print(answer("When is the CCS 2103 exam?"))                     # exam timetable
    # print(answer("When is the Operating Systems class?")) # teaching timetable

    print(answer("When is my Operating Systems exam?"))
    print(answer("When is my Operating Systems class?"))