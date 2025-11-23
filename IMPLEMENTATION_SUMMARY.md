# Implementation Summary: Google SSO Auth & Chat History

## Overview
This document summarizes the implementation of Google SSO authentication and chat history storage features for the Weather Disaster Management application.

## Backend Implementation

### 1. Database Setup
- **PostgreSQL** database with async SQLAlchemy
- **Location**: `src/database/connection.py`
- **Models**: 
  - `User` (`src/models/user.py`) - Stores authenticated users
  - `ChatHistory` (`src/models/chat_history.py`) - Stores chat conversations

### 2. Architecture Layers

#### Models (`src/models/`)
- `User`: email, name, google_id, timestamps
- `ChatHistory`: user_id, input_text, output_text, model, timestamps

#### Repositories (`src/repositories/`)
- `UserRepository`: Database operations for users
- `ChatHistoryRepository`: Database operations for chat history

#### Services (`src/services/`)
- `AuthService`: Handles Google OAuth authentication
- `ChatService`: Handles chat history operations

#### Utils (`src/utils/`)
- `jwt_utils.py`: JWT token creation and validation
- `oauth_utils.py`: Google OAuth token verification

#### Routes (`src/routes/`)
- `auth_routes.py`: `/auth/google/login`, `/auth/google/callback`
- `chat_routes.py`: `/chat/history`, `/chat/history/{id}`

### 3. Authentication Flow

1. Frontend sends Google ID token to `/auth/google/callback`
2. Backend verifies token with Google
3. If user exists: retrieve from DB
4. If user doesn't exist: create new user
5. Generate JWT token
6. Return JWT token to frontend

### 4. Chat History Storage

- Modified `/api/v1/disaster-response` endpoint to:
  - Require JWT authentication
  - Store input/output in `chat_history` table
  - Include model name and timestamp

### 5. Environment Variables Required

```bash
# Backend
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/weather_disaster_db
JWT_SECRET_KEY=your-secret-key-change-in-production
GOOGLE_CLIENT_ID=your-google-client-id

# Frontend
VITE_GOOGLE_CLIENT_ID=your-google-client-id
VITE_API_BASE_URL=http://localhost:8000
```

## Frontend Implementation

### 1. Authentication Context
- **Location**: `frontend/src/context/AuthContext.jsx`
- Manages JWT token and user state
- Persists to localStorage

### 2. Components

#### GoogleLoginButton (`frontend/src/components/auth/GoogleLoginButton.jsx`)
- Uses Google Identity Services
- Handles OAuth flow
- Sends credential to backend

#### ProtectedRoute (`frontend/src/components/auth/ProtectedRoute.jsx`)
- Wraps routes requiring authentication
- Redirects to login if not authenticated

### 3. Pages

#### Login (`frontend/src/pages/Login.jsx`)
- Google OAuth login page

#### ChatHistory (`frontend/src/pages/ChatHistory.jsx`)
- Lists user's chat history
- Shows conversation details

### 4. API Client Updates
- **Location**: `frontend/src/services/api.js`
- Automatically adds JWT token to requests
- Handles 401 errors (logout on unauthorized)
- New methods:
  - `googleLogin()`
  - `getChatHistory()`
  - `getChatById()`

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    google_id VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Chat History Table
```sql
CREATE TABLE chat_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    input_text TEXT NOT NULL,
    output_text TEXT NOT NULL,
    model VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## API Endpoints

### Authentication
- `POST /auth/google/login` - Initiate Google login
- `POST /auth/google/callback` - Handle Google OAuth callback

### Chat History
- `GET /chat/history` - Get user's chat history (requires auth)
- `GET /chat/history/{id}` - Get specific chat (requires auth)

### Modified Endpoints
- `POST /api/v1/disaster-response` - Now requires JWT authentication and saves chat history

## Setup Instructions

### 1. Backend Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/weather_disaster_db"
export JWT_SECRET_KEY="your-secret-key"
export GOOGLE_CLIENT_ID="your-google-client-id"

# Run database migrations (tables created automatically on startup)
uvicorn src.api.fastapi_app:app --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install

# Set environment variables in .env
VITE_GOOGLE_CLIENT_ID=your-google-client-id
VITE_API_BASE_URL=http://localhost:8000

npm run dev
```

### 3. Database Setup
```bash
# Using Docker Compose
docker-compose up -d postgres

# Or manually
createdb weather_disaster_db
```

## Testing

1. **Google OAuth**: 
   - Navigate to `/login`
   - Click Google Sign In
   - Verify JWT token is stored

2. **Chat History**:
   - Execute a disaster response workflow
   - Navigate to `/chat-history`
   - Verify conversation is saved

3. **Protected Routes**:
   - Try accessing protected routes without login
   - Should redirect to `/login`

## Security Features

1. **JWT Tokens**: Secure token-based authentication
2. **Token Validation**: All protected endpoints validate JWT
3. **User Isolation**: Chat history is user-specific
4. **CORS**: Configured for frontend origin
5. **Error Handling**: Comprehensive error handling and logging

## Notes

- Database tables are created automatically on application startup
- JWT tokens expire after 24 hours (configurable)
- Chat history is stored with user association for privacy
- All authentication errors are logged for debugging

