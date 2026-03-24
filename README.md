

<h1>RateShield – Rate Limiter &amp; Gateway</h1>
<p class="subtitle">Python · FastAPI · Redis · PostgreSQL · SQLAlchemy · Docker · AWS EC2</p>

<p>
  Production-grade distributed API Gateway with route-aware rate limiting, JWT-based auth, and role-based access control.
  Three containerized services orchestrated via Docker Compose, deployed on AWS EC2.
</p>

<div class="badges">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Redis">
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/AWS_EC2-FF9900?style=for-the-badge&logo=amazonec2&logoColor=white" alt="AWS EC2">
  <img src="https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white" alt="JWT">
</div>

<h2>Overview</h2>
<ul>
  <li>Distributed API gateway with 3 containerized services — API, Redis, PostgreSQL — wired via Docker Compose and hosted on AWS EC2.</li>
  <li>Route-aware sliding window rate limiter using Redis Sorted Sets; returns <code>429 Too Many Requests</code> with <code>Retry-After</code> headers on violation.</li>
  <li>JWT authentication with OAuth2-style token issuance and RBAC across <code>basic</code>, <code>premium</code>, and <code>admin</code> tiers.</li>
  <li>Resilient middleware with graceful in-memory fallback on Redis failure — no hard crash, no dropped requests.</li>
</ul>

<h2>Endpoints</h2>
<ul>
  <li><code>POST /auth/register</code> — register a client with name, tier, and secret</li>
  <li><code>POST /auth/token</code> — issue a signed JWT via OAuth2 password flow</li>
  <li><code>GET /</code> — protected root</li>
  <li><code>GET /me</code> — returns authenticated client identity and tier</li>
  <li><code>GET /admin/health</code> — admin-tier-only health check</li>
</ul>

<h2>Rate Limiting</h2>
<ul>
  <li>Algorithm: sliding window using Redis Sorted Sets — precise burst control under high concurrency</li>
  <li>Per-scope limits: <code>/auth/register</code>, <code>/auth/token</code>, general authenticated routes</li>
  <li>Response headers: <code>X-RateLimit-Limit</code>, <code>X-RateLimit-Remaining</code>, <code>X-RateLimit-Window</code></li>
  <li>Fallback: in-memory limiter activates automatically when Redis is unreachable</li>
</ul>

<h2>Auth &amp; Access Control</h2>
<ul>
  <li>Client secrets hashed with <code>pbkdf2_sha256</code> via passlib — never stored in plaintext</li>
  <li>Signed JWT tokens with configurable expiry via <code>python-jose</code></li>
  <li>Tier guards as reusable FastAPI dependencies — clean, composable, testable</li>
  <li>Invalid credentials → <code>401</code>. Insufficient tier → <code>403</code>.</li>
</ul>

<h2>Stack</h2>
<ul>
  <li><strong>Framework:</strong> FastAPI + Uvicorn (ASGI)</li>
  <li><strong>Auth:</strong> python-jose (JWT), passlib (hashing)</li>
  <li><strong>ORM:</strong> SQLAlchemy — PostgreSQL primary, SQLite fallback on init failure</li>
  <li><strong>Rate limiting:</strong> Redis Sorted Sets, in-memory fallback</li>
  <li><strong>Validation:</strong> Pydantic</li>
  <li><strong>Infra:</strong> Docker Compose · AWS EC2</li>
</ul>

<h2>Config</h2>
<p>Environment-driven via <code>.env</code> or Docker Compose:</p>
<ul>
  <li><code>JWT_SECRET</code>, <code>JWT_ALGORITHM</code>, <code>TOKEN_EXPIRY</code></li>
  <li><code>REDIS_URL</code></li>
  <li><code>DATABASE_URL</code></li>
  <li>Per-route and per-tier rate limit thresholds</li>
</ul>

<hr>

<p class="note">Core auth, rate limiting, and RBAC are fully implemented. Planned: persistent API request logging, blocked IP enforcement, dynamic route policies, and automated test coverage.</p>

</body>
</html>