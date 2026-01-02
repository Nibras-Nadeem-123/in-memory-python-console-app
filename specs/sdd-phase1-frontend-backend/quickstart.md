# Quickstart Guide: SDD System Phase 1

**Version**: 0.1.0
**Last Updated**: 2025-12-31

Get the Spec-Driven Development System Phase 1 running locally in under 10 minutes.

---

## Prerequisites

**Required**:
- Python 3.11+ ([download](https://www.python.org/downloads/))
- Node.js 18+ ([download](https://nodejs.org/))
- Git

**Recommended**:
- VS Code with Python and TypeScript extensions
- Postman or curl for API testing

**System Requirements**:
- macOS, Linux, or WSL2 (Windows)
- 4GB RAM minimum
- 500MB free disk space

---

## Quick Start (5 minutes)

### 1. Clone and Setup

```bash
# Clone repository
git clone <repository-url>
cd in-memory-python-console-app

# Checkout Phase 1 branch
git checkout phase1-frontend-backend
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows (WSL):
source venv/bin/activate
# On Windows (CMD):
venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

# Run backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify Backend**:
```bash
curl http://localhost:8000/api/v1/health
# Expected: {"status":"healthy","version":"0.1.0","timestamp":"2025-12-31T10:30:00Z"}
```

### 3. Frontend Setup (New Terminal)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**Expected Output**:
```
VITE v5.0.0  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

**Open Browser**:
Navigate to [http://localhost:5173](http://localhost:5173)

---

## Your First Spec Generation

### Option 1: Via Web UI

1. Open http://localhost:5173
2. Enter intent in text area:
   ```
   Create a task management application where users can create, edit, and delete tasks.
   Each task should have a title, description, priority level, and due date.
   Users should be able to categorize tasks using tags and filter tasks by priority or tag.
   ```
3. Click "Generate Spec"
4. View structured specification

### Option 2: Via API (curl)

```bash
curl -X POST http://localhost:8000/api/v1/spec \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Create a task management application where users can create, edit, and delete tasks. Each task should have a title, description, priority level, and due date. Users should be able to categorize tasks using tags and filter tasks by priority or tag."
  }'
```

**Expected Response**:
```json
{
  "goal": "Build a task management system with priority and categorization features",
  "entities": [
    {
      "name": "Task",
      "type": "Domain",
      "description": "Core work item that users manage",
      "attributes": ["title", "description", "priority", "dueDate", "status"],
      "relationships": [...]
    },
    ...
  ],
  "constraints": [...],
  "assumptions": [...],
  "metadata": {
    "generated_at": "2025-12-31T10:30:01Z",
    "processing_time_ms": 123.45,
    "confidence_score": 0.85,
    "warnings": []
  }
}
```

### Option 3: Via Postman

1. Import `specs/sdd-phase1-frontend-backend/contracts/openapi.yaml`
2. Use the "Generate Spec" request
3. Modify the `text` field with your intent
4. Send request

---

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── api/
│   │   │   └── spec.py          # /spec endpoint
│   │   ├── core/
│   │   │   ├── context.py       # Request context
│   │   │   ├── engine.py        # Orchestration
│   │   │   └── spec_builder.py  # Spec generation logic
│   │   ├── models/
│   │   │   ├── intent.py        # Input models
│   │   │   └── spec.py          # Output models
│   │   └── skills/
│   │       ├── entity_extractor.py
│   │       ├── constraint_parser.py
│   │       └── goal_identifier.py
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── contract/
│   ├── requirements.txt
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── IntentInput.tsx
│   │   │   ├── SpecOutput.tsx
│   │   │   └── ErrorDisplay.tsx
│   │   ├── api/
│   │   │   └── client.ts
│   │   ├── types/
│   │   │   └── spec.ts
│   │   └── hooks/
│   │       └── useSpecGeneration.ts
│   ├── tests/
│   ├── package.json
│   └── README.md
│
└── specs/
    └── sdd-phase1-frontend-backend/
        ├── plan.md
        ├── research.md
        ├── data-model.md
        ├── quickstart.md (this file)
        └── contracts/
            └── openapi.yaml
```

---

## Common Tasks

### Run Tests

**Backend**:
```bash
cd backend
pytest tests/
# With coverage:
pytest --cov=app tests/
```

**Frontend**:
```bash
cd frontend
npm test
# With coverage:
npm test -- --coverage
```

### Lint and Format

**Backend**:
```bash
cd backend
ruff check .
ruff format .
mypy app
```

**Frontend**:
```bash
cd frontend
npm run lint
npm run format
npm run type-check
```

### Generate TypeScript Types from OpenAPI

```bash
cd frontend
npx openapi-typescript-codegen \
  --input ../specs/sdd-phase1-frontend-backend/contracts/openapi.yaml \
  --output src/generated \
  --client fetch
```

---

## Architecture Overview

```
┌─────────────────┐
│   Frontend      │
│  (React + TS)   │
└────────┬────────┘
         │ HTTP POST /api/v1/spec
         │
         ▼
┌─────────────────┐
│  API Layer      │
│  (FastAPI)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Spec Builder   │
│  (Core Logic)   │
└────────┬────────┘
         │
         ├─────────────┬──────────────┬──────────────┐
         ▼             ▼              ▼              ▼
    ┌────────┐   ┌────────┐     ┌────────┐    ┌────────┐
    │ Goal   │   │Entity  │     │Constr- │    │Assump- │
    │Identif.│   │Extract.│     │aint    │    │tion    │
    │ Skill  │   │ Skill  │     │Parser  │    │Detector│
    └────────┘   └────────┘     └────────┘    └────────┘
```

**Data Flow**:
1. User enters intent in frontend
2. Frontend validates (50-500 words) and sends POST request
3. Backend receives and validates request (Pydantic)
4. SpecBuilder orchestrates skills to extract information
5. Skills analyze text and extract structured data
6. SpecBuilder assembles StructuredSpec
7. Backend returns JSON response
8. Frontend displays structured spec

---

## Configuration

### Backend Configuration

**Environment Variables** (create `backend/.env`):
```env
# Server
HOST=0.0.0.0
PORT=8000
RELOAD=true

# CORS
CORS_ORIGINS=http://localhost:5173

# Logging
LOG_LEVEL=INFO

# Timeouts
SPEC_GENERATION_TIMEOUT=2.0  # seconds
```

### Frontend Configuration

**Environment Variables** (create `frontend/.env`):
```env
VITE_API_URL=http://localhost:8000
VITE_API_TIMEOUT=5000  # milliseconds
```

---

## Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'app'`
**Solution**: Ensure you're in the `backend/` directory and venv is activated

**Problem**: `Port 8000 already in use`
**Solution**: Change port: `uvicorn app.main:app --port 8001`

**Problem**: `CORS error in browser console`
**Solution**: Verify `CORS_ORIGINS` includes frontend URL

### Frontend Issues

**Problem**: `Cannot connect to backend`
**Solution**: Verify backend is running on http://localhost:8000

**Problem**: `npm install fails`
**Solution**: Delete `node_modules` and `package-lock.json`, run `npm install` again

**Problem**: Type errors after OpenAPI changes
**Solution**: Regenerate types: `npm run generate-types`

### General Issues

**Problem**: Tests failing
**Solution**: Check logs, verify data model changes, run `pytest -v` for details

**Problem**: Slow spec generation
**Solution**: Check word count (keep under 500 words), verify no network issues

---

## Next Steps

1. **Explore the API**: Try different intents, review generated specs
2. **Read the Code**: Start with `backend/app/core/spec_builder.py`
3. **Run Tests**: Understand test patterns in `tests/`
4. **Customize Skills**: Add new extraction skills in `backend/app/skills/`
5. **Enhance UI**: Improve frontend components in `frontend/src/components/`

---

## Phase 2 Preview

**Coming Soon**:
- Planning Agent (generates implementation plans)
- Task Generation (breaks plans into tasks)
- Execution Guidance (provides implementation hints)
- Persistence Layer (save/load specs and plans)

**Not Yet Available**:
- User authentication
- Multi-user support
- AI model integration
- Real-time collaboration

---

## Resources

**Documentation**:
- [Full Plan](plan.md)
- [Research Decisions](research.md)
- [Data Model](data-model.md)
- [API Contract](contracts/openapi.yaml)

**External Links**:
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [React Documentation](https://react.dev)
- [Pydantic Documentation](https://docs.pydantic.dev)
- [Vite Documentation](https://vitejs.dev)

**Getting Help**:
- Check backend logs: stdout from uvicorn
- Check frontend logs: Browser DevTools Console
- Review test failures: `pytest -v` or `npm test`

---

## Development Workflow

### Making Changes

1. **Backend Changes**:
   ```bash
   # Edit code in app/
   # Backend auto-reloads (--reload flag)
   # Run tests: pytest tests/
   # Update OpenAPI if models changed
   ```

2. **Frontend Changes**:
   ```bash
   # Edit code in src/
   # Frontend auto-reloads (Vite HMR)
   # Regenerate types if API changed: npm run generate-types
   # Run tests: npm test
   ```

3. **Contract Changes**:
   ```bash
   # Edit contracts/openapi.yaml
   # Regenerate TypeScript types: cd frontend && npm run generate-types
   # Update backend models to match
   # Run contract tests: pytest tests/contract/
   ```

### Testing Workflow

```bash
# Backend: TDD cycle
cd backend
pytest tests/unit/test_new_feature.py  # Should fail
# Implement feature
pytest tests/unit/test_new_feature.py  # Should pass

# Frontend: Component testing
cd frontend
npm test -- --watch
# Edit component
# Tests auto-rerun
```

---

**Status**: ✅ Complete - Ready for development
**Questions?**: See troubleshooting section or review documentation
