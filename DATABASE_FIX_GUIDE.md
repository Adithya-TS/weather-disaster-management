# Database Connection Fix Guide

## Problem
Your application is trying to connect to PostgreSQL on **port 5435**, but PostgreSQL is not running on that port, causing the following error:

```
Multiple exceptions: [Errno 10061] Connect call failed ('::1', 5435, 0, 0), [Errno 10061] Connect call failed ('127.0.0.1', 5435)
```

## Solution

### Option 1: Fix the Database URL (Recommended)

1. **Check your `.env` file** in the project root directory
2. Look for the `DATABASE_URL` variable
3. **Change the port from 5435 to 5432**

Your `.env` file should have:

```bash
# WRONG - causes connection error
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5435/weather_disaster_db

# CORRECT - use standard PostgreSQL port
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/weather_disaster_db
```

### Option 2: Start PostgreSQL (if not running)

If PostgreSQL is not running, start it using Docker Compose:

```bash
docker-compose up -d postgres
```

This will start PostgreSQL on port 5432 (the standard port).

### Option 3: Verify PostgreSQL is Running

Check if PostgreSQL is running on the correct port:

```bash
# Windows PowerShell
netstat -ano | findstr :5432

# Or use Docker to check
docker ps | findstr postgres
```

## Steps to Fix

1. **Stop the running server** (if it's still running):
   - Press `Ctrl+C` in the terminal where `uvicorn` is running

2. **Update the `.env` file** with the correct port (5432)

3. **Ensure PostgreSQL is running**:
   ```bash
   docker-compose up -d postgres
   ```

4. **Restart your FastAPI server**:
   ```bash
   uvicorn src.api.fastapi_app:app --reload
   ```

5. **Verify the connection**:
   - Visit http://localhost:8000/healthz
   - You should see: `{"status": "ok", ...}`

## Expected .env File Configuration

Here's what your `.env` file should contain:

```bash
# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/weather_disaster_db

# JWT Configuration
JWT_SECRET_KEY=your-very-secure-secret-key-change-this-in-production
JWT_EXPIRATION_HOURS=24

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id

# API Keys
GOOGLE_API_KEY=your-google-api-key
OPENWEATHER_API_KEY=your-openweather-api-key

# Optional
LOG_LEVEL=INFO
```

## Verification

After fixing, you should see these logs on startup:

```
INFO:     Started server process [xxxx]
INFO:     Waiting for application startup.
{"log_file": "logs\\...", "event": "fastapi.startup", ...}
{"message": "Database tables created successfully", "event": "database.initialized", ...}
INFO:     Application startup complete.
```

No more database connection errors! ✅

