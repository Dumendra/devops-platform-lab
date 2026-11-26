import os

from flask import Flask, jsonify, request

from common import health_payload, metrics, service_name, track

_memory = {"orders": [], "next_id": 1}


def connect():
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        return None
    import psycopg

    return psycopg.connect(dsn, autocommit=True)


def ensure_schema():
    conn = connect()
    if not conn:
        return
    with conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS orders "
            "(id SERIAL PRIMARY KEY, item TEXT NOT NULL, qty INTEGER NOT NULL)"
        )
    conn.close()


def list_orders():
    conn = connect()
    if not conn:
        return {"orders": _memory["orders"]}
    with conn:
        rows = conn.execute("SELECT id, item, qty FROM orders ORDER BY id").fetchall()
    conn.close()
    return {"orders": [{"id": row[0], "item": row[1], "qty": row[2]} for row in rows]}


def add_order(item, qty):
    conn = connect()
    if not conn:
        order = {"id": _memory["next_id"], "item": item, "qty": qty}
        _memory["next_id"] += 1
        _memory["orders"].append(order)
        return order
    with conn:
        row = conn.execute(
            "INSERT INTO orders (item, qty) VALUES (%s, %s) RETURNING id, item, qty",
            (item, qty),
        ).fetchone()
    conn.close()
    return {"id": row[0], "item": row[1], "qty": row[2]}


def create_app():
    app = Flask(__name__)
    service = service_name("orders")
    ensure_schema()

    @app.get("/health")
    def health():
        return jsonify(health_payload())

    @app.get("/ready")
    def ready():
        return jsonify(status="ready")

    @app.get("/metrics")
    def prometheus_metrics():
        return metrics()

    @app.get("/orders")
    def orders():
        track(service, "list_orders")
        return jsonify(list_orders())

    @app.post("/orders")
    def create_order():
        track(service, "create_order")
        body = request.get_json(silent=True) or {}
        item = body.get("item")
        qty = body.get("qty", 1)
        if not item or not isinstance(qty, int) or qty < 1:
            return jsonify(error="item and positive integer qty are required"), 400
        return jsonify(add_order(item, qty)), 201

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
