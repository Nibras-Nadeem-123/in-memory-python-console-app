# Research: SDD System Phase 1 - Technology Decisions

**Date**: 2025-12-31
**Feature**: Frontend-Backend Spec Generation System
**Purpose**: Document all technology choices, alternatives considered, and rationale

---

## 1. FastAPI Best Practices for Spec Generation

### Decision: Use FastAPI with Pydantic V2 for request/response validation

**Rationale**:
- FastAPI provides automatic OpenAPI schema generation
- Pydantic V2 offers excellent validation and serialization performance
- Type hints enable IDE support and reduce runtime errors
- Built-in async support for future scalability

**Alternatives Considered**:
- **Flask**: More mature but lacks async support and automatic validation
- **Django REST Framework**: Too heavyweight for Phase 1 simple API
- **Plain ASGI**: Too low-level, would require manual validation

**Implementation Pattern**:
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

class IntentRequest(BaseModel):
    text: str = Field(..., min_length=50, max_length=5000)

@app.post("/api/v1/spec")
async def generate_spec(request: IntentRequest) -> StructuredSpec:
    # Validation automatic via Pydantic
    pass
```

**Error Handling Pattern**:
- 400 for validation errors (Pydantic handles automatically)
- 422 for ambiguous intent (custom logic)
- 500 for unexpected errors (FastAPI middleware)

**CORS Configuration**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)
```

---

## 2. React Component Patterns for Structured Data Display

### Decision: Use React 18 with TypeScript and composition patterns

**Rationale**:
- React 18 provides concurrent features for better UX
- TypeScript ensures type safety across frontend-backend boundary
- Composition pattern allows flexible spec rendering
- Component reusability for future phases

**Alternatives Considered**:
- **Vue 3**: Good choice but less ecosystem support for TypeScript
- **Svelte**: Excellent performance but smaller community
- **Plain JavaScript**: No type safety, error-prone

**Component Architecture**:
```tsx
// Composition pattern
<SpecOutput spec={spec}>
  <GoalSection goal={spec.goal} />
  <EntitiesSection entities={spec.entities} />
  <ConstraintsSection constraints={spec.constraints} />
  <AssumptionsSection assumptions={spec.assumptions} />
</SpecOutput>
```

**Rendering Decision: Custom Components over Markdown**

**Decision**: Use custom React components for structured display

**Rationale**:
- Full control over styling and interactivity
- Can add features like expand/collapse, entity graphs
- Better accessibility (ARIA attributes)
- Markdown would require parsing and sanitization

**Real-time Validation UI**:
```tsx
const [wordCount, setWordCount] = useState(0);
const isValid = wordCount >= 50 && wordCount <= 500;

<textarea
  onChange={(e) => setWordCount(e.target.value.split(/\s+/).length)}
  className={isValid ? "valid" : "invalid"}
/>
<span>{wordCount} / 500 words {!isValid && "(minimum 50)"}</span>
```

---

## 3. TypeScript Type Safety for API Contracts

### Decision: Use OpenAPI TypeScript Generator with runtime validation

**Rationale**:
- Single source of truth (OpenAPI spec)
- Automatic type generation prevents drift
- Runtime validation catches API contract violations
- Zod provides Pydantic-equivalent validation in TypeScript

**Alternatives Considered**:
- **Manual type definitions**: Error-prone, duplicates contract
- **GraphQL**: Overkill for simple REST API
- **tRPC**: Requires shared TypeScript monorepo

**Selected Tool**: `openapi-typescript-codegen`

**Generation Command**:
```bash
npx openapi-typescript-codegen \
  --input contracts/openapi.yaml \
  --output src/generated \
  --client fetch
```

**Runtime Validation with Zod**:
```typescript
import { z } from 'zod';

const StructuredSpecSchema = z.object({
  goal: z.string().min(1),
  entities: z.array(EntitySchema),
  constraints: z.array(ConstraintSchema),
  assumptions: z.array(AssumptionSchema),
  metadata: SpecMetadataSchema,
});

// Validate API response
const spec = StructuredSpecSchema.parse(apiResponse);
```

**Type Safety Guarantee**:
- Backend: Pydantic models define types
- OpenAPI: Generated from Pydantic models
- Frontend: TypeScript types generated from OpenAPI
- Runtime: Zod validates responses match types

---

## 4. Testing Strategy for Intent Parsing

### Decision: Multi-layer testing with fixtures and snapshot testing

**Rationale**:
- Different layers need different testing strategies
- Test data generation ensures coverage of varied inputs
- Snapshot testing catches unintended output changes
- Contract testing ensures frontend-backend alignment

**Test Layers**:

**Unit Tests (Backend)**:
```python
# Test individual skills
def test_entity_extractor():
    text = "Create a todo app with tasks and tags"
    entities = EntityExtractorSkill().extract(text)
    assert len(entities) == 2
    assert entities[0].name == "Task"
    assert entities[1].name == "Tag"
```

**Integration Tests (Backend)**:
```python
# Test full API endpoint
@pytest.mark.asyncio
async def test_spec_endpoint():
    response = await client.post("/api/v1/spec", json={
        "text": "Build a blog with posts and comments"
    })
    assert response.status_code == 200
    assert response.json()["goal"] is not None
```

