# RAG Query Application

A Retrieval Augmented Generation (RAG) application that allows users to upload documents, process them into vector embeddings, and query them using natural language.

## Project Structure

- `backend/`: FastAPI backend with PostgreSQL + pgvector for vector storage
- `frontend/`: Next.js frontend with React and Tailwind CSS
- `config/`: Configuration files for the application

## Features

- Document upload and processing
- Vector embedding generation using OpenAI
- Semantic search using pgvector
- Natural language querying with context-aware responses
- Modern, responsive UI

## Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL with pgvector extension
- OpenAI API key
- Poetry (recommended) or pip for Python dependency management

## Getting Started

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Option 1: Using Poetry (Recommended)
```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

2. Option 2: Using pip and venv
```bash
# Create and activate a virtual environment
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Set up the database:
```bash
# Make sure PostgreSQL is running and pgvector extension is installed
psql -U postgres -c "CREATE DATABASE doc_query;"
psql -U postgres -d doc_query -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

5. Run the backend server:
```bash
# If using Poetry
poetry run uvicorn app.main:app --reload

# If using venv
uvicorn app.main:app --reload
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Run the development server:
```bash
npm run dev
# or
yarn dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## License

MIT 