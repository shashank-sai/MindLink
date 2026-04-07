# Running MindLink

This guide explains how to run the MindLink application with user authentication.

## Quick Start

### 1. Prerequisites

Make sure you have:

- Python 3.8+ installed
- PostgreSQL 14+ running on your system
- All dependencies installed: `pip install -r requirements.txt`

### 2. Database Setup

**First time setup only:**

```bash
# Run the database setup script
python setup_database.py
```

This will:

- Create the `mindlink` database (if it doesn't exist)
- Run migrations to create all required tables
- Test the connection

**Important:** The database name is case-sensitive in PostgreSQL. The application uses lowercase `mindlink`.

### 3. Configuration

Check your `.env` file has the correct database URL:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/mindlink
DB_NAME=mindlink
DB_USER=postgres
DB_PASSWORD=YOUR_PASSWORD
```

### 4. Run the Application

```bash
python web_app.py
```

The application will start on `http://localhost:5000`

### 5. Access the Application

1. Open your browser to `http://localhost:5000`
2. You'll be redirected to the login page (`/auth`)
3. Click "Register" to create a new account
4. After registration, you'll be automatically logged in
5. Start chatting with the AI therapist!

## Features

### Authentication

- **Login/Register**: Secure JWT-based authentication
- **Password Security**: Bcrypt hashing with salt
- **Session Management**: Automatic session handling

### Chat Features

- **Per-User Conversations**: Each user has their own conversation history
- **Message History**: All conversations are saved and retrievable
- **Real-time Updates**: SocketIO for instant messaging

## Troubleshooting

### "relation 'users' does not exist"

Run the database setup:

```bash
python setup_database.py
```

### Password authentication failed

Check your `.env` file has the correct PostgreSQL password.

### Database connection error

Ensure PostgreSQL is running:

```bash
# Check PostgreSQL service status
# Windows: Check Services or run:
pg_ctl status
```

### Port 5000 already in use

Change the port in `web_app.py`:

```python
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001)  # Change port here
```

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user

### Conversations

- `GET /api/user/conversations` - Get user's conversations
- `GET /api/conversations/<id>/messages` - Get conversation messages

## File Structure

```
MindLink/
├── web_app.py           # Main application
├── api/
│   └── auth_routes.py   # Authentication endpoints
├── auth/
│   └── auth_manager.py  # Authentication logic
├── db/
│   └── models.py        # SQLAlchemy models
├── templates/
│   ├── auth.html        # Login/Register page
│   └── chat.html        # Chat interface
├── config/
│   └── database.py      # Database configuration
├── .env                 # Environment variables (credentials)
└── docs/
    └── RUNNING_THE_APP.md  # This file
```

## Next Steps

After running successfully:

1. Explore the chat interface at `/chat`
2. Check conversation history in the sidebar
3. Test logout and login again to verify persistence
4. Review `AUTHENTICATION_GUIDE.md` for detailed API documentation
