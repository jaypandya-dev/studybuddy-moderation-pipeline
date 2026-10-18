
import threading
import uuid


class VideoJobManager:
    def __init__(self):
        self.jobs = {}
        self.cancellation_events = {}
        self.lock = threading.Lock()

    def create_job(self, video_url: str) -> str:
        job_id = str(uuid.uuid4())
        cancellation_event = threading.Event()

        with self.lock:
            self.jobs[job_id] = {
                "job_id": job_id,
                "status": "QUEUED",
                "stage": "Queued",
                "progress": {
                    "completed": 0,
                    "total": 20,
                    "percentage": 0,
                },
                "result": None,
                "error": None,
                "video_url": video_url,
            }
            self.cancellation_events[job_id] = cancellation_event

        return job_id

    def cancel_job(self, job_id: str) -> bool:
        """Request cancellation for a queued or running video job."""
        with self.lock:
            job = self.jobs.get(job_id)
            cancellation_event = self.cancellation_events.get(job_id)

            if job is None or cancellation_event is None:
                return False

            if job["status"] in ("COMPLETED", "FAILED", "CANCELLED"):
                return False

            cancellation_event.set()

            if job["status"] == "QUEUED":
                job["status"] = "CANCELLED"
                job["stage"] = "Cancelled"
                job["result"] = None
                job["error"] = None

            return True

    def is_cancelled(self, job_id: str) -> bool:
        with self.lock:
            event = self.cancellation_events.get(job_id)
            return event.is_set() if event else True

    def update_job(self, job_id: str, **updates):
        with self.lock:
            job = self.jobs.get(job_id)

            if job is None:
                return

            # A completed cancellation must not be overwritten by the worker.
            if (
                job["status"] == "CANCELLED"
                and updates.get("status") != "CANCELLED"
            ):
                return

            job.update(updates)

            if updates.get("status") == "CANCELLED":
                job["stage"] = "Cancelled"
                job["result"] = None
                job["error"] = None

    def update_progress(self, job_id: str, progress: dict):
        with self.lock:
            job = self.jobs.get(job_id)

            if job is None or job["status"] in (
                "CANCELLED",
                "COMPLETED",
                "FAILED",
            ):
                return

            job["progress"] = dict(progress)
            job["stage"] = (
                f'Analyzing frame {progress["completed"]}/'
                f'{progress["total"]}'
            )

    def get_job(self, job_id: str):
        with self.lock:
            job = self.jobs.get(job_id)

            if job is None:
                return None

            return {
                **job,
                "progress": dict(job["progress"]),
            }


video_job_manager = VideoJobManager()
