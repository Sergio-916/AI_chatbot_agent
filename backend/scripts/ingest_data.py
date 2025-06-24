# backend/ingest_data.py

import json
import concurrent.futures
import os
import sys
import uuid

# Настройка путей для корректных импортов
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(project_root)

# Импортируем функции из наших модулей
from backend.services.google_vectorise import save_embedding_to_db
from backend.services.ollama_service import get_text_embedding
from backend.databases.postgre_db import create_items_table


def _get_processed_text_from_message_field(
    message_content_field,
) -> str:  # Fixed typo in function name
    """
    Extracts and combines text from the message's 'text' field.

    """
    if not message_content_field:
        return ""
    if isinstance(message_content_field, str):
        return message_content_field.strip()
    elif isinstance(message_content_field, list):
        parts = []
        for item in message_content_field:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
        return " ".join(parts).strip()
    return ""


def process_message_item(message_data, index, title):
    """
    Processes a single message using the full thread context.
    """
    message_id = message_data.get("id")
    if not message_id:
        return False  # Skip messages without ID

    if message_data.get("type") != "message" or not message_data.get("text"):
        return False  # Skip non-messages or empty

    text_to_embed = _get_processed_text_from_message_field(message_data.get("text"))

    if not text_to_embed or len(text_to_embed) < 3:
        print(f"Skipping message ID {message_id}: text for embedding is too short.")
        return False

    metadata = {
        "message_id": message_id,
        "title": title,
        "img_name": message_data.get("photo"),
        "date": message_data.get("date"),
        "from": message_data.get("from"),
        "reply_to_message_id": message_data.get("reply_to_message_id"),
    }

    try:
        embedding = get_text_embedding(text_to_embed)
        if embedding:
            original_text = _get_processed_text_from_message_field(
                message_data.get("text")
            )
            save_embedding_to_db(original_text, embedding, metadata)
            return True
        else:
            print(f"Skipped message ID {message_id}: failed to obtain embedding.")
            return False
    except Exception as e:
        print(f"Error processing message ID {message_id} (index {index}): {e}")
        return False


def ingest_messages_from_json(json_file_path: str):
    """
    Reads messages from JSON, builds context, and saves embeddings to the DB.
    """
    if not os.path.exists(json_file_path):
        print(f"Error: File not found at path: {json_file_path}")
        return

    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    title = data.get("name", data.get("title", "Unknown Chat"))
    messages_data = data.get("messages", [])

    if not isinstance(messages_data, list):
        print("Error: JSON file must contain a list of messages.")
        return

    print(f"Found {len(messages_data)} messages to process.")
    try:
        create_items_table()
    except Exception as e:
        print(f"Failed to prepare DB table: {e}")
        return

    successful_imports = 0
    failed_imports = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        future_to_message = {
            executor.submit(process_message_item, msg_data, i, title): msg_data.get(
                "id", f"N/A_idx_{i}"
            )
            for i, msg_data in enumerate(messages_data)
        }
        for future in concurrent.futures.as_completed(future_to_message):
            message_id_info = future_to_message[future]
            try:
                if future.result():
                    successful_imports += 1
                else:
                    failed_imports += 1
            except Exception as exc:
                print(f"Message {message_id_info} caused an exception: {exc}")
                failed_imports += 1

    print(
        f"\nProcessing complete. Successfully saved: {successful_imports}, skipped/errors: {failed_imports}."
    )


if __name__ == "__main__":
    json_path = os.path.join(os.path.dirname(__file__), "..", "data", "russians.json")
    print(f"Starting data loading from {json_path}...")
    ingest_messages_from_json(
        json_path
    )  # Corrected typo in "ingest_messages_from_json"
    print("Загрузка данных завершена.")  # Corrected typo in "завершена"
    print("Data loading finished.")
