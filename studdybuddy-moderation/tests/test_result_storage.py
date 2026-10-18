from app.result_storage import (
    save_moderation_result,
    load_moderation_result,
)


def test_save_and_load_moderation_result(tmp_path, monkeypatch):
    # Use a temporary directory so the real moderation_results
    # folder is not affected by the test.
    monkeypatch.setattr(
        "app.result_storage.RESULTS_DIR",
        tmp_path,
    )

    job_id = "test-job-123"

    result = {
        "decision": "APPROVE",
        "page_count": 2,
        "chunks": [
            {
                "page": 1,
                "chunk": 1,
                "moderation": {
                    "educational": True,
                    "harmful": False,
                    "category": "none",
                    "decision": "APPROVE",
                },
            }
        ],
    }

    path = save_moderation_result(
        job_id=job_id,
        result=result,
    )

    loaded = load_moderation_result(job_id)

    assert loaded == result
    assert path.endswith("test-job-123.json")