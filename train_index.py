import json
import joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline

DATA = Path("data/faqs.json")
PIPE_PATH = Path("tfidf_pipe.joblib")
FAQS_PATH = Path("faqs_texts.joblib")

# (Opcional) stopwords ES
STOPWORDS_FILE = Path("data/stopwords_es.txt")
stopwords_es = None
if STOPWORDS_FILE.exists():
    stopwords_es = [w.strip() for w in STOPWORDS_FILE.read_text(encoding="utf-8").splitlines() if w.strip()]

# 1) Cargar FAQs
faqs = json.loads(DATA.read_text(encoding="utf-8"))
questions = [it["q"].strip() for it in faqs]
answers   = [it["a"].strip() for it in faqs]

# 2) Vectorizador
pipe = Pipeline([
    ("tfidf", TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        stop_words=stopwords_es  # None si no hay archivo
    ))
])

# 3) Ajustar y transformar
X = pipe.fit_transform(questions)

# 4) Guardar artefactos
joblib.dump(pipe, PIPE_PATH)
joblib.dump({"X": X, "questions": questions, "answers": answers}, FAQS_PATH)

print("Índice TF-IDF creado y guardado.")
print(f"Preguntas cargadas: {len(questions)}")
