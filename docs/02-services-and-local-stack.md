# Lesson 2: Services and the local stack

## Learning goals

- Run and test the three services locally.
- Explain service contracts and environment-driven configuration.
- Understand Compose health checks and startup ordering.
- Observe caching and persistence behavior.

## Service contracts

| Service  | Endpoints                                   | Data             |
| -------- | ------------------------------------------- | ---------------- |
| gateway  | `/`, `/health`, `/ready`, `/metrics`, `/api/orders`, `/api/users` | Redis cache |
| orders   | `/orders` GET/POST, health and metrics       | Postgres         |
| users    | `/users` GET/POST, health and metrics        | In-memory        |

Every service exposes `/health` for liveness, `/ready` for traffic readiness,
and `/metrics` for Prometheus. The shared helpers live in `common/__init__.py`.

## Configuration

Configuration comes from the environment:

- `SERVICE_NAME`: name reported in health checks and metrics labels.
- `APP_ENV`, `APP_VERSION`: build and release metadata.
- `DATABASE_URL`: Postgres connection string used by orders.
- `REDIS_URL`: Redis connection string used by the gateway.
- `ORDERS_URL`, `USERS_URL`: downstream service URLs.

The same image runs everywhere; only configuration changes. That is the core
idea behind twelve-factor style applications.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python -m pytest -q

docker compose up --build
docker compose ps
docker compose logs -f gateway
```

Check each service:

```powershell
Invoke-RestMethod http://localhost:8080/health
Invoke-RestMethod http://localhost:8081/orders
Invoke-RestMethod http://localhost:8082/users
Invoke-RestMethod http://localhost:8080/api/users
```

## Health checks and startup order

Compose waits for Postgres and Redis to become healthy before starting
dependent services. A container can be "started" but not ready to serve. This
is why `depends_on` uses `condition: service_healthy`.

Each app container also has a Docker health check that calls `/health`. Later,
the Helm chart uses Kubernetes probes against the same endpoints.

## Persistence and caching

Orders creates its table at startup and stores rows in Postgres. The Compose
volume `postgres-data` keeps data across container restarts.

The gateway caches `/users` for 30 seconds in process and in Redis. If Redis is
unavailable, the gateway logs no secret and still calls users directly. This is
a graceful degradation pattern.

## Exercises

### Exercise 2.1: Add an endpoint

Add `GET /stats` to the gateway that returns counts of orders and users. Add a
test that mocks `fetch_json` and verifies the aggregated response.

### Exercise 2.2: Break the database

Stop Postgres and call `/orders`. Observe the error. Restart it and confirm the
data survived because of the named volume.

### Exercise 2.3: Cache behavior

Post a new user, then call `/api/users` twice. Explain why the new user may not
appear immediately. Change `CACHE_TTL` and observe when it appears.

### Exercise 2.4: Health vs readiness

Change the gateway readiness handler to fail and watch Kubernetes behavior in
the later lesson. Explain why a failing readiness probe does not restart a pod.

### Exercise 2.5: Load test

Use `hey` or `autocannon` to send traffic to the gateway. Watch request
counters on `/metrics` and explain what a rate of zero means.

## Checkpoint

You can start the stack, explain every environment variable, and describe why
health checks, readiness, and caching are separate concerns.
