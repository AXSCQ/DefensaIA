import joblib
import psycopg2
import pickle
import re
import unicodedata
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer, strip_accents_unicode
from sklearn.pipeline import Pipeline

# Configuración de la base de datos
DB_NAME = "DefensaIA"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"

PIPE_PATH = Path("tfidf_pipe.joblib")
FAQS_PATH = Path("faqs_texts.joblib")

# Función para normalizar texto (no será serializada)
def preprocess_text(docs):
    """Preprocesa una lista de documentos: minúsculas, sin acentos, sin puntuación"""
    processed_docs = []
    for text in docs:
        # Convertir a minúsculas
        text = text.lower().strip()
        # Quitar acentos
        text = strip_accents_unicode(text)
        # Quitar signos/puntuación
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        processed_docs.append(text)
    return processed_docs

# Cargar stopwords ES
STOPWORDS_FILE = Path("stopwords_es.txt")
stopwords_es = None
if STOPWORDS_FILE.exists():
    stopwords_es = [w.strip() for w in STOPWORDS_FILE.read_text(encoding="utf-8").splitlines() if w.strip()]

# 1) Cargar FAQs desde PostgreSQL
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cursor = conn.cursor()
cursor.execute("SELECT id, q, a FROM faq")
faqs_data = cursor.fetchall()

# Preparar datos
faq_ids = [str(row[0]) for row in faqs_data]
questions = [row[1].strip() for row in faqs_data]
answers = [row[2].strip() for row in faqs_data]

# Documento a indexar: PREGUNTA + RESPUESTA (aumenta recall)
raw_docs = [f"{q} {a}" for q, a in zip(questions, answers)]

# Preprocesar documentos
docs = preprocess_text(raw_docs)

# 2) Vectorizador mejorado (sin preprocessor personalizado)
pipe = Pipeline([
    ("tfidf", TfidfVectorizer(
        lowercase=False,         # Ya lo hicimos en el preprocesamiento
        preprocessor=None,       # No usar preprocessor personalizado
        tokenizer=None,          # Usar tokenizador por defecto
        stop_words=stopwords_es, # Stopwords en español
        ngram_range=(1, 3),      # N-gramas de 1 a 3 palabras
        sublinear_tf=True,       # Escala logarítmica para term frequency
        min_df=1,                # Mínima frecuencia de documento
        max_df=0.95              # Máxima frecuencia de documento (evitar palabras muy comunes)
    ))
])

# 3) Ajustar y transformar usando preguntas + respuestas
X = pipe.fit_transform(docs)

# 4) Guardar artefactos
joblib.dump(pipe, PIPE_PATH)
joblib.dump({"X": X, "questions": questions, "answers": answers, "ids": faq_ids}, FAQS_PATH)

# 5) Guardar vectores en la base de datos
cursor.execute("DELETE FROM vector_tfidf")
for i, faq_id in enumerate(faq_ids):
    # Serializar el vector TF-IDF usando pickle
    vector_bytes = pickle.dumps(X[i].toarray())
    cursor.execute(
        "INSERT INTO vector_tfidf (faq_id, vector_data) VALUES (%s, %s)",
        (faq_id, psycopg2.Binary(vector_bytes))
    )

# Confirmar cambios y cerrar conexión
conn.commit()
cursor.close()
conn.close()

print("Índice TF-IDF creado y guardado.")
print(f"Preguntas cargadas: {len(questions)}")
print(f"Vectores almacenados en la base de datos: {len(faq_ids)}")
