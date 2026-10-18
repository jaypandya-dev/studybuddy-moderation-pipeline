import os
from dotenv import load_dotenv
load_dotenv()
import tempfile
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File
from app.pdf_extractor import extract_text
from app.file_validator import validate_file
from app.upload_moderation_service import validate_and_moderate_pdf
from app.job_manager import job_manager
from app.reprocess_result import reprocess_moderation_result
from app.images.image_moderation_service import moderate_image
from fastapi import HTTPException
from pydantic import BaseModel, HttpUrl
from concurrent.futures import ThreadPoolExecutor

from app.youtube.video_metadata import validate_youtube_url, VideoValidationError
from app.youtube.video_job_manager import video_job_manager
from app.youtube.video_job_worker import process_video_job


app = FastAPI(
    title="StudyBuddy Moderation Service",
    description="Independent content moderation service for StudyBuddy",
    version="1.0.0",
)
video_executor = ThreadPoolExecutor(
    max_workers=2,
    thread_name_prefix="video-moderation",
)


class VideoModerationRequest(BaseModel):
    url: HttpUrl

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "service": "StudyBuddy Moderation Service",
        "status": "running",
    }


@app.post("/validate")
async def validate(
    file: UploadFile = File(...),
):
    file_bytes = await file.read()

    validation = validate_file(
        file_bytes=file_bytes,
        filename=file.filename,
        uploaded_mime_type=file.content_type,
    )

    return {
        "filename": file.filename,
        "size_bytes": len(file_bytes),
        **validation,
    }


@app.post("/extract")
async def extract(
    file: UploadFile = File(...),
):
    file_bytes = await file.read()

    validation = validate_file(
        file_bytes=file_bytes,
        filename=file.filename,
        uploaded_mime_type=file.content_type,
    )

    if not validation["valid"]:
        return {
            "success": False,
            "validation": validation,
        }

    if validation["file_type"] != "pdf":
        return {
            "success": False,
            "reason": "Text extraction is currently supported only for PDFs",
        }

    extraction = extract_text(file_bytes)

    return {
        "success": True,
        "filename": file.filename,
        **extraction,
    }


@app.post("/moderate")
async def moderate(
    file: UploadFile = File(...),
):
    """
    Queue a moderation job and return immediately.
    """

    file_bytes = await file.read()

    validation = validate_file(
        file_bytes=file_bytes,
        filename=file.filename,
        uploaded_mime_type=file.content_type,
    )

    if not validation["valid"]:
        return {
            "success": False,
            "decision": "REJECT",
            "validation": validation,
        }

    if validation["file_type"] != "pdf":
        return {
            "success": False,
            "decision": "UNSUPPORTED",
            "validation": validation,
        }

    job_id = job_manager.create_job(
        file_bytes=file_bytes,
        filename=file.filename,
    )

    return {
        "success": True,
        "job_id": job_id,
        "status": "QUEUED",
        "filename": file.filename,
        "size_bytes": len(file_bytes),
    }


@app.get("/moderate/{job_id}")
async def get_moderation_job(
    job_id: str,
):
    job = job_manager.get_job(job_id)

    if job is None:
        return {
            "success": False,
            "status": "NOT_FOUND",
            "job_id": job_id,
        }

    return {
        "success": True,
        **job,
    }


@app.post("/moderate-sync")
async def moderate_sync(
    file: UploadFile = File(...),
):
    """
    Synchronous moderation endpoint kept for development/testing.

    Do not use this for large real-world PDFs.
    """

    file_bytes = await file.read()

    result = validate_and_moderate_pdf(
        file_bytes=file_bytes,
        filename=file.filename,
        uploaded_mime_type=file.content_type,
    )

    return {
        "filename": file.filename,
        "size_bytes": len(file_bytes),
        **result,
    }
    
@app.post("/moderate-image")
async def moderate_image_endpoint(
    file: UploadFile = File(...),
):
    """
    Synchronously moderate an uploaded image.

    Image pipeline:
    validation -> SmolVLM2 -> OCR -> image-specific Qwen3 -> decision
    """

    file_bytes = await file.read()

    validation = validate_file(
        file_bytes=file_bytes,
        filename=file.filename,
        uploaded_mime_type=file.content_type,
    )

    if not validation["valid"]:
        return {
            "success": False,
            "decision": "REJECT",
            "validation": validation,
        }

    if validation["file_type"] != "image":
        return {
            "success": False,
            "decision": "UNSUPPORTED",
            "validation": validation,
        }

    temp_path = None

    try:
        suffix = Path(file.filename).suffix.lower()

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temp_file:
            temp_file.write(file_bytes)
            temp_path = temp_file.name

        result = moderate_image(temp_path)

        return {
            "success": True,
            "filename": file.filename,
            "size_bytes": len(file_bytes),
            "decision": result["decision"],
            "validation": validation,
            "result": result,
        }

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
    
@app.post("/moderate/{job_id}/reprocess")
async def reprocess_job(job_id: str):
    try:
        result = reprocess_moderation_result(job_id)

        return {
            "success": True,
            **result,
        }

    except FileNotFoundError:
        return {
            "success": False,
            "status": "NOT_FOUND",
            "job_id": job_id,
        }
        
@app.post("/moderate-video")
async def moderate_video(request: VideoModerationRequest):
    """
    Queue a YouTube video moderation job.
    """

    try:
        video_url = validate_youtube_url(str(request.url))
    except VideoValidationError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    job_id = video_job_manager.create_job(video_url)

    video_executor.submit(
        process_video_job,
        job_id,
        video_url,
    )

    return {
        "success": True,
        "job_id": job_id,
        "status": "QUEUED",
        "message": "Video moderation job has been queued.",
    }
    
@app.post("/moderate-video/{job_id}/cancel")
async def cancel_video_moderation_job(job_id: str):
    cancelled = video_job_manager.cancel_job(job_id)

    if not cancelled:
        job = video_job_manager.get_job(job_id)

        if job is None:
            raise HTTPException(
                status_code=404,
                detail="Video moderation job not found.",
            )

        if job.get("status") == "CANCELLED":
            return {
                "success": True,
                "status": "CANCELLED",
                "job_id": job_id,
            }

        raise HTTPException(
            status_code=409,
            detail="The video job has already finished or cannot be cancelled.",
        )

    return {
        "success": True,
        "status": "CANCELLATION_REQUESTED",
        "job_id": job_id,
    }
    
@app.post("/moderate/{job_id}/cancel")
async def cancel_moderation_job(job_id: str):
    cancelled = job_manager.cancel_job(job_id)

    if not cancelled:
        job = job_manager.get_job(job_id)

        if job is None:
            raise HTTPException(
                status_code=404,
                detail="Moderation job not found.",
            )

        if job.get("status") == "CANCELLED":
            return {
                "success": True,
                "status": "CANCELLED",
                "job_id": job_id,
            }

        raise HTTPException(
            status_code=409,
            detail="The moderation job has already finished or cannot be cancelled.",
        )

    return {
        "success": True,
        "status": "CANCELLATION_REQUESTED",
        "job_id": job_id,
    }
    
@app.get("/moderate-video/{job_id}")
async def get_video_moderation_job(job_id: str):
    """
    Get video moderation progress or the final result.
    """

    job = video_job_manager.get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Video moderation job not found.",
        )

    return {
        "success": True,
        **job,
    }