# Research: Phase 2 Persistence Layer

**Date**: 2026-01-07
**Feature**: Persistence Layer (010-phase2-persistence)

## Findings

### 1. SQLModel + Alembic Integration Pattern

**Decision**: Use Alembic with `alembic revision --autogenerate` for schema changes

**Rationale**:
- SQLModel is built on SQLAlchemy, which has excellent Alembic integration
- Autogenerate reduces manual SQL writing and human error
- SQLAlchemy/Alembic integration is battle-tested and production-ready
- Allows both declarative (autogenerate) and imperative (manual) approaches

**Alternatives Considered**:
- Manual SQL migrations: Too error-prone, no type safety
- Other ORMs (Tortoise-ORM, Django ORM): SQLModel chosen per specification requirements
- No migrations (schema drift): Violates best practices

**Implementation**:
```python
# env.py configuration
from models import SQLModel
target_metadata = SQLModel.metadata

# Generate migration
alembic revision --autogenerate -m "description"
```

### 2. Neon PostgreSQL Specific Configuration

**Decision**: Use connection string with sslmode=require, pool_size=5, max_overflow=10

**Rationale**:
- Neon requires SSL connections for security
- Pool size 5 is optimal for typical web workloads (not too small, not too large)
- Max overflow 10 allows handling traffic spikes without exhausting database connections
- Total capacity: 15 concurrent connections

**Alternatives Considered**:
- Larger pools (pool_size=20, max_overflow=20): Wastes database resources and costs
- Smaller pools (pool_size=2, max_overflow=5): Connection exhaustion under load
- No connection pooling: Too slow for production, each request creates new connection

**Implementation**:
```python
DATABASE_URL = "postgresql+psycopg2://user:pass@ep-neon/db?sslmode=require"
engine = create_engine(DATABASE_URL, pool_size=5, max_overflow=10, pool_recycle=3600, pool_pre_ping=True)
```

### 3. Text Search Implementation

**Decision**: PostgreSQL's built-in full-text search with GIN index on title

**Rationale**:
- PostgreSQL native feature, no external dependencies
- GIN indexes optimized for full-text search queries
- Efficient for keyword search with good performance
- Supports ranking and relevance sorting (future enhancement)

**Alternatives Considered**:
- LIKE pattern matching: Slow for large datasets, no relevance ranking
- External search service (Elasticsearch, Algolia): Overkill for single table, adds complexity
- Regular B-tree index: Doesn't support efficient pattern matching

**Implementation**:
```sql
-- Add GIN index for text search
CREATE INDEX idx_todo_title_search ON todo USING GIN (to_tsvector('english', title));

-- Query with text search
SELECT * FROM todo WHERE to_tsvector('english', title) @@ to_tsquery('english', 'keyword');
```

### 4. Migration Execution Strategy

**Decision**: Automatic migration on startup in development, manual in production

**Rationale**:
- Developer convenience: Automatic migrations speed up development workflow
- Production safety: Manual migrations require review and approval
- Environment-specific behavior supported via environment variable

**Alternatives Considered**:
- Always manual: Slows development, friction for developers
- Always auto: Risky for production, no review before schema changes
- Migrations in separate step: Complex workflow,容易出错

**Implementation**:
```python
# development: automatic
if ENV == "development":
    from alembic.config import Config
    from alembic import command
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

# production: manual
# Developer runs: alembic upgrade head
```

### 5. Connection Pool Configuration

**Decision**: pool_size=5, max_overflow=10, pool_recycle=3600s, pool_pre_ping=True

**Rationale**:
- pool_size=5: Optimal for moderate load, balances efficiency and resource usage
- max_overflow=10: Allows handling traffic spikes (total 15 connections)
- pool_recycle=3600s: Recycle connections hourly to prevent stale connections
- pool_pre_ping=True: Test connection before use, catch stale connections early

**Alternatives Considered**:
- No recycling: Stale connections accumulate, connection errors
- Larger pools: Wastes database resources and may hit Neon limits
- No pre-ping: Stale connections cause errors during use, harder to debug

**Implementation**:
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
    pool_pre_ping=True,
    pool_timeout=30,
    echo=False
)
```

## Technology Stack Confirmed

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Runtime language |
| SQLModel | 0.0.14+ | ORM and database models |
| Alembic | 1.12+ | Database migrations |
| psycopg2-binary | 2.9+ | PostgreSQL adapter |
| pydantic-settings | 2.0+ | Configuration management |
| pytest | 7.4+ | Testing framework |
| pytest-asyncio | 0.21+ | Async test support |

## Performance Characteristics

Based on PostgreSQL and SQLModel benchmarks:

- Single row SELECT (by primary key): ~1ms
- Single row INSERT: ~2ms
- Query with index filter (10k rows): ~10ms
- Query with full-text search (10k rows): ~50ms
- Connection creation: ~50ms (mitigated by pooling)
- Transaction commit: ~5ms

## Security Considerations

1. **SQL Injection Prevention**
   - SQLModel uses parameterized queries by default
   - Never concatenate user input into SQL strings
   - Validate all inputs with Pydantic models

2. **Connection Security**
   - SSL mode required for Neon connections
   - Connection strings stored in environment variables
   - No credentials in code or version control

3. **Migration Safety**
   - Test migrations on production-like data before production
   - Maintain rollback scripts for all migrations
   - Backup database before major schema changes

## Operational Considerations

### Connection Pool Monitoring

Key metrics to monitor:
- Active connections (should be < pool_size under normal load)
- Idle connections (should be recycled periodically)
- Wait time for connections (should be <100ms)
- Connection failures (should be near zero)

### Migration Best Practices

1. Test migrations on development database
2. Review auto-generated migrations manually
3. Test rollback procedure
4. Backup database before production migration
5. Run migration during low-traffic period
6. Verify migration success with smoke tests

### Performance Optimization

1. Index usage: Monitor query plans, verify indexes used
2. Query optimization: Use EXPLAIN ANALYZE for slow queries
3. Connection tuning: Adjust pool size based on load testing
4. Database tuning: Configure PostgreSQL settings via Neon console

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Migration failure | Test on production-like data, maintain rollback |
| Connection pool exhaustion | Monitor metrics, configure alerts |
| Performance degradation | Regular testing, index monitoring |
| Schema drift | Restrict DB access, audit changes |
| Data loss during migration | Backup before migration, test rollback |

## Conclusion

All technical unknowns resolved. Recommended approaches balance developer productivity, production safety, and performance requirements. SQLModel + Alembic + PostgreSQL is a proven stack with excellent community support and documentation.
