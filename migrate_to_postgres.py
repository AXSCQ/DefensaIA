#!/usr/bin/env python3
import json
import psycopg2
import uuid
from pathlib import Path

# Configuración de la base de datos
DB_NAME = "DefensaIA"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"

# Ruta al archivo JSON
JSON_PATH = Path("data/faqs.json")

def migrate_json_to_postgres():
    print("Iniciando migración de datos JSON a PostgreSQL...")
    
    # Cargar datos del archivo JSON
    try:
        faqs = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        print(f"Cargados {len(faqs)} FAQs desde el archivo JSON.")
    except Exception as e:
        print(f"Error al cargar el archivo JSON: {e}")
        return False
    
    # Conectar a la base de datos
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.autocommit = True
        cursor = conn.cursor()
        print("Conexión a PostgreSQL establecida.")
    except Exception as e:
        print(f"Error al conectar a PostgreSQL: {e}")
        return False
    
    # Limpiar tablas existentes
    try:
        cursor.execute("DELETE FROM consulta;")
        cursor.execute("DELETE FROM vector_tfidf;")
        cursor.execute("DELETE FROM faq;")
        print("Tablas limpiadas correctamente.")
    except Exception as e:
        print(f"Error al limpiar tablas: {e}")
        return False
    
    # Insertar FAQs en la base de datos
    for faq in faqs:
        try:
            # Asegurarse de que el ID sea un UUID válido
            try:
                faq_id = uuid.UUID(faq["id"])
            except (ValueError, KeyError):
                # Si el ID no es válido o no existe, generar uno nuevo
                faq_id = uuid.uuid4()
                faq["id"] = str(faq_id)
            
            cursor.execute(
                "INSERT INTO faq (id, q, a) VALUES (%s, %s, %s)",
                (str(faq_id), faq["q"], faq["a"])
            )
            print(f"FAQ insertada: {faq['q'][:30]}...")
        except Exception as e:
            print(f"Error al insertar FAQ: {e}")
    
    # Cerrar conexión
    cursor.close()
    conn.close()
    print("Migración completada exitosamente.")
    return True

if __name__ == "__main__":
    migrate_json_to_postgres()
