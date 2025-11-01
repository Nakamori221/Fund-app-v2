# Fund IC Automation System - Backend API

## Overview

FastAPI-based REST API for the Fund IC Automation System. Handles case management, conflict detection, report generation, and investment committee workflow automation.

**Status**: Phase 1 - Backend Skeleton (Endpoints scaffolded, Database models pending)
**API Version**: v1.0.0

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- pip or uv

### Installation

1. **Clone and setup**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Run migrations** (when available):
```bash
alembic upgrade head
```

4. **Start development server**:
```bash
python -m app.main
# Or with uvicorn directly:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. **Verify health**:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development"
}
```

## API Documentation

### OpenAPI/Swagger Documentation

When running in DEBUG mode, access interactive API docs:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

### API Endpoints

#### Authentication (`/api/v1/auth`)

| Method | Endpoint | Status | Description |
|--------|----------|--------|-------------|
| POST | `/register` | 201 | Register new user |
| POST | `/login` | 200 | Login and get JWT tokens |
| POST | `/refresh` | 200 | Refresh access token |
| GET | `/me` | 200 | Get current user info |

#### Cases (`/api/v1/cases`)

| Method | Endpoint | Status | Description |
|--------|----------|--------|-------------|
| GET | `/` | 200 | List cases (paginated) |
| POST | `/` | 201 | Create new case |
| GET | `/{case_id}` | 200 | Get case details |
| PUT | `/{case_id}` | 200 | Update case |
| DELETE | `/{case_id}` | 204 | Delete case (soft delete) |

**Future Endpoints** (Week 2+):

- `POST /api/v1/observations` - Create observations
- `GET /api/v1/observations` - List observations
- `POST /api/v1/conflicts/detect` - Detect conflicts
- `GET /api/v1/reports` - List reports
- `POST /api/v1/reports/generate` - Generate report
- WebSocket `/ws` - Real-time updates

## Authentication

### JWT Tokens

All protected endpoints require a Bearer token in the `Authorization` header:

```bash
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8000/api/v1/cases
```

### Token Types

- **Access Token**: 60-minute expiry, used for API requests
- **Refresh Token**: 7-day expiry, used to obtain new access token

### Example Login Flow

```bash
# 1. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "analyst@example.com",
    "password": "securepassword123"
  }'

# Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}

# 2. Use access token
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8000/api/v1/auth/me

# 3. Refresh token (before expiry)
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<refresh_token>"}'
```

## Role-Based Access Control

### Roles

| Role | Permissions | Use Case |
|------|-------------|----------|
| **analyst** | Create own cases/observations, read own cases | Analyst conducting research |
| **lead_partner** | Full case/observation access, approve observations, generate reports | Lead partner overseeing deal |
| **ic_member** | Read all cases/observations, approve/resolve conflicts, export reports | Investment committee member |
| **admin** | Full system access | System administrator |

### Permission Examples

```python
# Only analysts see their own cases
GET /api/v1/cases  # Returns only cases created by user

# Lead partners and IC members see all
GET /api/v1/cases  # Returns all cases in system

# Create observations (analyst)
POST /api/v1/observations  # Allowed for analysts and above

# Approve observations (lead_partner, ic_member, admin)
PUT /api/v1/observations/{id}/approve  # Restricted to lead_partner+

# Generate reports (ic_member, admin)
POST /api/v1/reports/generate  # Restricted to ic_member+
```

## Configuration

### Environment Variables

**Database**:
```
DATABASE_URL=postgresql://user:password@localhost:5432/fund_ic_dev
DATABASE_ECHO=True  # SQL logging (development only)
```

**Security**:
```
JWT_SECRET=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
```

**Application**:
```
APP_NAME=Fund IC Automation System
APP_VERSION=1.0.0
DEBUG=True
ENVIRONMENT=development  # development|staging|production
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

**OpenAI**:
```
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o
LLM_TEMPERATURE_EXTRACTION=0.1
LLM_TEMPERATURE_GENERATION=0.3
```

**Logging**:
```
LOG_LEVEL=INFO  # DEBUG|INFO|WARNING|ERROR|CRITICAL
```

**Retry Settings**:
```
MAX_RETRIES=3
INITIAL_RETRY_DELAY=2  # seconds
MAX_RETRY_DELAY=30  # seconds
```

**File Upload**:
```
MAX_UPLOAD_SIZE_MB=50
UPLOAD_DIRECTORY=./uploads
```

## Error Handling

### Error Response Format

All errors return consistent JSON format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "field_name": "error description"
    },
    "request_id": "req_abc123def456"
  }
}
```

