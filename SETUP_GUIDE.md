# Quick Setup Guide: Google SSO & Chat History

## Prerequisites

1. **PostgreSQL** (via Docker or local installation)
2. **Google Cloud Console** account for OAuth credentials
3. **Python 3.9+** and **Node.js 18+**

## Step 1: Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Google+ API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Configure:
   - Application type: **Web application**
   - Authorized JavaScript origins: `http://localhost:5173`, `http://localhost:3000`
   - Authorized redirect URIs: `http://localhost:5173`, `http://localhost:3000`
6. Copy the **Client ID**

## Step 2: Backend Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/weather_disaster_db

# JWT
JWT_SECRET_KEY=your-very-secure-secret-key-change-this-in-production
JWT_EXPIRATION_HOURS=24

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id-from-step-1

# Existing variables
GOOGLE_API_KEY=your-google-api-key
OPENWEATHER_API_KEY=your-openweather-api-key
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Start Database (Docker)

```bash
docker-compose up -d postgres
```

### Run Backend

```bash
uvicorn src.api.fastapi_app:app --reload
```

The database tables will be created automatically on startup.

## Step 3: Frontend Configuration

### Environment Variables

Create `frontend/.env`:

```bash
VITE_GOOGLE_CLIENT_ID=your-google-client-id-from-step-1
VITE_API_BASE_URL=http://localhost:8000
```

### Install Dependencies

```bash
cd frontend
npm install
```

### Run Frontend

```bash
npm run dev
```

## Step 4: Verify Setup

1. **Backend**: Visit `http://localhost:8000/docs` - should show API docs
2. **Frontend**: Visit `http://localhost:5173` - should show login page
3. **Database**: Check tables created:
   ```bash
   psql -U postgres -d weather_disaster_db -c "\dt"
   ```

## Testing the Features

### 1. Google SSO Login
1. Navigate to `http://localhost:5173/login`
2. Click "Sign in with Google"
3. Select your Google account
4. Should redirect to home page with user info in navbar

### 2. Chat History
1. After logging in, navigate to any workflow page
2. Execute a disaster response (e.g., from Home page)
3. Navigate to "Chat History" in the sidebar
4. Should see the conversation saved

### 3. Protected Routes
1. Logout (click logout icon in navbar)
2. Try accessing any protected route
3. Should redirect to login page

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running: `docker-compose ps`
- Check DATABASE_URL format: `postgresql+asyncpg://user:password@host:port/dbname`
- Verify database exists: `psql -U postgres -l`

### Google OAuth Issues
- Verify GOOGLE_CLIENT_ID matches in both backend and frontend
- Check authorized origins in Google Cloud Console
- Ensure JavaScript origins include your frontend URL

### JWT Token Issues
- Check JWT_SECRET_KEY is set
- Verify token expiration (default 24 hours)
- Check browser console for token storage

### CORS Issues
- Verify frontend URL in `fastapi_app.py` CORS middleware
- Check `VITE_API_BASE_URL` matches backend URL

## Production Considerations

1. **Change JWT_SECRET_KEY** to a secure random string
2. **Update CORS origins** to production domain
3. **Use environment-specific database URLs**
4. **Enable HTTPS** for OAuth redirects
5. **Set up database backups**
6. **Configure proper logging levels**

## API Endpoints Summary

### Authentication
- `POST /auth/google/login` - Initiate login
- `POST /auth/google/callback` - OAuth callback

### Chat History
- `GET /chat/history` - List user chats (requires auth)
- `GET /chat/history/{id}` - Get specific chat (requires auth)

### Modified
- `POST /api/v1/disaster-response` - Now requires auth and saves history

