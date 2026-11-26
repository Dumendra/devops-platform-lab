import json
import os
import time
import urllib.request

from flask import Flask, jsonify
from redis import Redis

from common import health_payload, metrics, service_name, track

CACHE_TTL = 30
_cache = {"payload": None, "expires": 0}


def fetch_json(url, timeout=3):
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return json.load(response)


def orders_url():
    return os.getenv("ORDERS_URL", "http://orders:8000")


def users_url():
    return os.getenv("USERS_URL", "http://users:8000")


def redis_client():
    url = os.getenv("REDIS_URL")
    if not url:
        return None
    return Redis.from_url(url, decode_responses=True, socket_connect_timeout=2)


def create_app():
    app = Flask(__name__)
    service = service_name("gateway")

    @app.get("/health")
    def health():
        return jsonify(health_payload())

    @app.get("/ready")
    def ready():
        return jsonify(status="ready")

    @app.get("/metrics")
    def prometheus_metrics():
        return metrics()

    @app.get("/")
    def index():
        track(service, "index")
        return jsonify(
            service=service,
            downstreams={"orders": orders_url(), "users": users_url()},
        )

    @app.get("/api/orders")
    def orders():
        track(service, "orders")
        return jsonify(fetch_json(f"{orders_url()}/orders"))

    @app.get("/api/users")
    def users():
        track(service, "users")
        now = time.monotonic()
        if _cache["payload"] is not None and _cache["expires"] > now:
            return jsonify(_cache["payload"])

        client = redis_client()
        if client:
            try:
                cached = client.get("gateway:users")
                if cached:
                    payload = json.loads(cached)
                    _cache.update(payload=payload, expires=now + CACHE_TTL)
                    return jsonify(payload)
            except Exception:
                pass

        payload = fetch_json(f"{users_url()}/users")
        _cache.update(payload=payload, expires=now + CACHE_TTL)
        if client:
            try:
                client.setex("gateway:users", CACHE_TTL, json.dumps(payload))
            except Exception:
                pass
        return jsonify(payload)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
