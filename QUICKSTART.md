# MindLink Quick Start Guide

## Current Status

Your environment is configured with:

- ✓ Database: PostgreSQL at `localhost:5432` (MindLink database)
- ✓ Credentials: user `mindlink_user` with password `6155`
- ✓ ChromaDB: Local storage at `./chroma_db`
- ✓ Ollama: Running at `localhost:11434`

## Next Steps Required

### Option 1: Install PostgreSQL (Recommended for Production)

1. **Download PostgreSQL:**
   - Windows: https://www.postgresql.org/download/windows/
   - Or use EnterpriseDB installer

2. **During installation:**
   - Set superuser password (remember it!)
   - Keep default port: 5432

3. **After installation, run:**

   ```bash
   # Open pgAdmin or psql and run:
   CREATE USER mindlink_user WITH PASSWORD '6155';
   CREATE DATABASE "MindLink" OWNER mindlink_user;
   ```

4. **Then run the setup:**
   ```bash
   python setup_database.py
   ```

### Option 2: Use Docker (Quick & Easy)

If you have Docker installed:

```bash
# Run PostgreSQL with your credentials
docker run -d --name mindlink-postgres \
  -p 5432:5432 \
  -e POSTGRES_USER=mindlink_user \
  -e POSTGRES_PASSWORD=6155 \
  -e POSTGRES_DB=MindLink \
  postgres:15

# Wait 10 seconds, then run:
python setup_database.py
```

### Option 3: Use SQLite (Development Only)

For testing without PostgreSQL, the system will automatically fall back to SQLite. Just run:

```bash
# This will create a local SQLite database
python web_app.py
```

**Note:** SQLite is not recommended for production use.

## Ollama Models Required

You need to pull the embedding model:

```bash
# Pull the embedding model for vector DB
ollama pull nomic-embed-text

# Verify models
ollama list
# Should show: phi3:3.8b, mistral:7b, phi3.5:3.8b, nomic-embed-text
```

## Testing the Setup

After PostgreSQL is running:

```bash
# 1. Initialize database
python setup_database.py

# 2. Run verification
python test_auth_setup.py

# 3. Start the application
python web_app.py
```

Then open http://localhost:5000 in your browser.

## API Endpoints

Once running, you can test:

```bash
# Register a user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'
```

## Troubleshooting

### "password authentication failed"

- PostgreSQL is running but user doesn't exist
- Create the user: `CREATE USER mindlink_user WITH PASSWORD '6155';`

### "could not connect to server"

- PostgreSQL is not running
- Start PostgreSQL service or run Docker container

### "model not found"

- Pull the required model: `ollama pull nomic-embed-text`

## Full Documentation

For complete setup instructions, see [`SETUP_GUIDE.md`](SETUP_GUIDE.md)
