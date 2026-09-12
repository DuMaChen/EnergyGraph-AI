from fastapi.testclient import TestClient

from app.main import app, upstream_error_type, upstream_url


client = TestClient(app)


def test_health(monkeypatch):
    monkeypatch.setenv("MOCK_MODE", "true")
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_mock(monkeypatch):
    monkeypatch.setenv("MOCK_MODE", "true")
    response = client.post(
        "/v1/chat/completions",
        json={"model": "gpt-5.6", "messages": [{"role": "user", "content": "测试"}]},
    )
    assert response.status_code == 200
    assert response.json()["choices"][0]["message"]["role"] == "assistant"


def test_chat_rejects_empty_messages(monkeypatch):
    monkeypatch.delenv("MOCK_MODE", raising=False)
    response = client.post("/v1/chat/completions", json={"messages": []})
    assert response.status_code == 400


def test_chat_rejects_missing_model(monkeypatch):
    monkeypatch.setenv("MOCK_MODE", "true")
    response = client.post(
        "/v1/chat/completions",
        json={"messages": [{"role": "user", "content": "测试"}]},
    )
    assert response.status_code == 400


def test_embedding_mock(monkeypatch):
    monkeypatch.setenv("MOCK_EMBEDDINGS", "true")
    monkeypatch.setenv("MOCK_EMBEDDING_DIMENSION", "8")
    response = client.post("/v1/embeddings", json={"input": ["储能"]})
    assert response.status_code == 200
    assert len(response.json()["data"][0]["embedding"]) == 8


def test_upstream_url_accepts_provider_root_or_v1_root():
    assert upstream_url("https://provider.example.com", "/v1/chat/completions") == (
        "https://provider.example.com/v1/chat/completions"
    )
    assert upstream_url("https://provider.example.com/v1", "/v1/chat/completions") == (
        "https://provider.example.com/v1/chat/completions"
    )


def test_chat_mock_stream_has_done_marker(monkeypatch):
    monkeypatch.setenv("MOCK_MODE", "true")
    response = client.post(
        "/v1/chat/completions",
        json={"model": "gpt-5.6", "stream": True, "messages": [{"role": "user", "content": "测试"}]},
    )
    assert response.status_code == 200
    assert "chat.completion.chunk" in response.text
    assert response.text.rstrip().endswith("data: [DONE]")


def test_upstream_error_types_are_normalized():
    assert upstream_error_type(401) == "authentication_error"
    assert upstream_error_type(429) == "rate_limit_error"
    assert upstream_error_type(500) == "upstream_error"
