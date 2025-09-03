-- Crear extensión para UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Crear tabla faq
CREATE TABLE IF NOT EXISTS faq (
    id UUID PRIMARY KEY,
    q TEXT NOT NULL,
    a TEXT NOT NULL
);

-- Crear tabla vector_tfidf
CREATE TABLE IF NOT EXISTS vector_tfidf (
    faq_id UUID PRIMARY KEY REFERENCES faq(id),
    vector_data BYTEA NOT NULL
);

-- Crear tabla consulta
CREATE TABLE IF NOT EXISTS consulta (
    id UUID PRIMARY KEY,
    texto TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    score FLOAT,
    faq_id UUID REFERENCES faq(id)
);
