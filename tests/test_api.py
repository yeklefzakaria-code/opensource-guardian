from fastapi.testclient import TestClient

from guardian.api import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_review_endpoint_uses_local_rules():
    response = client.post(
        "/v1/review",
        json={"diff": "+++ b/app.py\n@@ -0,0 +1 @@\n+requests.get(url, verify=False)", "use_ai": False},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["ai_reviewed"] is False
    assert payload["findings"][0]["rule_id"] == "OG002"


def test_rejects_empty_diff():
    response = client.post("/v1/review", json={"diff": "", "use_ai": False})
    assert response.status_code == 422


def test_dashboard_is_served():
    response = client.get("/")
    assert response.status_code == 200
    assert "OpenSource Guardian" in response.text
    assert "Analyze diff" in response.text


def test_sarif_endpoint_returns_sarif_media_type():
    response = client.post(
        "/v1/review/sarif",
        json={
            "diff": "+++ b/client.py\n@@ -0,0 +1 @@\n+requests.get(url, verify=False)",
            "use_ai": False,
        },
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/sarif+json")
    report = response.json()
    assert report["version"] == "2.1.0"
    assert report["runs"][0]["results"][0]["ruleId"] == "OG002"
