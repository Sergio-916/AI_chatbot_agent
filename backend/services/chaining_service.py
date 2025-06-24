import os
from datetime import datetime
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(project_root)

from backend.databases.postgre_db import get_db_connection


def get_chain(item):
    """
    Reconstructs a conversation thread from a PostgreSQL database. Given a specific message item,
    it queries the database for other messages sharing the same title and attempts
    to build a complete chain of related messages by identifying the root message and then collecting
    all messages belonging to that thread. The function returns a list of these messages, sorted by date,
    providing a chronological view of the conversation"""

    current_id = item.get("id")
    current_title = item.get("metadata").get("title")
    original_message_id = item.get("metadata", {}).get("message_id")

    conn = get_db_connection()

    cur = conn.cursor()

    query = """
        (SELECT
        id,
        content,
        metadata->>'title' AS title,
        metadata->>'message_id' AS message_id,
        metadata->>'reply_to_message_id' AS reply_to_message_id,
        metadata->>'date' AS date,
        metadata->>'from' AS author
        FROM items_3
        WHERE
        id < %s AND metadata->>'title' = %s 
        ORDER BY id DESC
        LIMIT 1000)

        UNION ALL

        (SELECT
            id,
            content,
            metadata->>'title' AS title,
            metadata->>'message_id' AS message_id,
            metadata->>'reply_to_message_id' AS reply_to_message_id,
            metadata->>'date' AS date,
            metadata->>'from' AS author
        FROM items_3
        WHERE
            id >= %s AND metadata->>'title' = %s 
        ORDER BY id ASC
        LIMIT 1000)        
"""

    cur.execute(query, (current_id, current_title, current_id, current_title))
    results = cur.fetchall()
    conn.close()

    messages = []
    for row in results:
        msg = {
            "id": row[0],
            "content": row[1],
            "title": row[2],
            "message_id": int(row[3]),
            "reply_to_message_id": int(row[4]) if row[4] else None,
            "date": datetime.fromisoformat(row[5]) if row[5] else None,
            "author": row[6],
        }
        messages.append(msg)

    id_to_msg = {msg["message_id"]: msg for msg in messages}

    def find_root(msg_id):
        current = id_to_msg.get(msg_id)
        if not current:
            return msg_id

        while current and current["reply_to_message_id"] is not None:
            parent_id = current["reply_to_message_id"]
            if parent_id in id_to_msg:
                current = id_to_msg[parent_id]
            else:
                break
        return current["message_id"] if current else msg_id

    root_id = find_root(original_message_id)

    thread = []
    for msg in messages:
        if find_root(msg["message_id"]) == root_id:
            thread.append(msg)

    thread.sort(key=lambda m: m["date"] if m["date"] else datetime.min)

    def return_chain_thread(root_id, thread):
        message_chain = [{"root_id": root_id}]
        for msg in thread:
            message_chain.append(
                {
                    "author": msg.get("author", "Unknown"),
                    "content": msg.get("content", "No content"),
                    "date": msg.get("date", "No date"),
                }
            )
        return message_chain

    return return_chain_thread(root_id, thread)
