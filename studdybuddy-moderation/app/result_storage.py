import json
from pathlib import Path


RESULTS_DIR = Path("moderation_results")
RESULTS_DIR.mkdir(exist_ok=True)


def save_moderation_result(job_id: str, result: dict) -> str:
    """
    Save the completed moderation result to disk.

    Only moderation results are persisted.
    The original uploaded PDF bytes are not stored here.
    """
    result_path = RESULTS_DIR / f"{job_id}.json"

    with result_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            result,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return str(result_path)


def load_moderation_result(job_id: str) -> dict | None:
    """
    Load a previously saved moderation result.
    """
    result_path = RESULTS_DIR / f"{job_id}.json"

    if not result_path.exists():
        return None

    with result_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)