import os
from dotenv import load_dotenv
from google import genai
from sentence_transformers import SentenceTransformer
import chromadb
import time

MODEL_FALLBACKS = ["gemini-3.8-flash", "gemini-flash-latest", "gemini-3.1-flash-lite"]

load_dotenv()

# Embedding model
model = SentenceTransformer('intfloat/multilingual-e5-small')

# Vector DB client — renamed
chroma_client = chromadb.Client()
collection = chroma_client.create_collection("poc")

# Gemini client — renamed
gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

docs = [
"The final exam period runs from Dec 1 to Dec 15.",
"To report a maintenance issue, submit a ticket at facilities.university.edu.",
"Late assignment submissions incur a 10% penalty per day.",
"The library is open from 7am to 11pm on weekdays.",
"To appeal a grade, contact your department's academic office within 14 days.",
]
embeddings = model.encode(docs).tolist()
collection.add(documents=docs, embeddings=embeddings, ids=[str(i) for i in range(len(docs))])


def answer(query, retries=2):
    q_emb = model.encode([query]).tolist()
    results = collection.query(query_embeddings=q_emb, n_results=2)
    context = "\n".join(results['documents'][0])
    prompt = f"Answer ONLY using this context. If it's not there, say you don't know.\n\nContext:\n{context}\n\nQuestion: {query}"

    for model_name in MODEL_FALLBACKS:
        for attempt in range(retries):
            try:
                response = gemini_client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                return response.text
            except Exception as e:
                print(f"{model_name} attempt {attempt + 1} failed: {e}")
                time.sleep(2 * (attempt + 1))
    return "Sorry, I'm having trouble reaching the AI service right now. Please try again in a moment."

if __name__ == "__main__":
    print(answer("When is the final exam period?"))
    print(answer("Mtihani wa mwisho ni lini?"))
    print(answer("What's the weather like today?"))  # should say it doesn't know

