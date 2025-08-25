from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
from sklearn.metrics.pairwise import cosine_similarity
from typing import List

# Cargar artefactos
pipe = joblib.load("tfidf_pipe.joblib")
store = joblib.load("faqs_texts.joblib")
X = store["X"]; QUESTIONS = store["questions"]; ANSWERS = store["answers"]

CONFIDENCE_THRESHOLD = 0.25

app = FastAPI(title="FAQ Chatbot (TF-IDF)", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

class AskIn(BaseModel):
    query: str

class AskOut(BaseModel):
    answer: str
    match_question: str
    score: float

class RankItem(BaseModel):
    question: str
    answer: str
    score: float

class TopKOut(BaseModel):
    results: List[RankItem]

@app.get("/")
def root():
    return {"status": "ok", "items": len(QUESTIONS)}

@app.post("/ask", response_model=AskOut)
def ask(payload: AskIn):
    q = (payload.query or "").strip()
    if not q:
        return {"answer": "Por favor, escribe una pregunta.", "match_question": "", "score": 0.0}
    v = pipe.transform([q])
    scores = cosine_similarity(v, X).ravel()
    ix = int(scores.argmax())
    score = float(scores[ix])
    if score < CONFIDENCE_THRESHOLD:
        return {
            "answer": "No estoy seguro. ¿Puedes reformular o ser más específico?",
            "match_question": "",
            "score": score
        }
    return {"answer": ANSWERS[ix], "match_question": QUESTIONS[ix], "score": score}

@app.post("/topk", response_model=TopKOut)
def topk(payload: AskIn, k: int = 5):
    q = (payload.query or "").strip()
    v = pipe.transform([q])
    scores = cosine_similarity(v, X).ravel()
    idx = scores.argsort()[::-1][:k]
    results = [
        {"question": QUESTIONS[i], "answer": ANSWERS[i], "score": float(scores[i])}
        for i in idx
    ]
    return {"results": results}
