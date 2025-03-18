# Database Setup for RAG Query API

This document provides instructions on how to set up and troubleshoot the database for the RAG Query API.

## Prerequisites

- PostgreSQL 12+ installed and running
- pgvector extension installed on your PostgreSQL server
- Python environment set up with required dependencies

## Quick Setup

Run the automated setup script:

```bash
# From the backend directory
python setup_db.py
```

This script will:
1. Create the database if it doesn't exist
2. Install the pgvector extension
3. Create all necessary tables

## Manual Setup

If the automated script fails, you can perform these steps manually:

### 1. Create the Database

```sql
CREATE DATABASE doc_query;
```

### 2. Install pgvector Extension

Connect to your database and run:

```sql
CREATE EXTENSION vector;
```

If this fails, you need to install the pgvector extension on your PostgreSQL server first:
- For Ubuntu/Debian: `sudo apt install postgresql-14-pgvector`
- For other systems, see: https://github.com/pgvector/pgvector

### 3. Create Database Tables

Run the initialization script:

```bash
# From the backend directory
python init_db.py
```

## Troubleshooting

### Check Database Connection

You can verify your database connection by visiting:
```
http://localhost:8000/api/v1/documents/db-check
```

This endpoint will provide information about:
- Database connection status
- Existence of required tables
- pgvector extension status
- Specific error messages if something is missing

### Common Issues

#### 1. "relation 'document' does not exist"

This means the database tables haven't been created. Run:
```bash
python init_db.py
```

#### 2. "could not connect to server"

Check that:
- PostgreSQL server is running
- Connection details in `.env` file are correct
- Network/firewall allows the connection

#### 3. "extension 'vector' does not exist"

The pgvector extension needs to be installed:
1. Install the extension on your PostgreSQL server
2. Connect to your database and run: `CREATE EXTENSION vector;`

#### 4. "function cosine_similarity does not exist"

This is related to the pgvector extension. Make sure:
1. pgvector is properly installed
2. The extension is created in your database

## Environment Variables

Make sure these are correctly set in your `.env` file:

```
POSTGRES_SERVER=localhost
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=doc_query
POSTGRES_PORT=5432
```

## Manual Database Reset

If you need to completely reset the database:

```sql
DROP DATABASE doc_query;
CREATE DATABASE doc_query;
```

Then run `python setup_db.py` again. 