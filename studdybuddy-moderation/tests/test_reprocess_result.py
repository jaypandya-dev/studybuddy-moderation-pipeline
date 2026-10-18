from app.reprocess_result import reprocess_moderation_result


def test_reprocess_saved_result(monkeypatch):
    saved_result = {
        "decision": "REJECT",
        "chunks": [
            {
                "page": 1,
                "chunk": 1,
                "page_role": "content",
                "moderation": {
                    "educational": True,
                    "harmful": False,
                    "category": "none",
                    "reason": "test",
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
                    "reason": "test",
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
                    "reason": "test",
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
                    "reason": "test",
                    "decision": "REJECT",
                },
            },
        ],
    }

    def fake_load(job_id):
        assert job_id == "test-job"
        return saved_result

    monkeypatch.setattr(
        "app.reprocess_result.load_moderation_result",
        fake_load,
    )

    result = reprocess_moderation_result("test-job")

    assert result["previous_decision"] == "REJECT"
    assert result["new_decision"] == "APPROVE"
    assert result["educational_chunks"] == 3
    assert result["non_educational_chunks"] == 1
    assert result["ignored_chunks"] == 0
    assert result["educational_coverage"] == 0.75