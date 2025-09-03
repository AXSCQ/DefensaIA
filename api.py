from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import psycopg2
import psycopg2.extras
import pickle
import uuid
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any, Optional

# Configuración de la base de datos
DB_NAME = "DefensaIA"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"

# Rutas de archivos para artefactos del modelo
PIPE_PATH = Path("tfidf_pipe.joblib")
FAQS_PATH = Path("faqs_texts.joblib")

# Cargar artefactos
pipe = joblib.load(PIPE_PATH)
store = joblib.load(FAQS_PATH)
X = store["X"]; QUESTIONS = store["questions"]; ANSWERS = store["answers"]; FAQ_IDS = store["ids"]

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

# Funciones auxiliares para CRUD con PostgreSQL
def get_db_connection():
    """Establece y retorna una conexión a la base de datos"""
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.autocommit = True
    return conn

def _read_faqs():
    """Lee las FAQs desde la base de datos PostgreSQL"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT id, q, a FROM faq")
    faqs = [dict(row) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return faqs

def _add_faq(item):
    """Añade una nueva FAQ a la base de datos"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO faq (id, q, a) VALUES (%s, %s, %s) RETURNING id",
        (item["id"], item["q"], item["a"])
    )
    faq_id = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return faq_id

def _update_faq(faq_id, item):
    """Actualiza una FAQ existente en la base de datos"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE faq SET q = %s, a = %s WHERE id = %s RETURNING id",
        (item["q"], item["a"], faq_id)
    )
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None

def _delete_faq(faq_id):
    """Elimina una FAQ de la base de datos"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Primero eliminar los vectores TF-IDF asociados
    cursor.execute("DELETE FROM vector_tfidf WHERE faq_id = %s", (faq_id,))
    
    # Eliminar referencias en la tabla consulta
    cursor.execute("DELETE FROM consulta WHERE faq_id = %s", (faq_id,))
    
    # Luego eliminar la FAQ
    cursor.execute("DELETE FROM faq WHERE id = %s RETURNING id", (faq_id,))
    result = cursor.fetchone()
    
    # Confirmar los cambios
    conn.commit()
    cursor.close()
    conn.close()
    return result is not None

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
    
    # Transformar la consulta
    v = pipe.transform([q])
    scores = cosine_similarity(v, X).ravel()
    ix = int(scores.argmax())
    score = float(scores[ix])
    
    # Preparar respuesta
    if score < CONFIDENCE_THRESHOLD:
        response = {
            "answer": "No estoy seguro. ¿Puedes reformular o ser más específico?",
            "match_question": "",
            "score": score
        }
        matched_faq_id = None
    else:
        response = {
            "answer": ANSWERS[ix], 
            "match_question": QUESTIONS[ix], 
            "score": score
        }
        matched_faq_id = FAQ_IDS[ix] if ix < len(FAQ_IDS) else None
    
    # Registrar la consulta en la base de datos
    try:
        consulta_id = str(uuid.uuid4())
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO consulta (id, texto, timestamp, score, faq_id) VALUES (%s, %s, CURRENT_TIMESTAMP, %s, %s)",
            (consulta_id, q, score, matched_faq_id)
        )
        cursor.close()
        conn.close()
    except Exception as e:
        # Ignorar errores en el registro de consultas
        pass
    
    return response

