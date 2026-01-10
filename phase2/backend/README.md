# Phase 2 Backend

FastAPI backend for the Phase 2 Spec-Driven Todo System.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp ../../.env.example .env
# Edit .env with your database URL
```

3. Initialize database (if not already done):
```bash
cd migrations
alembic upgrade head
```

## Run

Development server:
```bash
python -m phase2.backend.main
```

Production:
```bash
uvicorn phase2.backend.main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## API Endpoints

- `GET /api/todos` - List todos
- `POST /api/todos` - Create todo
- `GET /api/todos/{id}` - Get todo
- `PUT /api/todos/{id}` - Update todo
- `DELETE /api/todos/{id}` - Delete todo
- `PATCH /api/todos/{id}/status` - Update status
