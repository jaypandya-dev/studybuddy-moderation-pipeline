from unittest.mock import patch

from app.job_manager import ModerationJobManager


def test_job_manager_completes_successfully():
    manager = ModerationJobManager(
        max_workers=1
    )

    fake_result = {
        "decision": "APPROVE",
        "page_count": 10,
        "chunks": [
            {"page": 1},
            {"page": 2},
            {"page": 3},
        ],
    }

    with patch(
        "app.moderation_service.moderate_pdf",
        return_value=fake_result,
    ):
        job_id = manager.create_job(
            file_bytes=b"fake-pdf",
            filename="test.pdf",
        )

        manager.executor.shutdown(
            wait=True
        )

        job = manager.get_job(job_id)

    assert job is not None
    assert job["status"] == "COMPLETED"
    assert job["result"]["decision"] == "APPROVE"
    assert job["progress"]["processed_chunks"] == 3
    assert job["progress"]["total_chunks"] == 3
    assert job["progress"]["percentage"] == 100.0


def test_unknown_job_returns_none():
    manager = ModerationJobManager(
        max_workers=1
    )

    assert manager.get_job(
        "does-not-exist"
    ) is None

    manager.shutdown()


def test_progress_callback_updates_job():
    manager = ModerationJobManager(
        max_workers=1
    )

    def fake_moderation(
        file_bytes,
        progress_callback=None,
    ):
        progress_callback(1, 4)
        progress_callback(2, 4)
        progress_callback(3, 4)
        progress_callback(4, 4)

        return {
            "decision": "APPROVE",
            "page_count": 4,
            "chunks": [
                {"page": 1},
                {"page": 2},
                {"page": 3},
                {"page": 4},
            ],
        }

    with patch(
        "app.moderation_service.moderate_pdf",
        side_effect=fake_moderation,
    ):
        job_id = manager.create_job(
            file_bytes=b"fake-pdf",
            filename="progress.pdf",
        )

        manager.executor.shutdown(
            wait=True
        )

        job = manager.get_job(job_id)

    assert job["status"] == "COMPLETED"
    assert job["progress"]["processed_chunks"] == 4
    assert job["progress"]["total_chunks"] == 4
    assert job["progress"]["percentage"] == 100.0