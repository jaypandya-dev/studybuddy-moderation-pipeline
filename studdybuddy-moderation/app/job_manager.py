
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from threading import Event, Lock
from uuid import uuid4

from app.result_storage import save_moderation_result


class ModerationJobManager:
    def __init__(self, max_workers: int = 1):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.jobs = {}
        self.cancellation_events = {}
        self.lock = Lock()

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(timezone.utc).isoformat()

    def create_job(
        self,
        file_bytes: bytes,
        filename: str | None = None,
    ) -> str:
        job_id = str(uuid4())
        cancellation_event = Event()

        job = {
            "job_id": job_id,
            "status": "QUEUED",
            "filename": filename,
            "created_at": self._timestamp(),
            "started_at": None,
            "completed_at": None,
            "progress": {
                "processed_chunks": 0,
                "total_chunks": None,
                "percentage": 0.0,
            },
            "result": None,
            "result_path": None,
            "error": None,
        }

        with self.lock:
            self.jobs[job_id] = job
            self.cancellation_events[job_id] = cancellation_event

        self.executor.submit(
            self._run_job,
            job_id,
            file_bytes,
        )

        return job_id

    def cancel_job(self, job_id: str) -> bool:
        """Request cancellation of a queued or running PDF job."""
        with self.lock:
            job = self.jobs.get(job_id)
            event = self.cancellation_events.get(job_id)

            if job is None or event is None:
                return False

            if job["status"] in ("COMPLETED", "FAILED", "CANCELLED"):
                return False

            event.set()

            if job["status"] == "QUEUED":
                job["status"] = "CANCELLED"
                job["completed_at"] = self._timestamp()

            return True

    def is_cancelled(self, job_id: str) -> bool:
        with self.lock:
            event = self.cancellation_events.get(job_id)
            return event.is_set() if event else True

    def _mark_cancelled(
        self,
        job_id: str,
        result_path=None,
    ) -> None:
        if result_path:
            try:
                Path(result_path).unlink(missing_ok=True)
            except OSError as exc:
                print(
                    f"[Moderation] Could not remove cancelled result "
                    f"{result_path}: {exc}"
                )

        self._update_job(
            job_id,
            status="CANCELLED",
            completed_at=self._timestamp(),
            result=None,
            result_path=None,
            error=None,
        )

    def _run_job(
        self,
        job_id: str,
        file_bytes: bytes,
    ):
        if self.is_cancelled(job_id):
            return

        self._update_job(
            job_id,
            status="PROCESSING",
            started_at=self._timestamp(),
        )

        result_path = None

        try:
            from app.moderation_service import moderate_pdf

            def update_progress(
                processed_chunks: int,
                total_chunks: int,
            ):
                if self.is_cancelled(job_id):
                    return

                percentage = (
                    processed_chunks / total_chunks * 100
                    if total_chunks
                    else 0.0
                )

                self._update_job(
                    job_id,
                    progress={
                        "processed_chunks": processed_chunks,
                        "total_chunks": total_chunks,
                        "percentage": round(percentage, 2),
                    },
                )

            result = moderate_pdf(
                file_bytes,
                progress_callback=update_progress,
                cancellation_check=lambda: self.is_cancelled(job_id),
            )

            if self.is_cancelled(job_id):
                self._mark_cancelled(job_id)
                return

            result_path = save_moderation_result(
                job_id=job_id,
                result=result,
            )

            if self.is_cancelled(job_id):
                self._mark_cancelled(job_id, result_path)
                return

            total_chunks = len(result.get("chunks", []))

            # Make the final cancellation check and completion update atomic.
            with self.lock:
                job = self.jobs.get(job_id)
                event = self.cancellation_events.get(job_id)

                if (
                    job is None
                    or event is None
                    or event.is_set()
                    or job["status"] == "CANCELLED"
                ):
                    cancelled = True
                else:
                    cancelled = False
                    job.update(
                        status="COMPLETED",
                        completed_at=self._timestamp(),
                        progress={
                            "processed_chunks": total_chunks,
                            "total_chunks": total_chunks,
                            "percentage": 100.0,
                        },
                        result=result,
                        result_path=result_path,
                        error=None,
                    )

            if cancelled:
                self._mark_cancelled(job_id, result_path)

        except Exception as exc:
            if self.is_cancelled(job_id):
                self._mark_cancelled(job_id, result_path)
            else:
                self._update_job(
                    job_id,
                    status="FAILED",
                    completed_at=self._timestamp(),
                    error=str(exc),
                )

    def _update_job(
        self,
        job_id: str,
        **updates,
    ):
        with self.lock:
            if job_id not in self.jobs:
                return

            if (
                self.jobs[job_id]["status"] == "CANCELLED"
                and updates.get("status") != "CANCELLED"
            ):
                return

            self.jobs[job_id].update(updates)

    def get_job(
        self,
        job_id: str,
    ) -> dict | None:
        with self.lock:
            job = self.jobs.get(job_id)

            if job is None:
                return None

            return {
                **job,
                "progress": dict(job["progress"]),
            }

    def shutdown(self):
        self.executor.shutdown(
            wait=False,
            cancel_futures=True,
        )


job_manager = ModerationJobManager(max_workers=1)
