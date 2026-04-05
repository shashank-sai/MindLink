# MindLink Authentication & Vector DB Implementation Summary

## Overview

This implementation adds **user authentication** and **vector database integration** to the MindLink therapy assistant, enabling:

- **User accounts** with secure login/signup
- **Persistent conversations** across sessions
- **Long-term memory** via vector embeddings
- **Contextual responses** based on conversation history
- **Multi-user support** with data isolation

---

## What Was Implemented

### 1. Database Layer (PostgreSQL)

**Files Created:**

- `db/models.py` - SQLAlchemy ORM models
- `db/migrations/001_initial_schema.sql` - Database schema
- `config/database.py` - Database connection management

**Tables:**

- `users` - User accounts with secure password storage
- `user_sessions` - Active login sessions
- `conversations` - Conversation metadata
- `messages` - Individual message storage
- `user_profiles` - Extended user information
- `audit_logs` - Security audit trail

### 2. Authentication System

**Files Created:**

- `auth/auth_manager.py` - Core authentication logic
- `auth/__init__.py` - Module initialization
- `api/auth_routes.py` - REST API endpoints

**Features:**

- User registration with validation
- Secure login with bcrypt password hashing
- JWT token-based authentication
- Session management
- Password reset functionality
- Account lockout after failed attempts
- Audit logging

**API Endpoints:**

```
POST   /api/auth/register       - Register new user
POST   /api/auth/login          - User login
POST   /api/auth/logout         - User logout
GET    /api/auth/me             - Get current user
PUT    /api/auth/me             - Update profile
POST   /api/auth/forgot-password - Request password reset
POST   /api/auth/reset-password  - Reset password
POST   /api/auth/refresh        - Refresh JWT token
```

### 3. Vector Database (ChromaDB)

**Files Created:**

- `vector_store/chroma_client.py` - ChromaDB client
- `vector_store/embedding_service.py` - Embedding generation
- `vector_store/__init__.py` - Module initialization

**Features:**

- User-specific vector collections
- Semantic search for relevant conversations
- Automatic embedding generation via Ollama
- Persistent storage of conversation history
- GDPR-compliant data deletion

### 4. Enhanced Context Engine

**Files Created:**

- `core/vector_context_engine.py` - Vector-aware context management

**Features:**

- Short-term memory: In-memory conversation history (last 10 exchanges)
- Long-term memory: Vector-stored conversation history
- Semantic search for relevant past conversations
- Contextual response generation using both recent and historical data

### 5. Configuration

**Files Updated/Created:**

- `config/settings.py` - Enhanced with DB and auth settings
- `.env.example` - Environment variable template
- `requirements.txt` - Updated dependencies

---

## Architecture

### Data Flow

```
User Input
    ↓
[Auth Check] → JWT Token Validation
    ↓
[Context Engine] → Retrieves recent + relevant history
    ↓
[Vector DB Query] → Semantic search for similar past conversations
    ↓
[Orchestrator] → Processes through therapist + sentinel models
    ↓
[Synthesis] → Combines context + models for final response
    ↓
[Vector Store] → Stores new exchange with embedding
    ↓
Response to User
```

### Context Awareness

The system now provides context-aware responses by:

1. **Recent Context**: Retrieves last 10 in-memory exchanges
2. **Historical Context**: Searches vector DB for semantically similar past conversations
3. **Combined Prompt**: Formats both for the LLM to generate contextual responses

Example:

```
User: "I'm feeling stressed about work again"

System retrieves:
- Recent: Last conversation about weekend plans
- Historical: Past discussions about work stress, coping strategies discussed

LLM Response: "I remember you mentioned work stress before. How did the breathing technique we discussed last time work for you?"
```

---

## Dependencies

### New Packages Added

```
# Database
psycopg2-binary>=2.9.9    # PostgreSQL adapter
sqlalchemy>=2.0.0         # ORM
alembic>=1.13.0           # Migrations

# Vector Database
chromadb>=0.4.22          # Local vector DB

# Authentication & Security
bcrypt>=4.1.0             # Password hashing
PyJWT>=2.8.0              # JWT tokens
cryptography>=41.0.0      # Encryption
python-dotenv>=1.0.0      # Environment variables
```

### Ollama Models Required

```bash
ollama pull phi3:3.8b        # Therapist model
ollama pull mistral:7b       # Medical sentinel
ollama pull phi3.5:3.8b      # Synthesis
ollama pull nomic-embed-text # Embeddings (NEW)
```

---

## Setup Instructions

### Quick Start

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment:**

   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Initialize database:**

   ```bash
   python setup_database.py
   ```

