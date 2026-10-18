
import json
import math
import shutil
import subprocess
from pathlib import Path


# -----------------------------
# Frame extraction limits
# -----------------------------

MAX_SAMPLED_FRAMES = 20
MAX_FRAME_DIMENSION = 768
FFPROBE_TIMEOUT_SECONDS = 20
FFMPEG_TIMEOUT_SECONDS = 60


class FrameExtractionError(RuntimeError):
    """Raised when video inspection or frame extraction fails."""


def _run_command(command: list[str], timeout: int) -> str:
    """Run FFmpeg/FFprobe safely and return standard output."""

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )

    except FileNotFoundError as exc:
        raise FrameExtractionError(
            "FFmpeg or FFprobe was not found. Check your Windows PATH."
        ) from exc

    except subprocess.TimeoutExpired as exc:
        raise FrameExtractionError(
            "Video processing timed out."
        ) from exc

    if result.returncode != 0:
        raise FrameExtractionError(
            "Video processing failed: "
            + (result.stderr or "Unknown FFmpeg error")[-1500:]
        )

    return result.stdout


def inspect_video(video_path: str | Path) -> dict:
    """Inspect video duration and resolution using FFprobe."""

    path = Path(video_path).resolve()

    if not path.is_file():
        raise FrameExtractionError(
            "The downloaded video file does not exist."
        )

    command = [
        "ffprobe",
        "-v", "error",
        "-show_entries",
        "format=duration:stream=codec_type,width,height",
        "-of", "json",
        str(path),
    ]

    output = _run_command(
        command,
        timeout=FFPROBE_TIMEOUT_SECONDS,
    )

    try:
        data = json.loads(output)
    except json.JSONDecodeError as exc:
        raise FrameExtractionError(
            "FFprobe returned invalid video information."
        ) from exc

    video_streams = [
        stream
        for stream in data.get("streams", [])
        if stream.get("codec_type") == "video"
    ]

    if not video_streams:
        raise FrameExtractionError(
            "The downloaded file does not contain a video stream."
        )

    try:
        duration = float(data["format"]["duration"])
        width = int(video_streams[0]["width"])
        height = int(video_streams[0]["height"])
    except (KeyError, TypeError, ValueError, OverflowError):
        raise FrameExtractionError(
            "Could not determine video duration or resolution."
        ) from None

    if (
        not math.isfinite(duration)
        or duration <= 0
        or width <= 0
        or height <= 0
    ):
        raise FrameExtractionError(
            "The video has invalid duration or resolution."
        )

    return {
        "video_path": str(path),
        "duration_seconds": duration,
        "width": width,
        "height": height,
    }


def extract_video_frames(
    video_path: str | Path,
    max_frames: int = MAX_SAMPLED_FRAMES,
) -> dict:
    """
    Extract representative frames at evenly spaced timestamps.

    Frames are saved in a 'frames' directory beside the video.
    The returned timestamps are in seconds from the beginning.
    """

    if (
        isinstance(max_frames, bool)
        or not isinstance(max_frames, int)
        or not 1 <= max_frames <= MAX_SAMPLED_FRAMES
    ):
        raise FrameExtractionError(
            f"max_frames must be between 1 and {MAX_SAMPLED_FRAMES}."
        )

    video_info = inspect_video(video_path)
    duration = video_info["duration_seconds"]

    video_path = Path(video_info["video_path"])
    frames_dir = video_path.parent / "frames"

    # Avoid accidentally mixing frames from separate runs.
    if frames_dir.exists():
        shutil.rmtree(frames_dir)

    frames_dir.mkdir(parents=True, exist_ok=True)

    # Divide the video into equal segments and sample each
    # segment's midpoint, avoiding the exact start and end.
    frame_count = max_frames

    timestamps = [
        duration * (index + 0.5) / frame_count
        for index in range(frame_count)
    ]

    extracted_frames = []

    try:
        for index, timestamp in enumerate(timestamps, start=1):
            frame_path = frames_dir / f"frame_{index:02d}.jpg"

            command = [
                "ffmpeg",
                "-hide_banner",
                "-loglevel", "error",
                "-nostdin",
                "-y",
                "-ss", f"{timestamp:.3f}",
                "-i", str(video_path),
                "-map", "0:v:0",
                "-frames:v", "1",
                "-vf",
                (
                    f"scale=w='min({MAX_FRAME_DIMENSION},iw)':"
                    f"h='min({MAX_FRAME_DIMENSION},ih)':"
                    "force_original_aspect_ratio=decrease"
                ),
                "-q:v", "3",
                str(frame_path),
            ]

            _run_command(
                command,
                timeout=FFMPEG_TIMEOUT_SECONDS,
            )

            if not frame_path.is_file() or frame_path.stat().st_size == 0:
                raise FrameExtractionError(
                    f"FFmpeg did not produce frame {index}."
                )

            extracted_frames.append({
                "frame_number": index,
                "timestamp_seconds": round(timestamp, 3),
                "timestamp": (
                    f"{int(timestamp // 60):02d}:"
                    f"{timestamp % 60:05.2f}"
                ),
                "image_path": str(frame_path),
                "size_bytes": frame_path.stat().st_size,
            })

        return {
            "success": True,
            "video_path": str(video_path),
            "duration_seconds": duration,
            "original_width": video_info["width"],
            "original_height": video_info["height"],
            "sampled_frame_count": len(extracted_frames),
            "max_sampled_frames": MAX_SAMPLED_FRAMES,
            "max_frame_dimension": MAX_FRAME_DIMENSION,
            "frames_dir": str(frames_dir),
            "frames": extracted_frames,
        }

    except Exception:
        # Never leave a partial frame set after a failure.
        shutil.rmtree(frames_dir, ignore_errors=True)
        raise


def cleanup_extracted_frames(frame_result: dict) -> None:
    """Delete extracted frames after moderation finishes."""

    frames_dir = frame_result.get("frames_dir")

    if frames_dir:
        shutil.rmtree(frames_dir, ignore_errors=True)
