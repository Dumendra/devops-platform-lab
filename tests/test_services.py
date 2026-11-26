import apps.gateway.app as gateway
import apps.orders.app as orders
import apps.users.app as users


def client(app):
    app.config.update(TESTING=True)
    return app.test_client()


def test_gateway_index_and_health(monkeypatch):
    monkeypatch.setenv("SERVICE_NAME", "gateway")
    test_client = client(gateway.create_app())

    response = test_client.get("/")

    assert response.status_code == 200
    assert response.get_json()["service"] == "gateway"
    assert test_client.get("/health").get_json()["status"] == "ok"


def test_gateway_metrics():
    test_client = client(gateway.create_app())
    response = test_client.get("/metrics")

    assert response.status_code == 200
    assert "http_requests_total" in response.get_data(as_text=True)


def test_gateway_proxies_users(monkeypatch):
    gateway._cache.update(payload=None, expires=0)
    monkeypatch.delenv("REDIS_URL", raising=False)
    monkeypatch.setattr(gateway, "fetch_json", lambda url: {"users": [{"id": 9}]})
    test_client = client(gateway.create_app())

    response = test_client.get("/api/users")

    assert response.get_json() == {"users": [{"id": 9}]}


def test_gateway_uses_configured_orders_url(monkeypatch):
    seen = {}

    def fake_fetch(url):
        seen["url"] = url
        return {"orders": []}

    monkeypatch.setenv("ORDERS_URL", "http://orders:8000")
    monkeypatch.setattr(gateway, "fetch_json", fake_fetch)
    test_client = client(gateway.create_app())

    assert test_client.get("/api/orders").status_code == 200
    assert seen["url"] == "http://orders:8000/orders"


def test_order_lifecycle(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    orders._memory.update(orders=[], next_id=1)
    test_client = client(orders.create_app())

    response = test_client.post("/orders", json={"item": "widget", "qty": 2})

    assert response.status_code == 201
    assert test_client.get("/orders").get_json()["orders"][0]["item"] == "widget"


def test_order_validation(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    test_client = client(orders.create_app())

    assert test_client.post("/orders", json={"qty": 1}).status_code == 400


def test_user_lifecycle():
    users._memory.update(users=[{"id": 1, "name": "Ada"}], next_id=2)
    test_client = client(users.create_app())

    response = test_client.post("/users", json={"name": "Grace"})

    assert response.status_code == 201
    assert test_client.get("/users").get_json()["users"][1]["name"] == "Grace"


def test_user_validation():
    test_client = client(users.create_app())

    assert test_client.post("/users", json={}).status_code == 400
