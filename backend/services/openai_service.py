from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

model = os.getenv("OPENAI_MODEL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


client = OpenAI(api_key=OPENAI_API_KEY)


def get_response(user_query, context_prompt):
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that answers questions "
            "using the information provided in the context. "
            "If the information is not found, honestly state that you have no data to provide an answer.\n\n"
            f"Context:\n{context_prompt}",
        },
        {"role": "user", "content": user_query},
    ]

    response = client.chat.completions.create(
        model=model,
        # temperature=0.2,
        messages=messages,
    )

    return response.choices[0].message.content
