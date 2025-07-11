# AI Chatbot Agent: Knowledge Explorer with RAG

![Project is under active development]

The AI Chatbot Agent is an intelligent system designed to find, organize, and summarize information on a particular topic. Utilizing a **Retrieval-Augmented Generation (RAG)** architecture, this chatbot retrieves relevant data from saved Telegram chats and builds cohesive discussion chains to generate accurate and comprehensive answers.

---

## ✨ Key Features

* **Topical Search**: Quickly find and organize information on a specified subject.
* **Contextual Responses**: Generate detailed and summarized answers based on relevant documents extracted from the knowledge base.
* **Telegram Integration**: Uses Telegram chat history as the primary data source.
* **RAG Architecture**: Combines information retrieval and response generation to enhance accuracy and relevance.
* **Full Stack**: A complete solution with separate Frontend and Backend components.
* **Persistent Storage**: Utilizes a PostgreSQL vector database for efficient storage and retrieval of embeddings.

---

## 🚀 System Architecture

The Chatbot Agent consists of two main components:

### Frontend (UI)

* User interface developed with **React**.
* Provides an intuitive chat interface for sending requests and receiving responses from the AI agent.

### Backend (API)

* API server built on **FastAPI**.
* Handles requests from the Frontend, manages interaction with the RAG system, and sends responses back to the user.
* Implements logic for request validation and LLM interaction.

### RAG System

The core of the agent is the RAG system, built on a **PostgreSQL vector database**. It ensures efficient storage and rapid retrieval of document vector representations.

---

## ⚙️ How It Works

Interaction with the AI Chatbot Agent occurs as follows:

1.  **User Request**: The user sends a request via the Frontend chat interface.
2.  **Request Reception & Validation**: The Backend receives the request and performs initial validation, checking its relevance to the system's main topic.
3.  **Request Vectorization**: The validated request is vectorized using an Ollama embedding model.
4.  **Relevant Document Search**: The vectorized request is used to find the most relevant documents in the PostgreSQL vector database.
5.  **Context Building**: An extended context is formed based on the retrieved documents and complete discussion chains from the Telegram history.
6.  **LLM Response Generation**: The full context is sent to the LLM (Large Language Model) agent to generate a concise and informative response.
7.  **Response Return**: The LLM agent returns the generated response to the Backend, which then forwards it to the Frontend for display to the user.
8.  **Logging**: All requests and responses are saved in MD files for future reference and logging.

---

## 🛠️ Data Preparation (Initialization Phase)

For the RAG system to function, preliminary data preparation is required:

1.  **Export Telegram Chat History**: Export the necessary Telegram chat history in JSON format.
2.  **Add Messages to Vector DB**: Use the project's scripts to load the exported messages into the PostgreSQL vector database. During this process, messages will be vectorized using the chosen Ollama embedding model.

---

## 📦 Installation and Setup (Proposed Structure)

This section will include detailed instructions for setting up and running the project.

### Requirements

* Python 3.9+
* Node.js 18+
* Docker (recommended)
* Ollama

### Installation Steps

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/sergio-916/chatbot_integration.git](https://github.com/sergio-916/chatbot_integration.git)
    cd chatbot_integration
    ```
2.  **Backend Setup:**
    ```bash
    cd backend
    uv sync
    uv venv # Create a virtual environment
    source .venv/bin/activate # Linux/macOS
    # .venv\Scripts\activate # Windows (uncomment for Windows)
    # Add environment variables, e.g.:
    # DB_HOST=""
    # DB_NAME="postgres"
    # DB_USER="postgres"
    # DB_PASSWORD=""    
    # And other necessary variables...
    # Run Alembic migrations (if any)
    # alembic upgrade head
    ```
3.  **Frontend Setup:**
    ```bash
    cd ../frontend
    npm install # or yarn install
    cp .env.example .env # Create a .env file and configure it
    # VITE_BACKEND_URL=http://localhost:8000
    ```
4.  **Run Ollama:**
    [Instructions for installing and running Ollama, downloading a model, e.g., `paraphrase-multilingual:278m`]
    ```bash
    ollama run paraphrase-multilingual:278m # or another embedding model
    ```
5.  **Database Initialization (Preparation Phase):**
    [Instructions for running scripts to export Telegram data and load it into the vector DB]
    ```bash
    # Example: python scripts/ingest_data.py
    # Example: python scripts/postgre_db.py
    ```
6.  **Start Backend:**
    ```bash
    cd backend
    uvicorn main:app --reload # or gunicorn for production
    ```
7.  **Start Frontend:**
    ```bash
    cd frontend
    npm run dev # or yarn dev
    ```

---

## 🤝 Contributing

We welcome any suggestions and contributions to the project's development! Please refer to [`CONTRIBUTING.md`](CONTRIBUTING.md) (if such a file exists) for more detailed information.

---
Developed by [Sergio Shpak](https://github.com/sergio-916).
## 📄 License

This project is distributed under the MIT License.