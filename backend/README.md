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