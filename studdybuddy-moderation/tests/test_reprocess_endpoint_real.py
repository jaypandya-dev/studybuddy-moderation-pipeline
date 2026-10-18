from fastapi.testclient import TestClient

from app.main import app
from app.result_storage import save_moderation_result


client = TestClient(app)


def test_reprocess_endpoint_uses_saved_result(tmp_path, monkeypatch):
    # Use a temporary directory instead of the real
    # moderation_results folder.
    monkeypatch.setattr(
        "app.result_storage.RESULTS_DIR",
        tmp_path,
    )

    job_id = "real-reprocess-test"

    # Pretend this is the result produced by the expensive
    # chunk-level LLM moderation stage.
    saved_result = {
        "decision": "REJECT",
        "page_count": 4,
        "chunks": [
            {
                "page": 1,
                "chunk": 1,
                "page_role": "content",
                "moderation": {
                    "educational": True,
                    "harmful": False,
                    "category": "none",
                    "reason": "Educational content",
                    "decision": "APPROVE",
                },
            },
            {
                "page": 2,
                "chunk": 1,
                "page_role": "content",
                "moderation": {
                    "educational": True,
                    "harmful": False,
                    "category": "none",
                    "reason": "Educational content",
                    "decision": "APPROVE",
                },
            },
            {
                "page": 3,
                "chunk": 1,
                "page_role": "content",
                "moderation": {
                    "educational": True,
                    "harmful": False,
                    "category": "none",
                    "reason": "Educational content",
                    "decision": "APPROVE",
                },
            },
            {
                "page": 4,
                "chunk": 1,
                "page_role": "content",
                "moderation": {
                    "educational": False,
                    "harmful": False,
                    "category": "non_educational",
                    "reason": "Non-educational material",
                    "decision": "REJECT",
                },
            },
        ],
    }

    save_moderation_result(
        job_id=job_id,
        result=saved_result,
    )

    # Make sure this test does not accidentally call the LLM.
    def fail_if_llm_called(*args, **kwargs):
        raise AssertionError("LLM should not be called during reprocessing")

    monkeypatch.setattr(
        "app.llm_moderator.moderate_chunk",
        fail_if_llm_called,
    )

    monkeypatch.setattr(
        "app.llm_moderator.scan_chunk_risk",
        fail_if_llm_called,
    )

    response = client.post(
        f"/moderate/{job_id}/reprocess"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["job_id"] == job_id

    # The old decision was REJECT, but the new resource-level
    # policy allows it because educational coverage is 75%.
    assert data["previous_decision"] == "REJECT"
    assert data["new_decision"] == "APPROVE"

    assert data["reason"] == "sufficient_educational_coverage"
    assert data["educational_chunks"] == 3
    assert data["non_educational_chunks"] == 1
    assert data["ignored_chunks"] == 0
    assert data["educational_coverage"] == 0.75