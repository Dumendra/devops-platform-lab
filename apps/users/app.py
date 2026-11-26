import os

from flask import Flask, jsonify, request

from common import health_payload, metrics, service_name, track

_memory = {"users": [{"id": 1, "name": "Ada"}], "next_id": 2}


def list_users():
    return {"users": _memory["users"]}


def add_user(name):
    user = {"id": _memory["next_id"], "name": name}
    _memory["next_id"] += 1
    _memory["users"].append(user)
    return user


def create_app():
    app = Flask(__name__)
    service = service_name("users")

    @app.get("/health")
    def health():
        return jsonify(health_payload())

    @app.get("/ready")
    def ready():
        return jsonify(status="ready")

    @app.get("/metrics")
    def prometheus_metrics():
        return metrics()

    @app.get("/users")
    def users():
        track(service, "list_users")
        return jsonify(list_users())

    @app.post("/users")
    def create_user():
        track(service, "create_user")
        body = request.get_json(silent=True) or {}
        name = body.get("name")
        if not name:
            return jsonify(error="name is required"), 400
        return jsonify(add_user(name)), 201

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
