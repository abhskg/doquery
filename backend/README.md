# RAG Query API Backend

This is the backend for the RAG Query application, which allows users to upload documents, process them into embeddings, and query them using natural language.

## Setup

### Option 1: Using Poetry (Recommended)

1. Install Poetry if you don't have it already:
```bash
# On Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# On macOS/Linux
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Activate the virtual environment:
```bash
poetry shell
```

4. Copy `.env.example` to `.env` and update the values:
```bash
cp .env.example .env
```

5. Set up the database:
```bash
# Make sure PostgreSQL is running and pgvector extension is installed
psql -U postgres -c "CREATE DATABASE doc_query;"
psql -U postgres -d doc_query -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Option 2: Using pip and venv

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and update the values:
```bash
cp .env.example .env
```

5. Set up the database:
```bash
# Make sure PostgreSQL is running and pgvector extension is installed
psql -U postgres -c "CREATE DATABASE doc_query;"
psql -U postgres -d doc_query -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

## Model Provider Configuration

The application supports multiple model providers for generating embeddings and answering queries:

### OpenAI (Default)

To use OpenAI's models (default configuration):

```
MODEL_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key
EMBEDDING_MODEL=text-embedding-3-small
COMPLETION_MODEL=gpt-4o
```

### Local Models

To use locally hosted models (requires a local model server):

```
MODEL_PROVIDER=local
LOCAL_MODEL_SERVER_URL=http://localhost:8080
LOCAL_EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
LOCAL_COMPLETION_MODEL=mistralai/Mistral-7B-Instruct-v0.2
```

You can use any model server that implements the OpenAI-compatible API:
- [llama.cpp server](https://github.com/ggerganov/llama.cpp)
- [text-embeddings-inference](https://github.com/huggingface/text-embeddings-inference)
- [vLLM](https://github.com/vllm-project/vllm)
- [Ollama](https://github.com/ollama/ollama)

### HuggingFace

To use HuggingFace's hosted models:

```
MODEL_PROVIDER=huggingface
HUGGINGFACE_API_KEY=your_huggingface_api_key
HUGGINGFACE_EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
HUGGINGFACE_COMPLETION_MODEL=mistralai/Mistral-7B-Instruct-v0.2
```

## Running the Application

```bash
# If using Poetry
poetry run uvicorn app.main:app --reload

# If using venv
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000.

## API Documentation

Once the application is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

### Code Formatting

If you're using Poetry, the project includes development dependencies for code formatting:

```bash
# Format code
poetry run black .

# Sort imports
poetry run isort .

# Run type checking
poetry run mypy .

# Run tests
poetry run pytest
``` 