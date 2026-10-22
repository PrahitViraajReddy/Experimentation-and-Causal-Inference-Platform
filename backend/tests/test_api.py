from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_power_calculator():
    response = client.post("/api/v1/power/sample-size", json={
        "metric_type": "continuous", "standard_deviation": 10,
        "minimum_detectable_effect": 2, "alpha": 0.05, "power": 0.8
    })
    assert response.status_code == 200
    body = response.json()
    assert body["total_sample_size"] == body["control_sample_size"] + body["treatment_sample_size"]
    assert body["control_sample_size"] > 0


def test_simulation_reproducible():
    payload = {"sample_size_per_arm": 50, "baseline_rate": 0.2, "absolute_effect": 0.05, "seed": 123}
    a, b = client.post("/api/v1/experiments/simulate", json=payload), client.post("/api/v1/experiments/simulate", json=payload)
    assert a.json()["control"] == b.json()["control"]
    assert a.json()["treatment"] == b.json()["treatment"]


def test_proportion_test_reports_effect():
    response = client.post("/api/v1/experiments/analyze", json={
        "method": "proportion_z", "control": [100, 1000], "treatment": [130, 1000]
    })
    assert response.status_code == 200
    assert response.json()["effect"]["absolute_lift"] > 0
    assert 0 <= response.json()["p_value"] <= 1


def test_bonferroni_adjustment():
    response = client.post("/api/v1/experiments/multiple-testing", json={
        "p_values": [0.01, 0.04, 0.2], "method": "bonferroni"
    })
    assert response.status_code == 200
    assert response.json()["results"][0]["adjusted_p_value"] == 0.03


def test_invalid_simulation_is_rejected():
    response = client.post("/api/v1/experiments/simulate", json={
        "sample_size_per_arm": 50, "baseline_rate": 0.8, "absolute_effect": 0.3, "seed": 1
    })
    assert response.status_code == 422

def test_root_landing_route():
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "running"
    assert body["docs"] == "/docs"
    assert body["health"] == "/api/v1/health"
