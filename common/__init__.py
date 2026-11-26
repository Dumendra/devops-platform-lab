import os
import time

from flask import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, generate_latest

START = time.time()
REQUESTS = Counter("http_requests_total", "Total HTTP requests", ["service", "endpoint"])
UPTIME = Gauge("app_uptime_seconds", "Process uptime in seconds")
UPTIME.set(0)


def service_name(default):
    return os.getenv("SERVICE_NAME", default)


def track(service, endpoint):
    REQUESTS.labels(service, endpoint).inc()


def metrics():
    UPTIME.set(time.time() - START)
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


def health_payload(extra=None):
    payload = {
        "status": "ok",
        "service": service_name("unknown"),
        "version": os.getenv("APP_VERSION", "dev"),
        "environment": os.getenv("APP_ENV", "local"),
    }
    if extra:
        payload.update(extra)
    return payload
