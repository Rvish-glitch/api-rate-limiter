# API Rate Limiter (FastAPI)

Production-oriented FastAPI service focused on API authentication, tier-aware authorization, and resilient request throttling.

## Overview

This project provides a backend foundation for client-authenticated APIs where each request is protected by JWT, validated against stored client records, and rate-limited with Redis-backed sliding windows.

The service is designed for controlled multi-tenant API access with clear separation of concerns:
- Authentication and token issuance
- Authorization and tier enforcement
- Request-level throttling and abuse protection
- Database-backed client records

## Key Features

### 1) JWT-based Authentication
- Client registration with hashed secret storage
- Token issuance through OAuth2 password flow compatible endpoint
- Signed JWT access tokens with configurable expiry
- Token decoding and validation in dependency layer

### 2) Role/Tier-aware Authorization
- Tier model: basic, premium, admin
- Reusable dependency to enforce allowed tiers per route
- Example admin-only protected endpoint implemented

### 3) Sliding-window Rate Limiting (Redis)
- Middleware-level throttling for incoming requests
- Redis sorted-set window tracking for precise rolling limits
- Endpoint-specific scopes and limits:
	- Register requests
	- Token requests
	- General authenticated requests
- Response headers added for client visibility:
	- X-RateLimit-Limit
	- X-RateLimit-Remaining
	- X-RateLimit-Window

### 4) Resilient Fallback Behavior
- In-memory fallback limiter when Redis is temporarily unavailable
- Protected docs/OpenAPI routes excluded from limiter
- Graceful 429 responses with scope and window metadata

### 5) Database-backed Client Management
- SQLAlchemy models for clients and supporting entities
- Startup schema creation
- Automatic fallback to SQLite if PostgreSQL is unreachable at init

## API Surface (Current)

### Authentication
- POST /auth/register
	- Registers a client with name, tier, and secret
- POST /auth/token
	- Issues JWT access token for valid credentials

### Protected
- GET /
	- Protected root message
- GET /me
	- Returns authenticated client identity and tier
- GET /admin/health
	- Admin-tier-only health endpoint

## Security Notes

- Client secrets are stored as one-way hashes using passlib
- JWT signing is centralized and configurable by environment
- Invalid or missing credentials return standard OAuth-style 401 responses
- Tier-based access checks return 403 for insufficient privileges

## Configuration

Environment-driven configuration is supported for:
- JWT secret, algorithm, and token expiry
- Redis URL
- Rate-limit window and tier/route thresholds
- Database URL

Default values are present for local development safety, but production environments should always override sensitive defaults.

## Technologies Involved

- Language: Python 3.10
- API Framework: FastAPI
- ASGI Server: Uvicorn
- Data Validation: Pydantic
- ORM: SQLAlchemy
- Database: PostgreSQL (with SQLite fallback)
- Cache/Rate-limit store: Redis
- Authentication: OAuth2 Password flow + JWT (`python-jose`)
- Password Hashing: Passlib (`pbkdf2_sha256`)
- DB Drivers: `asyncpg`, `psycopg2-binary`
- Containerization: Docker, Docker Compose

## Project Structure

- main.py
	- FastAPI app entrypoint, middleware wiring, router inclusion
- app/core/
	- Config, Redis client, security utilities
- app/routers/
	- Authentication and protected route definitions
- app/dependencies/
	- Current-client resolution and tier guards
- app/middleware/
	- Rate limiting middleware implementation
- app/models/
	- SQLAlchemy ORM models
- app/schemas.py
	- Pydantic request/response contracts

## Infrastructure

Containerized stack includes:
- FastAPI application container
- Redis for rate-limiting state
- PostgreSQL for persistent relational data

Docker and Compose files are present for consistent environment provisioning.

## Current Status

The project is actively in development. Core authentication, authorization, and request-throttling capabilities are already implemented and ready for iterative hardening.

## Planned Enhancements

- Persist and expose API request logs from APILog model
- Activate and enforce blocked IP logic from BlockedIP model
- Dynamic per-route policy management using Route model
- Expand observability and operational metrics
- Add dedicated automated test coverage