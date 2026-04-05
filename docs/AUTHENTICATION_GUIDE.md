# MindLink Authentication Guide

This guide explains how to run MindLink with user authentication, ensuring each user has their own private conversation history.

## Quick Start

### 1. Prerequisites

Ensure you have the following installed:

- **Python 3.9+**
- **PostgreSQL** (or SQLite for development)
- **Ollama** with required models

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Database

**Option A: Using Docker (Recommended)**

```bash
# Start PostgreSQL with Docker
docker run -d --name mindlink-postgres \
  -p 5432:5432 \
  -e POSTGRES_USER=mindlink_user \
  -e POSTGRES_PASSWORD=6155 \
  -e POSTGRES_DB=MindLink \
  postgres:15

# Wait for PostgreSQL to start, then run:
python setup_database.py
```

**Option B: Manual PostgreSQL Setup**

```bash
# Create user and database
psql -U postgres

CREATE USER mindlink_user WITH PASSWORD '6155';
CREATE DATABASE "MindLink" OWNER mindlink_user;
\q

# Run migrations
python setup_database.py
```

**Option C: SQLite (Development Only)**

The app will automatically fall back to SQLite if PostgreSQL is not available. Data will be stored in `mindlink_dev.db`.

### 4. Pull Ollama Models

```bash
ollama pull nomic-embed-text
ollama pull phi3:3.8b
ollama pull mistral:7b
ollama pull phi3.5:3.8b
```

### 5. Configure Environment

Edit the `.env` file with your settings:

```env
# Database
DATABASE_URL=postgresql://mindlink_user:6155@localhost:5432/MindLink

# Security (generate a strong random secret!)
JWT_SECRET_KEY=your_super_secret_jwt_key_change_this_in_production

# Ollama
OLLAMA_HOST=http://localhost:11434
```

### 6. Run the Application

```bash
python web_app.py
```

Then open **http://localhost:5000** in your browser.

## Authentication Flow

1. **First Visit**: Users are redirected to `/auth` (login/register page)
2. **Register**: New users create an account with username, email, and password
3. **Login**: Users authenticate with their credentials
4. **Chat**: After login, users access the chat interface at `/chat`
5. **History**: All conversations are saved per-user and can be accessed from the sidebar

## Features

### User Authentication

- Secure JWT-based authentication
- Password hashing with bcrypt
- Account lockout after failed attempts
- Session management

### Per-User Conversations

- Each user has their own conversation history
- Conversations are isolated by user ID
- Users cannot see other users' conversations

### Conversation Management

- View past conversations in the sidebar
- Clear conversation history
- Automatic conversation creation on first message

### Security

- Token-based authentication
- Secure password storage
- Session expiration
- Audit logging

## API Endpoints

### Authentication

| Endpoint             | Method | Description           |
| -------------------- | ------ | --------------------- |
| `/api/auth/register` | POST   | Register new user     |
| `/api/auth/login`    | POST   | Login user            |
| `/api/auth/logout`   | POST   | Logout user           |
| `/api/auth/me`       | GET    | Get current user info |
| `/api/auth/me`       | PUT    | Update user profile   |

### Conversations

| Endpoint                           | Method | Description                     |
| ---------------------------------- | ------ | ------------------------------- |
| `/api/user/conversations`          | GET    | Get all user conversations      |
| `/api/conversations/<id>/messages` | GET    | Get messages for a conversation |

## Testing the Setup

### 1. Register a New User

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

### 3. Get User Info (with token)

```bash
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Troubleshooting

### "Authentication required" loop

**Problem**: User keeps getting redirected to login page

**Solution**:

1. Check browser console for errors
2. Verify JWT_SECRET_KEY is set in `.env`
3. Clear browser cache and cookies
4. Ensure system clock is correct (JWT is time-based)

### Database connection errors

**Problem**: Cannot connect to database

**Solution**:

1. Verify PostgreSQL is running: `pg_ctl status` or check Docker container
2. Check credentials in `.env` match your setup
3. For SQLite, ensure `mindlink_dev.db` is writable

### Ollama connection errors

**Problem**: Cannot connect to Ollama

**Solution**:

1. Verify Ollama is running: `ollama list`
2. Check Ollama host in `.env`: `OLLAMA_HOST=http://localhost:11434`
3. Ensure required models are pulled

### Conversations not saving

**Problem**: Messages not being saved to database

**Solution**:

1. Check database connection
2. Verify tables exist: `python setup_database.py`
3. Check application logs for SQL errors

## File Structure

```
MindLink/
├── web_app.py              # Main Flask application
├── api/
│   └── auth_routes.py      # Authentication API endpoints
├── auth/
│   └── auth_manager.py     # Authentication logic
├── db/
│   └── models.py           # Database models
├── templates/
│   ├── auth.html           # Login/Register page
│   ├── chat.html           # Main chat interface
│   └── index.html          # Redirect page
├── config/
│   └── database.py         # Database configuration
└── .env                    # Environment variables
```

## Next Steps

After setting up authentication:

1. **Test the full flow**: Register → Login → Chat → Logout → Login again
2. **Verify isolation**: Create two users and confirm they have separate histories
3. **Customize**: Modify the UI colors, add features, or adjust security settings
4. **Deploy**: Follow the deployment guide for production setup

## Support

For issues:

1. Check logs in console
2. Enable debug mode: `DEBUG=True` in `.env`
3. Review error messages in browser console
