
from app.youtube.video_metadata import (
    inspect_youtube_video,
    VideoValidationError,
)


def main():
    url = input("Enter a public YouTube video URL: ").strip()

    try:
        result = inspect_youtube_video(url)

        print("\nPreflight succeeded:")
        for key, value in result.items():
            print(f"{key}: {value}")

    except VideoValidationError as exc:
        print("\nPreflight rejected the video:")
        print(exc)


if __name__ == "__main__":
    main()
