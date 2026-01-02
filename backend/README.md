# SDD Backend - Phase 1

Backend API for the Spec-Driven Development System Phase 1.

## Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `POST /api/v1/spec` - Generate structured specification from user intent
- `GET /api/v1/health` - Health check endpoint

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/unit/test_spec_builder.py
```

## Code Quality

```bash
# Lint with ruff
ruff check .

# Format with ruff
ruff format .

# Type check with mypy
mypy app
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app instance
│   ├── api/
│   │   └── spec.py          # /spec endpoint
│   ├── core/
│   │   ├── context.py       # Request context
│   │   ├── engine.py        # Orchestration engine
│   │   └── spec_builder.py  # Spec generation logic
│   ├── models/
│   │   ├── intent.py        # Input models
│   │   └── spec.py          # Output models
│   └── skills/
│       ├── base.py          # Skill interface
│       ├── goal_identifier.py
│       ├── entity_extractor.py
│       ├── constraint_parser.py
│       └── assumption_detector.py
├── tests/
│   ├── unit/
│   └── integration/
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Environment Variables

Create a `.env` file:

```env
HOST=0.0.0.0
PORT=8000
RELOAD=true
CORS_ORIGINS=http://localhost:5173
LOG_LEVEL=INFO
SPEC_GENERATION_TIMEOUT=2.0
```
