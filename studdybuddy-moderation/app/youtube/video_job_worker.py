
from app.youtube.video_job_manager import video_job_manager
from app.youtube.video_metadata import (
    inspect_youtube_video,
    VideoValidationError,
)
from app.youtube.video_downloader import (
    download_youtube_video,
    cleanup_video_download,
)
from app.youtube.frame_extractor import (
    extract_video_frames,
    cleanup_extracted_frames,
)
from app.youtube.video_analyzer import analyze_video_frames


class VideoModerationCancelled(Exception):
    """Raised when video moderation is cancelled."""


def process_video_job(job_id: str, video_url: str) -> None:
    download_result = None
    frame_result = None

    def check_cancelled() -> None:
        if video_job_manager.is_cancelled(job_id):
            raise VideoModerationCancelled("MODERATION_CANCELLED")

    try:
        check_cancelled()

        video_job_manager.update_job(
            job_id,
            status="PROCESSING",
            stage="Validating YouTube video",
        )

        # Step 1: Validate URL and inspect metadata.
        check_cancelled()
        metadata = inspect_youtube_video(video_url)
        check_cancelled()

        video_job_manager.update_job(
            job_id,
            stage="Downloading video",
            metadata=metadata,
        )

        # Step 2: Download the video.
        check_cancelled()
        download_result = download_youtube_video(video_url)
        check_cancelled()

        video_job_manager.update_job(
            job_id,
            stage="Extracting frames",
        )

        # Step 3: Extract representative frames.
        check_cancelled()
        frame_result = extract_video_frames(
            download_result["video_path"]
        )
        check_cancelled()

        total_frames = len(frame_result["frames"])

        video_job_manager.update_job(
            job_id,
            stage="Starting frame moderation",
            progress={
                "completed": 0,
                "total": total_frames,
                "percentage": 0,
            },
        )

        # Step 4: Moderate frames and report progress.
        def on_progress(progress: dict) -> None:
            check_cancelled()
            video_job_manager.update_progress(job_id, progress)

        check_cancelled()
        result = analyze_video_frames(
            frame_result,
            progress_callback=on_progress,
        )
        check_cancelled()

        
        # Step 5: Store the final result only if not cancelled.
        check_cancelled()

        video_job_manager.update_job(
            job_id,
            status="COMPLETED",
            stage="Moderation completed",
            progress={
                "completed": total_frames,
                "total": total_frames,
                "percentage": 100,
            },
            result=result,
            error=None,
        )


    except VideoModerationCancelled:
        video_job_manager.update_job(
            job_id,
            status="CANCELLED",
            stage="Cancelled",
            result=None,
            error=None,
        )

    except Exception as exc:
        if video_job_manager.is_cancelled(job_id):
            video_job_manager.update_job(
                job_id,
                status="CANCELLED",
                stage="Cancelled",
                result=None,
                error=None,
            )
        else:
            video_job_manager.update_job(
                job_id,
                status="FAILED",
                stage="Moderation failed",
                error=str(exc),
            )

    finally:
        # Clean up extracted frames before deleting the video folder.
        if frame_result:
            cleanup_extracted_frames(frame_result)

        if download_result:
            cleanup_video_download(download_result)
