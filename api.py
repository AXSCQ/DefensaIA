from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import json
import uuid
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any, Optional

# Rutas de archivos
DATA = Path("data/faqs.json")
PIPE_PATH = Path("tfidf_pipe.joblib")
FAQS_PATH = Path("faqs_texts.joblib")

# Cargar artefactos
pipe = joblib.load(PIPE_PATH)
store = joblib.load(FAQS_PATH)
X = store["X"]; QUESTIONS = store["questions"]; ANSWERS = store["answers"]

CONFIDENCE_THRESHOLD = 0.25

app = FastAPI(title="FAQ Chatbot (TF-IDF)", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

# Modelos de datos
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
    
class FaqItem(BaseModel):
    q: str
    a: str
    id: Optional[str] = None

# Funciones auxiliares para CRUD
def _read_faqs():
    """Lee las FAQs desde el archivo JSON"""
    return json.loads(DATA.read_text(encoding="utf-8"))

def _write_faqs(items):
    """Escribe las FAQs al archivo JSON"""
    DATA.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

# Endpoints básicos
@app.get("/")
def root():
    return {"status": "ok", "items": len(QUESTIONS)}

@app.post("/ask", response_model=AskOut)
def ask(payload: AskIn):
    """Responde a una consulta buscando la pregunta más similar"""
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
    """Devuelve las k respuestas más similares a la consulta"""
    q = (payload.query or "").strip()
    v = pipe.transform([q])
    scores = cosine_similarity(v, X).ravel()
    idx = scores.argsort()[::-1][:k]
    results = [
        {"question": QUESTIONS[i], "answer": ANSWERS[i], "score": float(scores[i])}
        for i in idx
    ]
    return {"results": results}

# Endpoints CRUD para FAQs
@app.get("/faqs")
def list_faqs():
    """Lista todas las FAQs disponibles"""
    return _read_faqs()

@app.post("/faqs")
def add_faq(item: FaqItem):
    """Crea una nueva FAQ"""
    if not item.q or not item.a:
        raise HTTPException(400, "Formato requerido: {'q': 'pregunta', 'a': 'respuesta'}")
    
    items = _read_faqs()
    
    # Generar ID único si no se proporciona
    new_item = item.dict()
    if not new_item.get("id"):
        new_item["id"] = str(uuid.uuid4())
    
    items.append(new_item)
    _write_faqs(items)
    return new_item

@app.put("/faqs/{faq_id}")
def update_faq(faq_id: str, item: FaqItem):
    """Actualiza una FAQ existente"""
    items = _read_faqs()
    for it in items:
        if it.get("id") == faq_id:
            it["q"] = item.q if item.q else it["q"]
            it["a"] = item.a if item.a else it["a"]
            _write_faqs(items)
            return it
    raise HTTPException(404, "FAQ no encontrada")

@app.delete("/faqs/{faq_id}")
def delete_faq(faq_id: str):
    """Elimina una FAQ"""
    items = _read_faqs()
    new_items = [it for it in items if it.get("id") != faq_id]
    if len(new_items) == len(items):
        raise HTTPException(404, "FAQ no encontrada")
    _write_faqs(new_items)
    return {"deleted": faq_id}

@app.post("/reload")
def reload_data():
    """Reconstruye el índice TF-IDF en caliente sin reiniciar el servidor"""
    global X, QUESTIONS, ANSWERS
    
    # Leer FAQs actualizadas
    faqs = _read_faqs()
    QUESTIONS = [it["q"].strip() for it in faqs]
    ANSWERS = [it["a"].strip() for it in faqs]
    
    # Reconstruir índice
    X = pipe.fit_transform(QUESTIONS)
    
    # Guardar artefactos actualizados
    joblib.dump({"X": X, "questions": QUESTIONS, "answers": ANSWERS}, FAQS_PATH)
    
    return {"status": "reloaded", "items": len(QUESTIONS)}
