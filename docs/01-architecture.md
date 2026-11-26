# Lesson 1: Architecture

## Learning goals

- Explain each component and why it exists.
- Trace a request from the internet to the database.
- Identify failure domains and deployment boundaries.
- Explain how Git connects CI, the registry, and the cluster.

## System context

The platform is small enough to understand, but shaped like a real system:

```text
Internet -> Ingress -> gateway -> orders -> Postgres
                          | -> users
                          | -> Redis
```

| Component | Responsibility                                              |
| --------- | ----------------------------------------------------------- |
| gateway   | Public entry point, aggregates downstream APIs, caches users |
| orders    | Owns order records and the database schema                  |
| users     | Owns user records in memory for simplicity                  |
| Postgres  | Durable storage for orders                                  |
| Redis     | Short-lived cache in front of users                         |
| Ingress   | HTTP routing and the single public hostname                 |

Each service owns its data. The gateway does not write to Postgres; it calls the
owning service. That boundary is what makes independent scaling and deployment
possible.

## Request flow

1. A client requests `GET /api/orders` on `platform.local`.
2. Ingress routes to the gateway Service.
3. The gateway calls `orders:8000/orders` using `ORDERS_URL`.
4. Orders queries Postgres using `DATABASE_URL`.
5. The response travels back through the gateway.

A `GET /api/users` request first checks the in-process cache, then Redis, then
the users service. This teaches two caching layers and two invalidation problems.

## Delivery flow

```text
commit -> CI -> GHCR -> Git values update -> ArgoCD -> cluster
```

CI owns build and test. ArgoCD owns deployment. Nothing pushes directly to the
cluster from CI in this project. That separation makes the deployed state
visible in Git and reviewable by humans.

## Failure domains

- If Postgres is down, orders returns errors but users still works.
- If Redis is down, the gateway falls back to calling users directly.
- If users is down, cached user data may still be served for 30 seconds.
- If the gateway is down, the whole public API is unavailable.

Write these down before designing alerts. A good alert targets a user-visible
failure, not a random pod restart.

## Trade-offs to discuss

- One Dockerfile for all services is simple to teach but installs all
  dependencies into every image. A production setup would use per-service
  requirements or a shared base layer.
- In-memory users are easy to reset, but not durable. Replace with a database
  when teaching migrations.
- Helm values hold a lab database password. Use External Secrets or a secrets
  manager in real environments.
- ArgoCD prod sync is manual, which is slower but safer than automatic sync.

## Exercises

### Exercise 1.1: Draw the system

Draw the request flow and mark where each environment variable is used. Include
`ORDERS_URL`, `USERS_URL`, `REDIS_URL`, `DATABASE_URL`, and `SERVICE_NAME`.

### Exercise 1.2: Failure injection

List what happens when each component is deleted. Then verify one case by
scaling Redis to zero and calling `/api/users`.

### Exercise 1.3: Add a service

Plan a `notifications` service: which ports, endpoints, data store, URLs, and
Helm values would it need? Do not implement it yet.

### Exercise 1.4: Boundaries

Explain why the gateway should not connect directly to Postgres. What breaks if
two services share a database schema?

## Checkpoint

You can explain the request path, the delivery path, and at least three failure
modes without looking at this file.