4. **Pull Ollama models:**

   ```bash
   ollama pull nomic-embed-text
   ```

5. **Run tests:**

   ```bash
   python test_auth_setup.py
   ```

6. **Start application:**
   ```bash
   python web_app.py
   ```

### Detailed Setup

See [`SETUP_GUIDE.md`](SETUP_GUIDE.md) for comprehensive setup instructions.

---

## Testing

### Verify Installation

Run the test script:

```bash
python test_auth_setup.py
```

Expected output:

```
[1/6] Environment variables... ✓
[2/6] Database connection... ✓
[3/6] ChromaDB... ✓
[4/6] Ollama... ✓
[5/6] Embedding service... ✓
[6/6] Authentication... ✓
```

### Test Authentication Flow

```bash
# 1. Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# 2. Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'

# 3. Use token to access protected routes
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:5000/api/auth/me
```

---

## Project Structure

```
MindLink/
├── auth/                    # Authentication module
│   ├── __init__.py
│   └── auth_manager.py
├── vector_store/            # Vector DB module
│   ├── __init__.py
│   ├── chroma_client.py
│   └── embedding_service.py
├── api/                     # REST API
│   ├── __init__.py
│   ├── auth_routes.py
│   └── conversation_routes.py
├── db/                      # Database layer
│   ├── __init__.py
│   ├── models.py
│   └── migrations/
│       └── 001_initial_schema.sql
├── core/
│   ├── context_engine.py    # Original (unchanged)
│   └── vector_context_engine.py  # NEW: Enhanced version
├── config/
│   ├── settings.py          # Updated
│   └── database.py          # NEW
├── .env.example             # NEW
├── requirements.txt         # Updated
├── setup_database.py        # NEW
├── test_auth_setup.py       # NEW
└── SETUP_GUIDE.md          # NEW
```

---

## Security Features

1. **Password Security:**
   - Bcrypt hashing with salt
   - Minimum 8 character password requirement
   - No plain text password storage

2. **JWT Tokens:**
   - Time-limited tokens (24 hours default)
   - Secure secret key (configurable)
   - Token refresh mechanism

3. **Session Management:**
   - Unique session tokens
   - Session expiration
   - Device tracking

4. **Audit Trail:**
   - Login attempts logged
   - Password changes tracked
   - Account lockout after failed attempts

5. **Data Isolation:**
   - User-specific vector collections
   - Foreign key constraints
   - Cascade deletes for privacy

---

## Performance Considerations

### Vector Search Performance

- **Local mode**: ChromaDB stores vectors in `./chroma_db`
- **Remote mode**: Can use ChromaDB server for better performance
- **Indexing**: Automatic indexing for fast similarity search
- **Batch operations**: Embeddings can be batched for efficiency

### Database Performance

- **Connection pooling**: SQLAlchemy pool management
- **Indexes**: Optimized indexes on common queries
- **Cascade deletes**: Efficient cleanup of user data

---

## Future Enhancements

### Recommended Next Steps

1. **Conversation History UI** - Show full conversation history
2. **Mood Tracking** - Track user mood over time
3. **Therapy Goals** - Set and track therapy progress
4. **Export Data** - Allow users to export their data (GDPR)
5. **Multi-device Sync** - Sync conversations across devices

### Optional Features

- Email verification
- Two-factor authentication
- Social login (Google, Apple)
- Conversation search
- Conversation tagging
- Session notes
- Progress reports

---

## Troubleshooting

### Common Issues

1. **Database connection failed**
   - Check PostgreSQL is running
   - Verify DATABASE_URL in .env
   - Run: `python setup_database.py`

2. **Ollama not responding**
   - Ensure Ollama service is running
   - Check OLLAMA_HOST in .env
   - Run: `ollama list`

3. **ChromaDB errors**
   - Check CHROMA_DB_PATH permissions
   - Try deleting chroma_db folder and restarting

4. **JWT token errors**
   - Regenerate JWT_SECRET_KEY
   - Check system time is correct
   - Clear browser cookies

For more help, see [SETUP_GUIDE.md](SETUP_GUIDE.md#troubleshooting)

---

## License & Credits

This implementation extends the original MindLink project with authentication and vector database capabilities.

**Original MindLink**: Therapy assistant with dual-model system
**Enhanced by**: Authentication + Vector DB integration

---

## Support

For issues or questions:

1. Check logs in `mindlink.log`
2. Enable debug mode: `DEBUG=True`
3. Review [SETUP_GUIDE.md](SETUP_GUIDE.md)
4. Run `python test_auth_setup.py` to diagnose issues
