
from app.youtube.video_downloader import (
    download_youtube_video,
    cleanup_video_download,
)
from app.youtube.frame_extractor import (
    extract_video_frames,
    cleanup_extracted_frames,
)


def main():
    url = input("Enter a public YouTube video URL: ").strip()

    download_result = None
    frame_result = None

    try:
        print("\nDownloading video...")
        download_result = download_youtube_video(url)

        print("\nExtracting frames...")
        frame_result = extract_video_frames(
            download_result["video_path"]
        )

        print("\nFrame extraction successful!")
        print("Duration:", frame_result["duration_seconds"], "seconds")
        print(
            "Original resolution:",
            f'{frame_result["original_width"]}x'
            f'{frame_result["original_height"]}',
        )
        print("Frames extracted:", frame_result["sampled_frame_count"])
        print("Frames directory:", frame_result["frames_dir"])

        for frame in frame_result["frames"]:
            print(
                f'Frame {frame["frame_number"]}: '
                f'{frame["timestamp"]} | '
                f'{frame["size_bytes"]} bytes | '
                f'{frame["image_path"]}'
            )

        input("\nPress Enter to clean up temporary files...")

    except Exception as exc:
        print("\nTest failed:")
        print(type(exc).__name__ + ":", exc)

    finally:
        if frame_result is not None:
            cleanup_extracted_frames(frame_result)

        if download_result is not None:
            cleanup_video_download(download_result)

        print("\nCleanup completed.")


if __name__ == "__main__":
    main()
