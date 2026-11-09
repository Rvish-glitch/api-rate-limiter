# RateShield

A distributed API gateway built with FastAPI, Redis, and PostgreSQL. Features route-aware sliding-window rate limiting, JWT token issuance, and tier-based RBAC (`basic`, `premium`, `admin`).

[![Python](https://img.shields.io/badge/Python_3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic_v2-E92063?style=for-the-badge&logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![uv](https://img.shields.io/badge/uv-DE5FE9?style=for-the-badge&logo=astral&logoColor=white)](https://docs.astral.sh/uv/)
[![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)](https://jwt.io/)
[![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)](https://pytest.org/)

---

## Why I Built This

Most API rate limiting examples use fixed-window counters, which suffer from the classic boundary-burst flaw (e.g., doubling traffic right at the edge of the reset window).

RateShield solves this with a **sliding window counter implemented via Redis Sorted Sets (ZSET)**. Timestamps are scored in epoch milliseconds, stale requests are evicted on every check, and rate checks happen in atomic Redis pipelines.

If Redis drops or crashes, RateShield doesn't crash your API—it automatically switches to an in-memory sliding window fallback with circuit-breaking so traffic keeps flowing.

---

## What's Inside

- **Sliding-Window Rate Limiter**: Sub-second precision bursts protection with Redis Sorted Sets + thread-safe in-memory fallback.
- **Client Identity & RBAC**: Client accounts with access tiers (`basic`, `premium`, `admin`) enforced via FastAPI dependency guards.
- **JWT Auth**: Passwords hashed with PBKDF2 (`pbkdf2_sha256`), signed access tokens with configurable expiration.
- **Dynamic Proxy Registry**: Store and manage upstream destinations (`Route` model) and access controls (`BlockedIP`).
- **Clean Layered Architecture**: Strict separation of concerns (`api/` ➔ `services/` ➔ `models/` + `schemas/` + `utils/`).
- **Modern Python Toolchain**: Powered by `uv` for lightning-fast deterministic builds and dependency locking.

---

## Architecture

```
Incoming Request
      │
      ▼
RateLimitMiddleware (Inspects IP / Bearer Token, checks sliding window in Redis)
      │
      ▼
API Routers (/api/v1/...) ──► FastAPI Dependencies (DB Session, Auth, Tiers)
      │
      ▼
Service Layer (AuthService, RateLimitService, ClientService, RouteService)
      │
  ┌───┴───────────────────────┐
  ▼                           ▼
PostgreSQL / SQLite      Redis Cache
(Client, Route, APILog)  (Sliding-window ZSETs)
```

---

## API Endpoints

All endpoints are versioned under `/api/v1/`:

| Method | Endpoint | Description | Auth / Tier |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Register new client identity & tier | Public |
| `POST` | `/api/v1/auth/tokens` | Issue OAuth2 Bearer access token | Public |
| `GET` | `/api/v1/clients/me` | Fetch profile for authenticated client | Basic / Premium / Admin |
| `GET` | `/api/v1/clients` | List registered clients (paginated) | Admin only |
| `GET` | `/api/v1/clients/{id}` | Inspect client details by ID | Admin only |
| `GET` | `/api/v1/rate-limits/status` | Current quota consumption & reset timer | Basic / Premium / Admin |
| `GET` | `/api/v1/rate-limits/policies` | Active rate limit tier configurations | Admin only |
| `GET` | `/api/v1/routes` | List registered upstream routes | Admin only |
| `POST` | `/api/v1/routes` | Add a new upstream proxy route | Admin only |
| `DELETE` | `/api/v1/routes/{id}` | Remove an upstream route | Admin only |
| `GET` | `/api/v1/blocked-ips` | View active IP blocklist | Admin only |
| `POST` | `/api/v1/blocked-ips` | Add an IP address to blocklist | Admin only |
| `DELETE` | `/api/v1/blocked-ips/{ip}` | Remove IP from blocklist | Admin only |
| `GET` | `/api/v1/system/health` | Health check verifying DB & Redis | Public |
| `GET` | `/api/v1/system/metrics` | Gateway throughput & counters | Admin only |

---

## Rate Limit Headers

Every response carries standard rate limit headers:

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 58
X-RateLimit-Reset: 1731149200
```

When quota is exceeded, RateShield responds with `429 Too Many Requests`:

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please wait before retrying.",
    "details": {
      "limit": 60,
      "window_seconds": 60,
      "retry_after_seconds": 12
    }
  }
}
```

---

## Quickstart

### Prerequisites
- Python 3.10+ (tested on 3.12)
- [uv](https://docs.astral.sh/uv/) installed
- Docker & Docker Compose (optional for local DB/Redis)

### 1. Clone & install dependencies
```bash
git clone https://github.com/your-username/rateshield.git
cd rateshield

# Install dependencies using uv
uv sync
```

### 2. Start infrastructure (Redis & PostgreSQL)
```bash
docker compose up -d redis db
```
*(If you run without Docker, RateShield automatically falls back to local SQLite and in-memory rate limiting).*

### 3. Run the gateway
```bash
uv run uvicorn app.main:app --reload --port 8000
```

Interactive Swagger docs will be live at `http://localhost:8000/docs`.

---

## Quick Curl Walkthrough

**1. Register a new client:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "alex", "tier": "premium", "secret": "mypassword123"}'
```

**2. Grab an access token:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/tokens \
  -F "username=alex" \
  -F "password=mypassword123"
```

**3. Check your profile:**
```bash
curl -X GET http://localhost:8000/api/v1/clients/me \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

**4. Check your real-time rate limit quota:**
```bash
curl -X GET http://localhost:8000/api/v1/rate-limits/status \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

---

## Testing

Run the test suite with `uv`:

```bash
uv run pytest
```