@app.post("/topk", response_model=TopKOut)
def topk(payload: AskIn, k: int = 5):
    """Devuelve las k respuestas más similares a la consulta"""
    q = (payload.query or "").strip()
    v = pipe.transform([q])
    scores = cosine_similarity(v, X).ravel()
    idx = scores.argsort()[::-1][:k]
    
    # Preparar resultados
    results = [
        {"question": QUESTIONS[i], "answer": ANSWERS[i], "score": float(scores[i])}
        for i in idx
    ]
    
    # Registrar la consulta en la base de datos
    try:
        consulta_id = str(uuid.uuid4())
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obtener el ID de la FAQ con mayor puntuación
        top_idx = idx[0] if len(idx) > 0 else None
        matched_faq_id = FAQ_IDS[top_idx] if top_idx is not None and top_idx < len(FAQ_IDS) else None
        top_score = float(scores[top_idx]) if top_idx is not None else 0.0
        
        cursor.execute(
            "INSERT INTO consulta (id, texto, timestamp, score, faq_id) VALUES (%s, %s, CURRENT_TIMESTAMP, %s, %s)",
            (consulta_id, q, top_score, matched_faq_id)
        )
        cursor.close()
        conn.close()
    except Exception as e:
        # Ignorar errores en el registro de consultas
        pass
        
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
    
    # Generar ID único si no se proporciona
    new_item = item.dict()
    if not new_item.get("id"):
        new_item["id"] = str(uuid.uuid4())
    
    # Insertar en la base de datos
    try:
        _add_faq(new_item)
        return new_item
    except Exception as e:
        raise HTTPException(500, f"Error al crear FAQ: {str(e)}")

@app.put("/faqs/{faq_id}")
def update_faq(faq_id: str, item: FaqItem):
    """Actualiza una FAQ existente"""
    # Verificar que la FAQ existe
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM faq WHERE id = %s", (faq_id,))
    existing_faq = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not existing_faq:
        raise HTTPException(404, "FAQ no encontrada")
    
    # Actualizar FAQ
    update_data = {
        "q": item.q if item.q else existing_faq["q"],
        "a": item.a if item.a else existing_faq["a"],
        "id": faq_id
    }
    
    if _update_faq(faq_id, update_data):
        return update_data
    else:
        raise HTTPException(500, "Error al actualizar FAQ")

@app.delete("/faqs/{faq_id}")
def delete_faq(faq_id: str):
    """Elimina una FAQ"""
    # Eliminar de la base de datos
    if _delete_faq(faq_id):
        return {"deleted": faq_id}
    else:
        raise HTTPException(404, "FAQ no encontrada")

@app.post("/reload")
def reload_data():
    """Reconstruye el índice TF-IDF en caliente sin reiniciar el servidor"""
    global X, QUESTIONS, ANSWERS, FAQ_IDS
    
    # Cargar stopwords (opcional)
    stopwords_file = Path("stopwords_es.txt")
    stopwords_es = None
    if stopwords_file.exists():
        stopwords_es = [w.strip() for w in stopwords_file.read_text(encoding="utf-8").splitlines() if w.strip()]
    
    # Leer FAQs actualizadas desde PostgreSQL
    faqs = _read_faqs()
    FAQ_IDS = [str(it["id"]) for it in faqs]
    QUESTIONS = [it["q"].strip() for it in faqs]
    ANSWERS = [it["a"].strip() for it in faqs]
    
    # Reconstruir índice
    # Actualizar configuración del vectorizador si hay stopwords
    if stopwords_es:
        pipe.named_steps['tfidf'].stop_words = stopwords_es
    
    X = pipe.fit_transform(QUESTIONS)
    
    # Guardar artefactos actualizados
    joblib.dump({"X": X, "questions": QUESTIONS, "answers": ANSWERS, "ids": FAQ_IDS}, FAQS_PATH)
    
    # Actualizar vectores en la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Limpiar vectores antiguos
    cursor.execute("DELETE FROM vector_tfidf")
    
    # Insertar nuevos vectores
    for i, faq_id in enumerate(FAQ_IDS):
        # Serializar el vector TF-IDF usando pickle
        vector_bytes = pickle.dumps(X[i].toarray())
        cursor.execute(
            "INSERT INTO vector_tfidf (faq_id, vector_data) VALUES (%s, %s)",
            (faq_id, psycopg2.Binary(vector_bytes))
        )
    
    # Cerrar conexión
    conn.commit()
    cursor.close()
    conn.close()
    
    # Registrar consulta para fines de auditoría
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO consulta (id, texto, timestamp) VALUES (%s, %s, CURRENT_TIMESTAMP)",
            (str(uuid.uuid4()), "[SYSTEM] Recarga del índice TF-IDF")
        )
        cursor.close()
        conn.close()
    except Exception:
        # Ignorar errores en el registro de auditoría
        pass
    
    return {"status": "reloaded", "items": len(QUESTIONS)}
