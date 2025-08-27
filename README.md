# Sistema Inteligente de FAQs con TF-IDF y FastAPI

## Descripción General

Este proyecto implementa un sistema inteligente de preguntas frecuentes (FAQs) utilizando técnicas de Procesamiento de Lenguaje Natural (NLP) basadas en TF-IDF y similitud de coseno. El sistema es capaz de responder consultas de usuarios encontrando la pregunta más similar en su base de conocimiento y devolviendo la respuesta asociada.

**Características principales:**
- Vectorización TF-IDF para representación semántica de texto
- Búsqueda por similitud de coseno
- API RESTful completa con FastAPI
- CRUD para gestión dinámica de FAQs
- Reconstrucción de índice en caliente
- Interfaz web interactiva
- Umbral de confianza configurable

## Fundamentos Teóricos

### TF-IDF (Term Frequency-Inverse Document Frequency)

TF-IDF es una técnica estadística que evalúa la importancia de una palabra en un documento en relación con una colección de documentos. Combina dos métricas:

1. **TF (Term Frequency)**: Mide la frecuencia de aparición de un término en un documento.
2. **IDF (Inverse Document Frequency)**: Penaliza términos comunes en toda la colección y premia términos distintivos.

La fórmula general es: `TF-IDF(t,d,D) = TF(t,d) × IDF(t,D)`

Esta técnica permite representar textos como vectores numéricos donde las palabras más informativas tienen mayor peso.

### Similitud de Coseno

La similitud de coseno mide el ángulo entre dos vectores, proporcionando un valor entre -1 y 1 (aunque con TF-IDF suele estar entre 0 y 1). Cuanto más cercano a 1, mayor similitud semántica.

Fórmula: `cos(θ) = (A·B)/(||A||·||B||)`

En nuestro sistema, comparamos el vector de la consulta del usuario con los vectores de todas las preguntas en nuestra base de conocimiento.

## Requisitos

- Python 3.10+ (recomendado 3.10–3.12)
- Pip
- Navegador moderno (Chrome/Firefox/Edge)

## Instalación y Configuración

```bash
# Clonar repositorio
git clone <URL_DE_TU_REPOSITORIO>.git
cd ia-faq-bot

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Construir índice inicial
python train_index.py

# Iniciar API
uvicorn api:app --reload

# En otra terminal, iniciar servidor web
cd web
python -m http.server 5500
```

## Arquitectura del Sistema

### Componentes Principales

1. **Vectorizador TF-IDF**: Transforma texto en vectores numéricos
2. **Motor de Similitud**: Calcula similitud de coseno entre vectores
3. **API RESTful**: Gestiona consultas y administración de FAQs
4. **Base de Conocimiento**: Almacena pares pregunta-respuesta
5. **Interfaz Web**: Permite interacción con usuarios finales

### Estructura de Archivos

```
ia-faq-bot/
├─ requirements.txt      # Dependencias del proyecto
├─ data/
│  ├─ faqs.json         # Base de conocimiento (preguntas y respuestas)
│  └─ stopwords_es.txt  # Palabras vacías para filtrar (opcional)
├─ train_index.py       # Script para construir el índice TF-IDF
├─ api.py               # API FastAPI con endpoints
├─ web/
│  └─ index.html        # Interfaz de usuario
└─ (generados)
   ├─ tfidf_pipe.joblib # Modelo serializado
   └─ faqs_texts.joblib # Vectores y textos procesados
```

## Funcionalidades API

### Consulta de FAQs

- **POST /ask**: Responde a consultas de usuarios
  - Input: `{"query": "¿Qué es TF-IDF?"}`
  - Output: `{"answer": "...", "match_question": "...", "score": 0.95}`

- **POST /topk**: Devuelve las k respuestas más similares
  - Input: `{"query": "inteligencia"}`
  - Output: Lista de coincidencias ordenadas por similitud

### Gestión de FAQs (CRUD)

- **GET /faqs**: Lista todas las FAQs disponibles
- **POST /faqs**: Crea una nueva FAQ
  - Input: `{"q": "¿Nueva pregunta?", "a": "Nueva respuesta"}`
- **PUT /faqs/{id}**: Actualiza una FAQ existente
- **DELETE /faqs/{id}**: Elimina una FAQ
- **POST /reload**: Reconstruye el índice sin reiniciar el servidor

## Flujo de Procesamiento

1. **Entrenamiento**:
   - Carga de FAQs desde JSON
   - Vectorización TF-IDF de preguntas
   - Almacenamiento de vectores y modelo

2. **Consulta**:
   - Recepción de consulta de usuario
   - Vectorización de la consulta
   - Cálculo de similitud con todas las preguntas
   - Selección de respuesta más similar si supera umbral

3. **Administración**:
   - Modificación de FAQs mediante API
   - Reconstrucción de índice en caliente

## Parámetros Configurables

- **CONFIDENCE_THRESHOLD** (en api.py, default 0.25): Umbral mínimo de confianza para responder
- **ngram_range** (en train_index.py, default (1,2)): Tamaño de n-gramas para capturar frases
- **Stopwords**: Palabras a ignorar durante vectorización (data/stopwords_es.txt)

## Ventajas del Enfoque

1. **Eficiencia**: Algoritmo ligero que no requiere GPU ni grandes recursos
2. **Transparencia**: Funcionamiento explicable y resultados predecibles
3. **Mantenibilidad**: Fácil actualización de contenido sin conocimientos técnicos
4. **Adaptabilidad**: Funciona con cualquier conjunto de FAQs en cualquier idioma
5. **Control de calidad**: El umbral de confianza evita respuestas incorrectas

## Limitaciones y Trabajo Futuro

1. **Sensibilidad léxica**: Depende de coincidencia de palabras exactas
   - *Mejora propuesta*: Incorporar embeddings semánticos (Word2Vec, BERT)

2. **Sin contexto conversacional**: Cada consulta se procesa independientemente
   - *Mejora propuesta*: Implementar gestión de contexto y memoria a corto plazo

3. **Escalabilidad limitada**: Rendimiento puede degradarse con miles de FAQs
   - *Mejora propuesta*: Implementar búsqueda aproximada de vecinos más cercanos

## Solución de Problemas

- **CORS o bloqueo al abrir index.html**: Usa el servidor local (python -m http.server 5500)
- **Puerto ocupado**: Cambia los puertos (uvicorn api:app --port 8001)
- **Acentos/ruido**: Añade stopwords en data/stopwords_es.txt y reconstruye el índice

## Documentación API

Swagger UI disponible en: http://127.0.0.1:8000/docs

## Demo Web

Interfaz de usuario disponible en: http://127.0.0.1:5500/index.html



---
