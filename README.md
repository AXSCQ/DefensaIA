# Chatbot de FAQs (TF-IDF + FastAPI + Web)
Chatbot sencillo y defendible (30 min) que responde FAQs por **similitud TF-IDF + coseno**.  
Incluye: construcción de índice, **API FastAPI** y **demo web**.

## 1) Requisitos
- Python 3.10+ (recomendado 3.10–3.12)
- Pip
- (Opcional) Navegador moderno (Chrome/Firefox/Edge)

## 2) Clonado
```bash
git clone <URL_DE_TU_REPOSITORIO>.git
cd ia-faq-bot


python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

[
  {"q": "¿Qué es inteligencia artificial?", "a": "Campo que diseña sistemas capaces de realizar tareas que normalmente requieren inteligencia humana."},
  {"q": "¿Qué es TF-IDF?", "a": "Representación de texto que pondera términos por frecuencia en el documento y rareza en el corpus."},
  {"q": "¿Cómo funciona el bot?", "a": "Vectoriza la consulta y busca la pregunta más similar por similitud coseno."}
]

comando para ocontruir el indice
python train_index.py


lo que se contruye


Esto genera (ignorados por git):

tfidf_pipe.joblib (vectorizador)

faqs_texts.joblib (matriz X y textos)

levantar la api 

uvicorn api:app --reload

Swagger: http://127.0.0.1:8000/docs

Probar POST /ask con {"query":"¿Qué es TF-IDF?"}


## 7) Demo web (cliente)
- Opción A — Servidor estático (recomendado)

cd web
python -m http.server 5500

Abrir: http://127.0.0.1:5500/index.html


8) ¿Cómo funciona?

TF-IDF convierte cada pregunta del corpus en un vector (palabras informativas pesan más).

La consulta del usuario se vectoriza igual.

Similitud coseno compara la consulta con todas las preguntas; devolvemos la de mayor score.

Si el score < umbral (CONFIDENCE_THRESHOLD), el bot no inventa: pide reformular.

9) Parámetros clave

CONFIDENCE_THRESHOLD (en api.py, default 0.25): sube para ser más estricto.

ngram_range (en train_index.py, default (1,2)): aumenta a (1,3) si quieres captar frases más largas.

data/stopwords_es.txt (opcional): lista de stopwords para limpiar ruido.



ia-faq-bot/
├─ requirements.txt
├─ data/
│  ├─ faqs.json
│  └─ stopwords_es.txt     # opcional
├─ train_index.py
├─ api.py
├─ web/
│  └─ index.html
└─ (generados)
   ├─ tfidf_pipe.joblib
   └─ faqs_texts.joblib

# instalar
pip install -r requirements.txt

# entrenar índice
python train_index.py

# API
uvicorn api:app --reload

# web
cd web && python -m http.server 5500


12) Troubleshooting

CORS o bloqueo al abrir index.html
Usa el servidor local (python -m http.server 5500).

Puerto ocupado
uvicorn api:app --reload --port 8001 o python -m http.server 5501.

Cambiaste FAQs y no se refleja
Vuelve a correr python train_index.py.

Acentos/ruido
Añade stopwords (data/stopwords_es.txt) y re-entrena.



---

¿Quieres que además agregue un **Dockerfile** y comandos `docker build/run` para tener una demo “todo en uno” sin instalar Python en la máquina destino?