**Snapshot Tests**:
```python
def test_spec_generation_snapshot(snapshot):
    spec = generate_spec("Create a CRM system")
    snapshot.assert_match(spec.model_dump_json(indent=2))
```

**Contract Tests**:
```python
# Validate OpenAPI compliance
def test_openapi_contract():
    response = client.post("/api/v1/spec", json=valid_request)
    validate_against_openapi_schema(response.json())
```

**Frontend Tests**:
```typescript
// Component tests
describe('SpecOutput', () => {
  it('renders all sections', () => {
    render(<SpecOutput spec={mockSpec} />);
    expect(screen.getByText(mockSpec.goal)).toBeInTheDocument();
    expect(screen.getByText('Entities')).toBeInTheDocument();
  });
});

// Integration tests
describe('Intent to Spec flow', () => {
  it('submits intent and displays spec', async () => {
    render(<App />);
    const input = screen.getByRole('textbox');
    await userEvent.type(input, validIntent);
    await userEvent.click(screen.getByText('Generate Spec'));
    await waitFor(() => {
      expect(screen.getByText(/Build a task/)).toBeInTheDocument();
    });
  });
});
```

**Test Data Generation**:
- Fixtures: 20+ sample intents covering different domains
- Edge cases: Very short, very long, ambiguous inputs
- Invalid cases: Empty, non-English, too vague

---

## 5. Development Workflow

### Decision: Separate backend and frontend development with contract-first approach

**Workflow**:
1. Define OpenAPI contract first
2. Generate TypeScript types from contract
3. Implement backend to match contract
4. Implement frontend using generated types
5. Run contract tests to verify alignment

**Local Development**:
- Backend: `http://localhost:8000` (uvicorn)
- Frontend: `http://localhost:5173` (Vite)
- Hot reload on both sides

**Build and Deploy** (Future):
- Backend: Docker container
- Frontend: Static build to CDN
- API Gateway for routing

---

## 6. State Management

### Decision: Use TanStack Query (React Query) for server state

**Rationale**:
- Built-in caching and request deduplication
- Automatic loading/error states
- No need for Redux/Context for Phase 1
- Simplifies async data fetching

**Alternatives Considered**:
- **Redux**: Overkill for single API endpoint
- **Plain fetch + useState**: Manual loading/error handling
- **SWR**: Good alternative, but React Query more features

**Implementation**:
```typescript
const useSpecGeneration = () => {
  return useMutation({
    mutationFn: (text: string) =>
      api.generateSpec({ text }),
    onSuccess: (data) => {
      // Handle success
    },
    onError: (error) => {
      // Handle error
    }
  });
};
```

---

## 7. Code Quality Tools

### Backend
- **Linting**: ruff (fast, modern Python linter)
- **Type Checking**: mypy (strict mode)
- **Formatting**: ruff format (replaces black)
- **Testing**: pytest + pytest-asyncio + pytest-cov

### Frontend
- **Linting**: ESLint with TypeScript plugin
- **Type Checking**: tsc --noEmit
- **Formatting**: Prettier
- **Testing**: Vitest + React Testing Library

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: backend-lint
        name: Backend Lint
        entry: cd backend && ruff check .
      - id: backend-types
        name: Backend Types
        entry: cd backend && mypy app
      - id: frontend-lint
        name: Frontend Lint
        entry: cd frontend && npm run lint
      - id: frontend-types
        name: Frontend Types
        entry: cd frontend && npm run type-check
```

---

## Summary Table

| Decision Area | Choice | Rationale | Alternative |
|---------------|--------|-----------|-------------|
| Backend Framework | FastAPI | Async, validation, OpenAPI | Flask, Django |
| Frontend Framework | React 18 + TS | Type safety, ecosystem | Vue, Svelte |
| Type Safety | OpenAPI → TS Generator | Single source of truth | Manual types |
| State Management | TanStack Query | Server state focus | Redux, SWR |
| Validation | Pydantic + Zod | Runtime safety | Manual validation |
| Testing | pytest + Vitest | Modern, fast | unittest, Jest |
| API Design | REST with JSON | Simple, standard | GraphQL, gRPC |

---

## Risk Mitigation

**Risk**: Frontend-backend type drift
**Mitigation**: OpenAPI-generated types, contract tests

**Risk**: Ambiguous intent handling
**Mitigation**: Clear error messages with suggestions, confidence scoring

**Risk**: Performance degradation with complex inputs
**Mitigation**: Word limit (500), timeout (2s), performance tests

**Risk**: Incomplete spec extraction
**Mitigation**: Confidence scoring, explicit assumptions, warnings

---

## Decisions Log

| Date | Decision | Status |
|------|----------|--------|
| 2025-12-31 | Use FastAPI for backend | ✅ Approved |
| 2025-12-31 | Use React 18 + TypeScript for frontend | ✅ Approved |
| 2025-12-31 | OpenAPI-first development | ✅ Approved |
| 2025-12-31 | TanStack Query for state | ✅ Approved |
| 2025-12-31 | Zod for runtime validation | ✅ Approved |

---

**Status**: All research complete - ready for implementation
**Next**: Generate data-model.md and contracts/openapi.yaml
