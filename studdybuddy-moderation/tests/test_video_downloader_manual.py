
from app.youtube.video_downloader import (
    download_youtube_video,
    cleanup_video_download,
)


def main():
    url = input("Enter a public YouTube video URL: ").strip()

    result = None

    try:
        result = download_youtube_video(url)

        print("\nDownload successful!")
        print("Video path:", result["video_path"])
        print("Size:", result["actual_size_mb"], "MB")
        print("Maximum height:", result["max_video_height"], "p")

        input("\nPress Enter to delete the temporary video...")

    except Exception as exc:
        print("\nDownload failed:")
        print(exc)

    finally:
        if result is not None:
            cleanup_video_download(result)
            print("Temporary files cleaned up.")


if __name__ == "__main__":
    main()
