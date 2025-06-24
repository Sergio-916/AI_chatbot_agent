from google import genai
from dotenv import load_dotenv
import psycopg2.extras
import os

from backend.databases.postgre_db import get_db_connection
from backend.services.ollama_service import get_text_embedding

load_dotenv()


api_key = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=api_key)


EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL")


def save_embedding_to_db(text: str, embedding: list[float], metadata: dict = None):
    """
    Saves text and its embedding to the PostgreSQL database.
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        jsonb_metadata = (
            psycopg2.extras.Json(metadata) if metadata is not None else None
        )
        # SQL query for data insertion
        # psycopg2 automatically converts a Python list to the PostgreSQL vector format
        # psycopg2.extras.Json is for JSONB, but in this case psycopg2 handles dict on its own
        cur.execute(
            "INSERT INTO items_3 (content, embedding, metadata) VALUES (%s, %s, %s) RETURNING id;",
            (text, embedding, jsonb_metadata),
        )
        item_id = cur.fetchone()[0]
        conn.commit()
        print(
            f"Text and embedding for '{text[:30]}...' successfully saved with ID: {item_id}"
        )
        return item_id
    except Exception as e:
        print(f"Error saving embedding to DB: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            cur.close()
            conn.close()


def find_similar_items(query_text: str, top_k: int = 5) -> list[dict]:
    """
    Finds the most similar items in the database based on vector similarity.
    """
    conn = None
    try:
        query_embedding = get_text_embedding(query_text)
        if not query_embedding:
            print("Failed to get embedding for the query.")
            return []

        conn = get_db_connection()
        cur = conn.cursor()

        # Query for cosine similarity search
        # `<=>` is the cosine distance operator in pgvector.
        # The smaller the distance, the greater the similarity.
        # ORDER BY embedding <=> %s ASC - sort by increasing distance (i.e., by decreasing similarity)
        cur.execute(
            """
            SELECT id, content, metadata, embedding <=> %s::vector AS distance
            FROM items_3
            ORDER BY distance ASC
            LIMIT %s;
            """,
            (query_embedding, top_k),
        )

        results = cur.fetchall()

        # Convert results to a list of dictionaries for convenience
        similar_items = []
        for row in results:
            item_id, content, metadata, distance = row
            similar_items.append(
                {
                    "id": item_id,
                    "content": content,
                    "metadata": metadata,
                    "distance": distance,
                }
            )

        print(f"Found {len(similar_items)} similar items for query: '{query_text}'")
        # print(f"Found similar_items: '{similar_items.get('content')}'")
        for content in similar_items:
            print(f"Found similar_items: {content.get('content')}")

        return similar_items

    except Exception as e:
        print(f"Error searching for similar items: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            cur.close()
            conn.close()


# Example usage:
if __name__ == "__main__":
    sample_text = "Example text for vectorization and saving to the database."

    print(f"Generating embedding for: '{sample_text}'")
    embedding = get_text_embedding(sample_text)

    if embedding:
        print(f"Embedding obtained. Dimension: {len(embedding)}")
        print(
            f"First 5 embedding values: {embedding[:5]}"
        )  # Can be uncommented for debugging

        try:
            # Metadata can be any dictionary you want to save
            item_metadata = {"source": "manual_input", "category": "test"}
            save_embedding_to_db(sample_text, embedding, item_metadata)
        except Exception as e:
            print(f"Failed to save data to DB: {e}")
    else:
        print("Failed to get embedding.")
