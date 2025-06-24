from google import genai
from dotenv import load_dotenv
import os
import sys
import time
from datetime import datetime

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(project_root)

from backend.services.google_vectorise import find_similar_items
from backend.services.openai_service import get_response
from backend.services.chaining_service import get_chain


load_dotenv()


api_key = os.getenv("GOOGLE_API_KEY")
llm_flag = os.getenv("llm_flag")

client = genai.Client(api_key=api_key)


def log_llm_interaction(question: str, response: str):
    """
    Logs the user's question and the LLM's response to a Markdown file.
    """
    log_file_path = "./data/Schools.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file_path, "a", encoding="utf-8") as f:
        f.write(f"## Interaction on {timestamp}\n\n")
        f.write(f"**Question:**\n{question}\n\n")
        f.write(f"**LLM Response:**\n{response}\n\n")
        f.write("---\n\n")


def validate_input(user_query: str) -> bool:
    prompt = f"""
    Check that the user query is related to schools in Argentina and system of education.
    query can contain only school name e.g. ILSE
    response: True or False
    
    User query: {user_query}
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    print(f"Модель ответила: '{response.text.strip()}'")
    return response.text.strip().lower() == "true"


def get_llm_response_with_context(user_query: str, top_k_context: int = 5) -> str:
    """
    Searches for relevant information in the database
    and uses it to generate an LLM response.
    """
    print(f"Searching for context for query: '{user_query}'")
    # Step 1: Find relevant context
    retrieved_items = find_similar_items(user_query, top_k=top_k_context)
    retrieved_items_for_print = []
    for item in retrieved_items:
        retrieved_items_for_print.append(item.get("content"))

    context_strings = []
    if retrieved_items:
        print(f"Found {len(retrieved_items)} relevant fragments.")

        for item in retrieved_items:
            context_strings.append(get_chain(item))
    else:
        print("Relevant context not found in the database.")

    context_prompt = ""
    if context_strings:
        context_prompt = (
            "\n\nAvailable context:\n"
            + "\n---\n".join([str(c) for c in context_strings])
            + "\n---\n"
        )
        context_prompt += "Use this context to answer the user's question. If the context does not contain the necessary information, state this."

    # Main system prompt
    system_instruction = """
    As the 'Argentine School Directory' assistant, 
    your primary goal is to deliver thorough and complete answers to questions by synthesizing 
    all pertinent information about schools in Argentina and particulary in Buenos Aires 
    from the provided context and the ongoing dialogue chains. 
    Crucially, ensure that no question remains unanswered without explanation. 
    If, after reviewing all available data, the information required to answer the question is not found, 
    you must explicitly declare that you do not possess the necessary data to formulate a response.
    If you list prices please add publication date for reference, if date is not relevant do not add it.
    Use Markdown formatting for the response.
    Answer in English.
    """

    full_prompt = f"{system_instruction}\n\nUser question: {user_query}{context_prompt}"

    start_time = time.time()
    if llm_flag == "openai":
        try:
            llm_response_text = get_response(user_query, context_prompt)
            log_llm_interaction(user_query, llm_response_text)
            return llm_response_text

        except Exception as e:
            log_llm_interaction(user_query, f"Error: {e}")
            print(f"Error generating LLM response: {e}")
            return "Sorry, an error occurred while getting the response."

    else:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=full_prompt,
        )

        end_time = time.time()
        llm_response_text = response.text
        # log_llm_interaction(user_query, llm_response_text)  # logging results into md file
        return llm_response_text, (end_time - start_time)


if __name__ == "__main__":
    rag_query_1 = "Need information on technical schools?"
    llm_response_1 = get_llm_response_with_context(rag_query_1, top_k_context=3)
    print(f"\nQuestion: {rag_query_1}")

    print(f"LLM Response {llm_flag}:\n{llm_response_1}")

    print("\n" + "=" * 50 + "\n")
