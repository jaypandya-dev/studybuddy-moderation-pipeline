
from typing import Callable

from app.images.image_moderation_service import moderate_image

class VideoAnalysisError(Exception):
    """Raised when video frame moderation cannot be completed."""


EDUCATIONAL_APPROVAL_THRESHOLD = 75.0


def analyze_video_frames(frame_result: dict,progress_callback: Callable[[dict], None] | None = None,) -> dict:    
    """
    Moderate extracted video frames using the existing image pipeline.

    Each frame goes through:
        SmolVLM2 -> OCR -> Qwen3 -> image decision

    Video-level rules:
        1. Any harmful frame -> REJECT.
        2. Any failed frame, without a harmful frame -> REVIEW.
        3. At least 75% educational frames -> APPROVE.
        4. Otherwise -> REVIEW.
    """

    frames = frame_result.get("frames", [])

    if not frames:
        raise VideoAnalysisError(
            "No frames were provided for moderation."
        )

    frame_results = []
    
    total_frames = len(frames)

    def report_progress(completed: int, frame_result: dict) -> None:
        if progress_callback is not None:
            progress_callback({
                "completed": completed,
                "total": total_frames,
                "percentage": round(
                    completed / total_frames * 100
                ),
                "timestamp": frame_result.get(
                    "timestamp_text", "Unknown"
                ),
                "status": frame_result.get("status", "unknown"),
            })

    for frame in frames:
        timestamp = frame.get("timestamp_seconds")
        timestamp_text = frame.get("timestamp", "Unknown")
        image_path = frame.get("image_path")

        if not image_path:
            failed_result = {
                "timestamp_seconds": timestamp,
                "timestamp_text": timestamp_text,
                "status": "failed",
                "error": "Frame image path is missing.",
            }

            frame_results.append(failed_result)
            report_progress(len(frame_results), failed_result)
            continue

        try:
            result = moderate_image(image_path)

            successful_result = {
                "timestamp_seconds": timestamp,
                "timestamp_text": timestamp_text,
                "status": "success",
                **result,
            }

            frame_results.append(successful_result)
            report_progress(len(frame_results), successful_result)

        except Exception as exc:
            failed_result = {
                "timestamp_seconds": timestamp,
                "timestamp_text": timestamp_text,
                "status": "failed",
                "error": str(exc),
            }

            frame_results.append(failed_result)
            report_progress(len(frame_results), failed_result)

    successful_frames = [
        item for item in frame_results
        if item["status"] == "success"
    ]

    failed_frames = [
        item for item in frame_results
        if item["status"] == "failed"
    ]

    # Reject if any successfully analyzed frame is harmful.
    harmful_frames = [
        item for item in successful_frames
        if item["moderation"]["harmful"] is True
    ]
    review_frames = [
        item for item in successful_frames
        if (
            item.get("decision") == "REVIEW"
            or item["moderation"].get("needs_review") is True
        )
    ]

    # Count educational frames that are not harmful.
    educational_frames = [
        item for item in successful_frames
        if (
            item["moderation"]["educational"] is True
            and item["moderation"]["harmful"] is False
        )
    ]

    non_educational_frames = [
        item for item in successful_frames
        if (
            item["moderation"]["educational"] is False
            and item["moderation"]["harmful"] is False
        )
    ]

    total_frames = len(frames)
    educational_count = len(educational_frames)

    educational_percentage = (
        educational_count / total_frames * 100
    )

    # Apply video-level decision rules.
        # Apply video-level decision rules.
    if harmful_frames:
        decision = "REJECT"
    elif failed_frames or review_frames:
        decision = "REVIEW"
    elif educational_percentage >= EDUCATIONAL_APPROVAL_THRESHOLD:
        decision = "APPROVE"
    else:
        decision = "REJECT"

    status = "partial" if failed_frames else "success"

    return {
        "decision": decision,
        "status": status,
        "total_frames": total_frames,
        "successful_frames": len(successful_frames),
        "failed_frames": len(failed_frames),
        "educational_frames": educational_count,
        "non_educational_frames": len(non_educational_frames),
        "harmful_frames": len(harmful_frames),
        "educational_percentage": round(
            educational_percentage, 2
        ),
        "frame_results": frame_results,
    }
