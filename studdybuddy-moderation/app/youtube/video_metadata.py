
import math
from urllib.parse import urlparse

from yt_dlp import YoutubeDL


# -----------------------------
# Video processing limits
# -----------------------------

MAX_VIDEO_DURATION_SECONDS = 15 * 60
MAX_VIDEO_SIZE_BYTES = 500 * 1024 * 1024  # 500 MB
MAX_VIDEO_HEIGHT = 720
MAX_SAMPLED_FRAMES = 20

# -----------------------------
# Supported YouTube hosts
# -----------------------------

ALLOWED_YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "music.youtube.com",
    "youtu.be",
}


class VideoValidationError(ValueError):
    """Raised when a video cannot pass preflight validation."""


def validate_youtube_url(url: str) -> str:
    """
    Validate that the input is an HTTP(S) URL on an
    explicitly supported YouTube host.
    """

    if not isinstance(url, str) or not url.strip():
        raise VideoValidationError("A YouTube URL is required.")

    url = url.strip()
    parsed = urlparse(url)

    if parsed.scheme not in {"http", "https"}:
        raise VideoValidationError(
            "The URL must use HTTP or HTTPS."
        )

    host = (parsed.hostname or "").lower()

    if host not in ALLOWED_YOUTUBE_HOSTS:
        raise VideoValidationError(
            "Only supported YouTube video URLs are allowed."
        )

    if parsed.username or parsed.password:
        raise VideoValidationError(
            "URLs containing embedded credentials are not allowed."
        )

    if not parsed.path or parsed.path == "/":
        raise VideoValidationError(
            "The URL does not identify a video."
        )

    return url


def _format_size_bytes(fmt: dict) -> int | None:
    """Return a known or approximate format size in bytes."""

    size = fmt.get("filesize")

    if size is None:
        size = fmt.get("filesize_approx")

    if size is None:
        return None

    try:
        size = int(size)
    except (TypeError, ValueError, OverflowError):
        return None

    return size if size > 0 else None


def _estimate_download_size(info: dict) -> int | None:
    """
    Estimate the size of the best available video stream
    at or below the configured height, plus its audio stream.

    Return None if the metadata does not provide a reliable
    estimate. The actual download will still need a hard cap.
    """

    formats = info.get("formats", [])

    video_only = [
        fmt for fmt in formats
        if fmt.get("vcodec") not in (None, "none")
        and fmt.get("acodec") in (None, "none")
        and fmt.get("height") is not None
        and fmt["height"] <= MAX_VIDEO_HEIGHT
    ]

    audio_only = [
        fmt for fmt in formats
        if fmt.get("vcodec") == "none"
        and fmt.get("acodec") not in (None, "none")
    ]

    # Prefer separate video and audio streams when available.
    if video_only and audio_only:
        best_video = max(
            video_only,
            key=lambda fmt: (
                fmt.get("height") or 0,
                fmt.get("fps") or 0,
                fmt.get("tbr") or 0,
            ),
        )

        best_audio = max(
            audio_only,
            key=lambda fmt: (
                fmt.get("abr") or 0,
                fmt.get("tbr") or 0,
            ),
        )

        video_size = _format_size_bytes(best_video)
        audio_size = _format_size_bytes(best_audio)

        if video_size is not None and audio_size is not None:
            return video_size + audio_size

        # The preferred stream sizes are unknown.
        # Do not pretend we have a reliable estimate.
        return None

    # Otherwise, look for a combined audio/video stream
    # that does not exceed the configured height.
    combined_formats = [
        fmt for fmt in formats
        if fmt.get("vcodec") not in (None, "none")
        and fmt.get("acodec") not in (None, "none")
        and fmt.get("height") is not None
        and fmt["height"] <= MAX_VIDEO_HEIGHT
    ]

    if not combined_formats:
        return None

    best_combined = max(
        combined_formats,
        key=lambda fmt: (
            fmt.get("height") or 0,
            fmt.get("fps") or 0,
            fmt.get("tbr") or 0,
        ),
    )

    return _format_size_bytes(best_combined)


def inspect_youtube_video(url: str) -> dict:
    """
    Validate a YouTube video and retrieve metadata without
    downloading the video or calling an AI model.
    """

    url = validate_youtube_url(url)

    ydl_options = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "noplaylist": True,
        "socket_timeout": 20,
        "retries": 1,
    }

    try:
        with YoutubeDL(ydl_options) as ydl:
            info = ydl.extract_info(url, download=False)

    except Exception as exc:
        raise VideoValidationError(
            "Could not retrieve video metadata. "
            "Check that the video is accessible and try again."
        ) from exc

    if not isinstance(info, dict):
        raise VideoValidationError(
            "YouTube did not return valid video metadata."
        )

    if info.get("_type") == "playlist" or info.get("entries"):
        raise VideoValidationError(
            "Playlist URLs are not supported. Provide one video URL."
        )

    # Live and upcoming streams are not supported.
    live_status = info.get("live_status")

    if info.get("is_live") or live_status in {
        "is_live",
        "is_upcoming",
    }:
        raise VideoValidationError(
            "Live and upcoming streams are not supported."
        )

    # Reject videos with missing or unverifiable duration.
    duration = info.get("duration")

    if duration is None:
        raise VideoValidationError(
            "The video duration could not be verified."
        )

    try:
        duration = float(duration)
    except (TypeError, ValueError, OverflowError):
        raise VideoValidationError(
            "The video duration is invalid."
        ) from None

    if not math.isfinite(duration) or duration <= 0:
        raise VideoValidationError(
            "The video must have a valid, finite duration."
        )

    if duration > MAX_VIDEO_DURATION_SECONDS:
        raise VideoValidationError(
            "Videos longer than 15 minutes are not allowed."
        )

    # Estimate size using the available format metadata.
    estimated_size = _estimate_download_size(info)

    if (
        estimated_size is not None
        and estimated_size > MAX_VIDEO_SIZE_BYTES
    ):
        raise VideoValidationError(
            "The estimated video download exceeds the 500 MB limit."
        )

    return {
        "valid": True,
        "video_id": info.get("id"),
        "title": info.get("title"),
        "description": (info.get("description") or "")[:5000],
        "channel": info.get("channel") or info.get("uploader"),
        "video_url": info.get("webpage_url") or url,
        "duration_seconds": duration,
        "duration_limit_seconds": MAX_VIDEO_DURATION_SECONDS,
        "estimated_size_bytes": estimated_size,
        "estimated_size_mb": (
            round(estimated_size / (1024 * 1024), 2)
            if estimated_size is not None
            else None
        ),
        "max_file_size_bytes": MAX_VIDEO_SIZE_BYTES,
        "max_video_height": MAX_VIDEO_HEIGHT,
        "max_sampled_frames": MAX_SAMPLED_FRAMES,
        "requires_download_size_cap": True,
    }
