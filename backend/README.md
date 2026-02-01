# MentAI Backend

AI-powered learning assistant backend built with Django and Django REST Framework.

## Endpoints

### Core Endpoints
- `GET /`: Basic status check. Returns `{"status": "MentAI backend is running"}`.
- `GET /health`: Detailed health check. Returns service status, name, and environment.

### API v1 (`/api/v1/`)
- `POST /api/v1/ask`: Submit a query to MentAI.
  - **Request Body**: `{"query": "..."}`
  - **Response**: `{"answer": "...", "timestamp": "..."}`

## Deployment
Deployed on Railway using Nixpacks.
- **Root Directory**: `backend`
- **Builder**: `Nixpacks`
- **Port**: Listens on `0.0.0.0:$PORT` (configured via `gunicorn`).

## Configuration
- **CORS**: Configured to allow requests from localhost (3000, 3001, 5173) and any origins specified in `CORS_ALLOWED_ORIGINS`.
- **Environment Variables**:
  - `DJANGO_SECRET_KEY`: Secret key for production.
  - `DJANGO_DEBUG`: Set to `False` in production.
  - `ALLOWED_HOSTS`: List of allowed hostnames.
  - `CORS_ALLOWED_ORIGINS`: List of allowed CORS origins.
  - `DATABASE_URL`: Railway database connection string.
