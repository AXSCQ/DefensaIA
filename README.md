# Sistema Inteligente de FAQs con TF-IDF, FastAPI y PostgreSQL

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
- Base de datos PostgreSQL para almacenamiento persistente
- Registro de consultas para análisis

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
- PostgreSQL 12+
- Navegador moderno (Chrome/Firefox/Edge)

## Instalación y Configuración

### 1. Preparación del entorno

```bash
# Clonar repositorio
git clone <URL_DE_TU_REPOSITORIO>.git
cd ia-faq-bot

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración de PostgreSQL

```bash
# Asegúrate de que PostgreSQL esté en ejecución
sudo systemctl status postgresql  # Verificar estado

# Crear base de datos (usando usuario postgres)
sudo -u postgres psql -c "CREATE DATABASE DefensaIA;"

# Crear tablas y estructura
python migrate_to_postgres.py  # Este script crea las tablas necesarias
```

### 3. Construir índice y ejecutar

```bash
# Construir índice inicial (ahora desde PostgreSQL)
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

### Estructura de Archivos y Base de Datos

### Archivos

```
.
├── web/                 # Interfaz web
│   └── index.html      # Cliente web simple
├── api.py              # API REST (FastAPI)
├── train_index.py      # Script para crear índice TF-IDF
├── tfidf_pipe.joblib   # Pipeline TF-IDF serializado
├── faqs_texts.joblib   # Vectores y textos serializados
├── migrate_to_postgres.py # Script de migración a PostgreSQL
├── stopwords_es.txt    # Palabras vacías en español (opcional)
├── requirements.txt    # Dependencias Python
└── README.md           # Documentación
```

### Estructura de la Base de Datos

```
DefensaIA (Base de datos PostgreSQL)
├─ faq                # Tabla principal de preguntas y respuestas
│  ├─ id (UUID)       # Identificador único
│  ├─ q (TEXT)        # Pregunta
│  └─ a (TEXT)        # Respuesta
├─ vector_tfidf       # Vectores TF-IDF para cada FAQ
│  ├─ faq_id (UUID)   # Referencia a faq.id
│  └─ vector_data (BYTEA) # Vector serializado
└─ consulta           # Registro de consultas realizadas
   ├─ id (UUID)       # Identificador único
   ├─ texto (TEXT)     # Texto de la consulta
   ├─ timestamp       # Fecha y hora
   ├─ score (FLOAT)    # Puntuación de similitud
   └─ faq_id (UUID)   # Referencia a la FAQ respondida
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
   - Carga de FAQs desde PostgreSQL
   - Vectorización TF-IDF de preguntas
   - Almacenamiento de vectores en la base de datos y modelo en disco

2. **Consulta**:
   - Recepción de consulta de usuario
   - Vectorización de la consulta
   - Cálculo de similitud con todas las preguntas
   - Selección de respuesta más similar si supera umbral
   - Registro de la consulta en la base de datos para análisis

3. **Administración**:
   - Modificación de FAQs mediante API (almacenadas en PostgreSQL)
   - Reconstrucción de índice en caliente con actualización de vectores en la BD

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
6. **Persistencia**: Almacenamiento en PostgreSQL para mayor seguridad y escalabilidad
7. **Análisis**: Registro de consultas para estudiar patrones de uso y mejorar el sistema

## Limitaciones y Trabajo Futuro

1. **Sensibilidad léxica**: Depende de coincidencia de palabras exactas
   - *Mejora propuesta*: Incorporar embeddings semánticos (Word2Vec, BERT)

2. **Sin contexto conversacional**: Cada consulta se procesa independientemente
   - *Mejora propuesta*: Implementar gestión de contexto y memoria a corto plazo

3. **Escalabilidad mejorable**: A pesar de usar PostgreSQL, el cálculo de similitud se realiza en memoria
   - *Mejora propuesta*: Implementar búsqueda aproximada de vecinos más cercanos o utilizar extensiones de PostgreSQL para búsqueda vectorial

4. **Análisis de datos**: El registro actual es básico
   - *Mejora propuesta*: Implementar dashboard de análisis con estadísticas de uso

## Solución de Problemas

- **CORS o bloqueo al abrir index.html**: Usa el servidor local (python -m http.server 5500)
- **Puerto ocupado**: Cambia los puertos (uvicorn api:app --port 8001)
- **Problemas de conexión a PostgreSQL**: Verifica credenciales y que el servicio esté activo
- **Error en migración**: Ejecuta `python migrate_to_postgres.py` para recrear las tablas
- **Acentos/ruido**: Añade stopwords en data/stopwords_es.txt y reconstruye el índice

## Documentación API

Swagger UI disponible en: http://127.0.0.1:8000/docs

## Demo Web

Interfaz de usuario disponible en: http://127.0.0.1:5500/index.html



---
