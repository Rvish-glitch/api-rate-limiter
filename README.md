# RateShield – High-Performance Distributed API Gateway

RateShield is a production-grade distributed API Gateway featuring route-aware sliding window rate limiting (Redis Sorted Sets with in-memory fallback), JWT authentication with OAuth2 password flows, and tier-based Role-Based Access Control (RBAC).

Orchestrated with Docker Compose and managed using [**`uv`**](https://docs.astral.sh/uv/).

---

## 🏗️ Layered Architecture

RateShield adheres to a strict, modular layered architecture:

- **`app/api/v1/`**: Versioned API routers parsing schemas, invoking services, and setting HTTP responses.
- **`app/schemas/`**: Pydantic v2 DTOs enforcing request validation and serialization.
- **`app/models/`**: SQLAlchemy 2.0 ORM models (`Client`, `Route`, `APILog`, `BlockedIP`).
- **`app/services/`**: Isolated business domain logic, transactions, and Redis cache coordination.
- **`app/utils/`**: Stateless cryptographic, network (client IP resolution), and window math helpers.
- **`app/core/`**: Infrastructure configurations, database engine, and Redis client.
- **`app/dependencies/`**: FastAPI dependency injection providers (`get_db`, `get_current_client`, `require_tier`, service providers).
- **`app/middleware/`**: Sliding-window rate limiter middleware with graceful in-memory fallback.

---

## 📦 Package Management with `uv`

All dependency management and script execution uses `uv`:

```bash
# Sync virtual environment from uv.lock
uv sync

# Run the API gateway locally with hot reload
uv run uvicorn app.main:app --reload

# Execute automated test suite
uv run pytest
```

---

## 🚀 API Endpoints (`/api/v1`)

| Method | Endpoint | Description | Access Tier | Status Code |
| :--- | :--- | :--- | :---: | :---: |
| `POST` | `/api/v1/auth/register` | Register client identity and tier | Public | `201 Created` |
| `POST` | `/api/v1/auth/tokens` | Issue OAuth2 Bearer access token | Public | `200 OK` |
| `GET` | `/api/v1/clients/me` | Current authenticated client profile | Basic / Premium / Admin | `200 OK` |
| `GET` | `/api/v1/clients` | List registered clients (paginated) | Admin | `200 OK` |
| `GET` | `/api/v1/clients/{client_id}` | Fetch client details by ID | Admin | `200 OK` |
| `GET` | `/api/v1/rate-limits/status` | Inspect remaining request quota | Basic / Premium / Admin | `200 OK` |
| `GET` | `/api/v1/rate-limits/policies` | Active tier rate limits | Admin | `200 OK` |
| `GET` | `/api/v1/routes` | List active upstream gateway routes | Admin | `200 OK` |
| `POST` | `/api/v1/routes` | Register new upstream proxy route | Admin | `201 Created` |
| `DELETE` | `/api/v1/routes/{route_id}` | Deactivate/remove upstream route | Admin | `204 No Content` |
| `GET` | `/api/v1/blocked-ips` | List blocked IP addresses | Admin | `200 OK` |
| `POST` | `/api/v1/blocked-ips` | Block an IP with reason | Admin | `201 Created` |
| `DELETE` | `/api/v1/blocked-ips/{ip}` | Unblock an IP address | Admin | `204 No Content` |
| `GET` | `/api/v1/system/health` | Gateway health check (DB + Redis) | Public | `200 OK` |
| `GET` | `/api/v1/system/metrics` | Gateway throughput & inventory counters | Admin | `200 OK` |

---

## ⚡ Rate Limiting Standards

- **Algorithm**: Sliding window using Redis Sorted Sets with epoch millisecond scoring.
- **Failover**: Automatic in-memory sliding window fallback if Redis is temporarily unreachable.
- **Standard Headers**:
  - `X-RateLimit-Limit`: Maximum requests permitted within the window.
  - `X-RateLimit-Remaining`: Remaining requests in current window.
  - `X-RateLimit-Reset`: Unix epoch timestamp when current window resets.
  - `Retry-After`: Seconds to wait on HTTP 429.