### Error Codes

| Code | HTTP Status | Meaning |
|------|-------------|---------|
| `VALIDATION_ERROR` | 400 | Input validation failed |
| `AUTHENTICATION_ERROR` | 401 | Invalid credentials |
| `AUTHORIZATION_ERROR` | 403 | Permission denied |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT_ERROR` | 409 | Data conflict detected |
| `RATE_LIMIT_ERROR` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

### Request IDs

Every request gets a unique `X-Request-ID` header for tracing:

```
Response headers:
X-Request-ID: req_abc123def456
```

Use this ID to correlate logs and debug issues.

## Development

### Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Settings management
│   ├── database.py             # Database setup
│   ├── core/
│   │   ├── security.py         # JWT & RBAC
│   │   └── errors.py           # Exception classes
│   ├── models/
│   │   └── schemas.py          # Pydantic models
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py         # Auth endpoints
│   │       └── cases.py        # Case endpoints
│   ├── services/               # Business logic (TODO)
│   └── utils/                  # Helper functions (TODO)
├── migrations/                 # Database migrations (TODO)
├── tests/                      # Test suites (TODO)
├── requirements.txt
└── README.md
```

### Adding New Endpoints

1. **Create endpoint file** in `app/api/v1/`:
```python
from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.database import get_db

router = APIRouter()

@router.get("/endpoint")
async def endpoint_handler(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Endpoint documentation"""
    pass
```

2. **Register router** in `app/api/v1/__init__.py`:
```python
from app.api.v1.new_module import router as new_router
router.include_router(new_router, prefix="/resource", tags=["Resource"])
```

3. **Test endpoint** using Swagger UI or curl

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test
pytest tests/test_auth.py::test_login

# Run in watch mode
pytest-watch
```

### Code Style

This project uses:
- **Black** for code formatting: `black app/`
- **isort** for import organization: `isort app/`
- **pylint** for linting: `pylint app/`
- **mypy** for type checking: `mypy app/`

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic current
```

## Deployment

### Docker

```bash
# Build image
docker build -t fund-ic-backend .

# Run container
docker run -p 8000:8000 \
  --env-file .env.production \
  fund-ic-backend

# Using Docker Compose
docker-compose up -d backend
```

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Update `JWT_SECRET` to strong random value
- [ ] Configure production database URL
- [ ] Set `ENVIRONMENT=production`
- [ ] Disable OpenAPI docs (`DEBUG=False` disables automatically)
- [ ] Configure CORS properly (limit origins)
- [ ] Set up Redis for caching
- [ ] Enable HTTPS/TLS
- [ ] Configure logging to file
- [ ] Set up monitoring/alerting
- [ ] Run database migrations
- [ ] Load SSL certificates

## Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

### Database Connection Status

```bash
curl http://localhost:8000/api/v1/admin/db-status  # TODO: Implement
```

### Logs

```bash
# View logs
tail -f logs/app.log

# Filter by request ID
grep "req_abc123def456" logs/app.log
```

## Troubleshooting

### Database Connection Issues

```
ERROR: could not connect to server: Connection refused
```

**Solution**: Ensure PostgreSQL is running and DATABASE_URL is correct

```bash
# Test connection
psql postgresql://user:password@localhost:5432/fund_ic_dev
```

### JWT Token Errors

```json
{
  "error": {
    "code": "AUTHENTICATION_ERROR",
    "message": "Invalid token"
  }
}
```

**Solutions**:
- Token may be expired - use refresh endpoint
- Token may be malformed - check format
- JWT_SECRET may not match - verify config

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

## API Specification

See detailed API specification in `../docs/API_SPECIFICATION.md` including:
- All endpoints with examples
- Request/response schemas
- Error codes
- Rate limiting
- Pagination

## Architecture Documentation

See `../docs/ARCHITECTURE.md` for:
- System architecture diagram
- Data flow
- Component interactions
- Technology stack rationale
- Security design
- Performance optimization

## RBAC Specification

See `../docs/RBAC_SPECIFICATION.md` for:
- Detailed role definitions
- Permission matrix
- Data masking rules
- Audit logging requirements
- Access control implementation

## Contributing

1. Create feature branch: `git checkout -b feature/name`
2. Make changes and test: `pytest`
3. Commit with clear message: `git commit -m "feat: description"`
4. Push and create Pull Request
5. Address review comments
6. Merge when approved

## Support

For issues or questions:
1. Check existing GitHub issues
2. Review documentation in `docs/`
3. Check application logs
4. Contact development team

## License

Internal use only - Fund IC Automation System
