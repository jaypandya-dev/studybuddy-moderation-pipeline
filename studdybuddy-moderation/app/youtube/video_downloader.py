import os
import shutil
import tempfile
from pathlib import Path
import uuid
from pathlib import Path
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from app.youtube.video_metadata import (
    MAX_VIDEO_SIZE_BYTES,
    MAX_VIDEO_HEIGHT,
    inspect_youtube_video,
    VideoValidationError,
)


def download_youtube_video(url: str) -> dict:
    """
    Validate and download a YouTube video into a temporary directory.

    Limits:
    - Maximum duration: 15 minutes (validated by metadata service)
    - Maximum download size: 500 MB
    - Maximum video height: 720p

    The caller must call cleanup_video_download() after processing.
    """

    # Always validate before downloading.
    metadata = inspect_youtube_video(url)

    project_root = Path(__file__).resolve().parents[2]

    temp_root = project_root / "temp" / "youtube"
    temp_root.mkdir(parents=True, exist_ok=True)
    temp_dir = str(temp_root / uuid.uuid4().hex)
    Path(temp_dir).mkdir(parents=True, exist_ok=False)
    output_template = os.path.join(temp_dir, "video.%(ext)s")

    # Track the largest observed download size for each stream.
    # This helps account for separate video and audio downloads.
    stream_sizes = {}

    def enforce_download_limit(progress):
        if progress.get("status") != "downloading":
            return

        info = progress.get("info_dict") or {}
        format_id = str(info.get("format_id") or "unknown")
        downloaded = progress.get("downloaded_bytes") or 0

        stream_sizes[format_id] = max(
            stream_sizes.get(format_id, 0),
            downloaded,
        )

        total_downloaded = sum(stream_sizes.values())

        if total_downloaded > MAX_VIDEO_SIZE_BYTES:
            raise DownloadError(
                "Video download exceeded the 500 MB limit."
            )

    options = {
        "format": (
            f"bestvideo[height<={MAX_VIDEO_HEIGHT}]"
            "+bestaudio/"
            f"best[height<={MAX_VIDEO_HEIGHT}]"
        ),
        "outtmpl": output_template,
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": 20,
        "retries": 2,
        "fragment_retries": 2,
        "max_filesize": MAX_VIDEO_SIZE_BYTES,
        "progress_hooks": [enforce_download_limit],
        "overwrites": True,
    }

    try:
        with YoutubeDL(options) as ydl:
            ydl.extract_info(url, download=True)

        # Find the completed video file.
        video_files = [
            path for path in Path(temp_dir).iterdir()
            if path.is_file()
            and path.suffix.lower() in {
                ".mp4", ".mkv", ".webm", ".mov"
            }
            and not path.name.endswith(".part")
        ]

        if len(video_files) != 1:
            raise VideoValidationError(
                "The downloaded video file could not be identified."
            )

        video_path = video_files[0]
        actual_size = video_path.stat().st_size

        # Check the final merged file as well.
        if actual_size > MAX_VIDEO_SIZE_BYTES:
            raise VideoValidationError(
                "The downloaded video exceeds the 500 MB limit."
            )

        return {
            "success": True,
            "video_path": str(video_path),
            "temp_dir": temp_dir,
            "actual_size_bytes": actual_size,
            "actual_size_mb": round(
                actual_size / (1024 * 1024), 2
            ),
            "max_video_height": MAX_VIDEO_HEIGHT,
            "metadata": metadata,
        }

    except Exception as exc:
        # Remove partial downloads if anything fails.
        shutil.rmtree(temp_dir, ignore_errors=True)

        if isinstance(exc, VideoValidationError):
            raise

        raise VideoValidationError(
            "The video could not be downloaded within the "
            "configured limits. It may be unavailable, too large, "
            "or temporarily inaccessible."
        ) from exc


def cleanup_video_download(download_result: dict) -> None:
    """Remove temporary video files after processing."""

    temp_dir = download_result.get("temp_dir")

    if temp_dir:
        shutil.rmtree(temp_dir, ignore_errors=True)
