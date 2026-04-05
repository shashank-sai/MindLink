# MindLink Authentication & Vector DB Setup Guide

This guide walks you through setting up user authentication and vector database integration for MindLink.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Database Setup](#database-setup)
4. [Ollama Setup](#ollama-setup)
5. [Configuration](#configuration)
6. [Running the Application](#running-the-application)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

1. **Python 3.9+** - [Download](https://python.org)
2. **PostgreSQL 14+** - [Download](https://postgresql.org) or use Docker
3. **Ollama** - [Download](https://ollama.ai)

### Optional (Recommended)

- **Docker** - For easy PostgreSQL and ChromaDB setup

---

## Installation

### Step 1: Install Python Dependencies

```bash
# Navigate to project directory
cd MindLink

# Install requirements
pip install -r requirements.txt
```

### Step 2: Set Up Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings
# Key variables to configure:
# - DATABASE_URL
# - JWT_SECRET_KEY (generate a strong random string)
# - OLLAMA_HOST
```

---

## Database Setup

### Option A: Using the Setup Script (Recommended)

```bash
# Run the automated setup
python setup_database.py
```

### Option B: Manual Setup

#### 1. Install PostgreSQL

**Windows:**

```powershell
# Download and install from https://postgresql.org/download/windows
# Or use Chocolatey:
choco install postgresql
```

**Linux:**

```bash
sudo apt-get install postgresql postgresql-contrib
```

**macOS:**

```bash
brew install postgresql
```

#### 2. Create Database User and Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create user
CREATE USER mindlink_user WITH PASSWORD 'your_secure_password';

# Create database
CREATE DATABASE mindlink OWNER mindlink_user;

# Enable UUID extension
\c mindlink
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

# Exit
\q
```

#### 3. Run Migrations

```bash
# Apply schema
psql -U mindlink_user -d mindlink -f db/migrations/001_initial_schema.sql
```

---

## Ollama Setup

### 1. Install Ollama

Download from [ollama.ai](https://ollama.ai) or install via:

**Windows:**

```powershell
winget install Ollama.Ollama
```

**Linux/macOS:**

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2. Pull Required Models

```bash
# Therapy model
ollama pull phi3:3.8b

# Medical sentinel model
ollama pull mistral:7b

# Synthesis model
ollama pull phi3.5:3.8b

# Embedding model (NEW - for vector DB)
ollama pull nomic-embed-text
```

### 3. Verify Ollama is Running

```bash
ollama list
# Should show all pulled models
```

---

## Configuration

### Environment Variables (.env)

```env
# Database
DATABASE_URL=postgresql://mindlink_user:your_password@localhost:5432/mindlink
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mindlink
DB_USER=mindlink_user
DB_PASSWORD=your_password

# Vector Database (ChromaDB)
CHROMA_DB_PATH=./chroma_db

# Security
JWT_SECRET_KEY=generate_a_strong_random_secret_here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Ollama
OLLAMA_HOST=http://localhost:11434
EMBEDDING_MODEL=nomic-embed-text

# App
FLASK_SECRET_KEY=another_random_secret
DEBUG=False
```

### Generate Secure Secrets

```bash
# Generate JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Running the Application

### 1. Start Ollama (if not running)

```bash
# Windows: Ollama runs as a service
# Linux/macOS:
ollama serve
```

### 2. Run the Web Application

```bash
# Start the Flask web server
python web_app.py
```

### 3. Access the Application

Open your browser to:

```
http://localhost:5000
```

---

## Testing

### Test Authentication

```bash
# Register a new user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword123"
  }'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "securepassword123"
  }'
```

### Test Conversation with Vector DB

```bash
# Create conversation
curl -X POST http://localhost:5000/api/conversations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"title": "Test Conversation"}'

# Send message (will be stored in vector DB)
curl -X POST http://localhost:5000/api/conversations/CONVERSATION_ID/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message": "I have been feeling stressed about work lately"}'
```

---

## Docker Setup (Alternative)

### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: "3.8"

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: mindlink_user
      POSTGRES_PASSWORD: your_password
      POSTGRES_DB: mindlink
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8000:8000"
    volumes:
      - chroma_data:/chroma

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

volumes:
  postgres_data:
  chroma_data:
  ollama_data:
```

Run:

```bash
docker-compose up -d
```

---

## Troubleshooting

### PostgreSQL Connection Failed

**Error:** `could not connect to server`

**Solution:**

1. Check if PostgreSQL is running: `pg_ctl status`
2. Check port: `netstat -an | grep 5432`
3. Verify credentials in `.env`

### Ollama Not Responding

**Error:** `Connection refused`

**Solution:**

1. Start Ollama: `ollama serve`
2. Check if running: `ollama list`
3. Verify host in `.env`: `OLLAMA_HOST=http://localhost:11434`

### ChromaDB Issues

**Error:** `Failed to initialize ChromaDB`

**Solution:**

1. Install: `pip install chromadb`
2. Or use local mode: Set `CHROMA_DB_PATH=./chroma_db`
3. Check permissions on chroma_db folder

### JWT Token Errors

**Error:** `Invalid token` or `Token expired`

**Solution:**

1. Regenerate JWT_SECRET_KEY
2. Check system time (tokens are time-based)
3. Clear browser cookies and re-login

### Vector Search Not Working

**Symptoms:** No relevant history returned

**Solution:**

1. Verify embedding model: `ollama pull nomic-embed-text`
2. Check vector collection exists in chroma_db folder
3. Test embedding generation:
   ```python
   from vector_store.embedding_service import get_embedding_service
   service = get_embedding_service()
   print(service.generate_embedding("test"))
   ```

---

## Next Steps

After setup is complete:

1. **Test the full flow:**
   - Register → Login → Create conversation → Send messages

2. **Verify vector DB:**
   - Send multiple messages
   - Check if relevant history is retrieved

3. **Explore the API:**
   - See `api/auth_routes.py` for auth endpoints
   - See `api/conversation_routes.py` for conversation endpoints

4. **Customize:**
   - Adjust `max_history` in ContextEngine
   - Modify embedding model in `.env`
   - Configure JWT expiration

---

## Support

For issues:

1. Check logs in `mindlink.log`
2. Enable debug mode: `DEBUG=True` in `.env`
3. Review error messages in console
