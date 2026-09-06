from pathlib import Path

from app import ingest


def test_course_data_directory_is_defined():
    assert Path("app/ingest.py").exists()


def test_qdrant_payload_keeps_flowise_and_direct_query_fields(monkeypatch):
    captured = []

    class FakeClient:
        def get_collections(self):
            return None

        def collection_exists(self, name):
            return False

        def create_collection(self, **kwargs):
            return None

        def upsert(self, **kwargs):
            captured.extend(kwargs["points"])

    monkeypatch.setattr(ingest, "QdrantClient", lambda **kwargs: FakeClient())
    monkeypatch.setattr(
        ingest,
        "embed",
        lambda texts: [[0.1] * ingest.EMBEDDING_DIMENSION for _ in texts],
    )
    item = {
        "id": "00000000-0000-0000-0000-000000000001",
        "text": "储能变流器",
        "metadata": {"source_file": "course.pdf", "chapter": "第3章", "page": 12},
    }

    ingest.upsert([item])

    payload = captured[0].payload
    assert payload["content"] == item["text"]
    assert payload["text"] == item["text"]
    assert payload["metadata"] == item["metadata"]
    assert payload["source_file"] == "course.pdf"
    assert payload["page"] == 12
