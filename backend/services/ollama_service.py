import ollama

model = "paraphrase-multilingual:278m"
# model = "nomic-embed-text:v1.5"


def get_text_embedding(text: str):
    response = ollama.embeddings(model=model, prompt=text)
    return response["embedding"]
