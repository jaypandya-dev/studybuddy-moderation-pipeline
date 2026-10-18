from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_reprocess_endpoint(monkeypatch):
    def fake_reprocess(job_id):
        assert job_id == "test-job-123"

        return {
            "job_id": job_id,
            "previous_decision": "REJECT",
            "new_decision": "APPROVE",
            "reason": "sufficient_educational_coverage",
            "educational_chunks": 9,
            "non_educational_chunks": 3,
            "ignored_chunks": 2,
            "educational_coverage": 0.75,
        }

    monkeypatch.setattr(
        "app.main.reprocess_moderation_result",
        fake_reprocess,
    )

    response = client.post(
        "/moderate/test-job-123/reprocess"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["job_id"] == "test-job-123"
    assert data["previous_decision"] == "REJECT"
    assert data["new_decision"] == "APPROVE"
    assert data["reason"] == "sufficient_educational_coverage"
    assert data["educational_chunks"] == 9
    assert data["non_educational_chunks"] == 3
    assert data["ignored_chunks"] == 2
    assert data["educational_coverage"] == 0.75


def test_reprocess_endpoint_not_found(monkeypatch):
    def fake_reprocess(job_id):
        raise FileNotFoundError()

    monkeypatch.setattr(
        "app.main.reprocess_moderation_result",
        fake_reprocess,
    )

    response = client.post(
        "/moderate/non-existent-job/reprocess"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is False
    assert data["status"] == "NOT_FOUND"
    assert data["job_id"] == "non-existent-job"