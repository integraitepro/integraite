# Integraite Backend API

FastAPI backend for the Integraite Autonomous Self-Healing Ops platform.

## Features

- **Multi-tenant Architecture**: Organization-based data isolation
- **Authentication & Authorization**: JWT-based auth with RBAC
- **Agent Management**: AI agent deployment and monitoring
- **Incident Management**: Autonomous incident detection and resolution
- **Integrations**: Support for 50+ external services
- **Billing**: Stripe integration for subscription management
- **Audit Logging**: Comprehensive activity tracking

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -e .
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run migrations:
```bash
alembic upgrade head
```

5. Start the server:
```bash
uvicorn app.main:app --reload
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

Install dev dependencies:
```bash
pip install -e ".[dev]"
```

Run tests:
```bash
pytest
```

Format code:
```bash
black .
isort .
```

Type checking:
```bash
mypy .
```
