-- Script para limpiar todas las tablas de la base de datos DefensaIA
-- Eliminar primero las tablas con claves foráneas

-- Desactivar temporalmente las restricciones de clave foránea
SET session_replication_role = 'replica';

-- Limpiar la tabla consulta (tiene referencia a faq)
DELETE FROM consulta;

-- Limpiar la tabla vector_tfidf (tiene referencia a faq)
DELETE FROM vector_tfidf;

-- Limpiar la tabla faq
DELETE FROM faq;

-- Reactivar las restricciones de clave foránea
SET session_replication_role = 'origin';

-- Confirmar que las tablas están vacías
SELECT 'Tabla consulta: ' || COUNT(*) AS consulta_count FROM consulta;
SELECT 'Tabla vector_tfidf: ' || COUNT(*) AS vector_tfidf_count FROM vector_tfidf;
SELECT 'Tabla faq: ' || COUNT(*) AS faq_count FROM faq;
