
from dotenv import load_dotenv

load_dotenv(override=True)

from app.youtube.video_downloader import (
    download_youtube_video,
    cleanup_video_download,
)
from app.youtube.frame_extractor import (
    extract_video_frames,
    cleanup_extracted_frames,
)
from app.youtube.video_analyzer import analyze_video_frames


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

        print(
            "\nModerating all extracted frames "
            "using the existing image pipeline..."
        )

        analysis = analyze_video_frames(frame_result)

        print("\n" + "=" * 60)
        print("VIDEO MODERATION RESULTS")
        print("=" * 60)

        print("Video decision:", analysis["decision"])
        print("Analysis status:", analysis["status"])
        print("Total frames:", analysis["total_frames"])
        print("Successful frames:", analysis["successful_frames"])
        print("Failed frames:", analysis["failed_frames"])
        print("Educational frames:", analysis["educational_frames"])
        print(
            "Non-educational frames:",
            analysis["non_educational_frames"],
        )
        print("Harmful frames:", analysis["harmful_frames"])
        print(
            "Educational percentage:",
            f"{analysis['educational_percentage']}%",
        )

        for frame in analysis["frame_results"]:
            print("\n" + "-" * 60)
            print("Frame timestamp:", frame["timestamp_text"])
            print("Frame status:", frame["status"])

            if frame["status"] == "failed":
                print("Error:", frame.get("error", "Unknown error"))
                continue

            moderation = frame["moderation"]

            print("Frame decision:", frame["decision"])
            print("Visual description:")
            print(frame["description"] or "(No description returned)")

            print("\nOCR text:")
            print(frame["ocr_text"] or "(No text detected)")

            print("\nModeration details:")
            print("Educational:", moderation["educational"])
            print("Harmful:", moderation["harmful"])
            print("Category:", moderation["category"])
            print("Reason:", moderation["reason"])

        print("\n" + "=" * 60)
        print("FINAL VIDEO DECISION:", analysis["decision"])
        print("=" * 60)

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
