# Quick Start Commands

## Setup (First Time Only)
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Start FastAPI Application
```bash
uvicorn src.api.fastapi_app:app --reload
```

## Alternative: Run with Custom Port
```bash
uvicorn src.api.fastapi_app:app --reload --port 8000
```

## Alternative: Run with Host Binding
```bash
uvicorn src.api.fastapi_app:app --reload --host 0.0.0.0 --port 8000
```

## Run CLI Version (Alternative)
```bash
python -m src.main
```

## Access Points
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health: http://localhost:8000/healthz

