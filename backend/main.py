"""
Biomechanics Analysis API
FastAPI backend that accepts video uploads, runs pose estimation,
computes biomechanics metrics, and compares against pro reference data.
"""

import os
import uuid
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil

from pose_pipeline import extract_pose_keypoints
from biomech_analysis import compute_biomech_metrics
from pro_reference import get_pro_reference, compare_to_pro, generate_feedback

app = FastAPI(title="Biomechanics Analysis API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def force_local_dev_cors(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/")
def root():
    return {"status": "ok", "message": "Biomechanics Analysis API running"}


@app.post("/analyze")
async def analyze_video(
    video: UploadFile = File(...),
    activity: str = Form(default="tennis_forehand"),
):
    allowed = {"video/mp4", "video/quicktime", "video/x-msvideo"}
    if video.content_type not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {video.content_type}. Use MP4 or MOV."
        )

    session_id = str(uuid.uuid4())[:8]
    video_path = UPLOAD_DIR / f"{session_id}_{video.filename}"

    try:
        with open(video_path, "wb") as f:
            shutil.copyfileobj(video.file, f)

        print(f"[{session_id}] Running pose estimation...")
        keypoint_frames = extract_pose_keypoints(str(video_path))

        if not keypoint_frames:
            raise HTTPException(
                status_code=422,
                detail="No pose detected in video. Ensure a person is clearly visible."
            )

        print(f"[{session_id}] Computing biomech metrics...")
        metrics = compute_biomech_metrics(keypoint_frames)
        print(f"[{session_id}] Hip score: {metrics.get('hip_score')} | Spine lean: {metrics.get('spine_lean')}")

        print(f"[{session_id}] Comparing to pro reference...")
        pro_reference = get_pro_reference(activity)
        comparison = compare_to_pro(metrics, pro_reference)

        feedback = generate_feedback(comparison, activity)

        result = {
            "session_id": session_id,
            "activity": activity,
            "frame_count": len(keypoint_frames),
            "keypoint_frames": keypoint_frames[::max(1, len(keypoint_frames) // 30)],
            "metrics": metrics,
            "pro_reference": pro_reference,
            "comparison": comparison,
            "feedback": feedback,
            "efficiency_score": comparison["overall_score"],
        }

        return JSONResponse(content=result)

    except HTTPException:
        raise
    except Exception as e:
        print(f"[{session_id}] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    finally:
        if video_path.exists():
            os.remove(video_path)


@app.get("/pro-reference/{activity}")
def get_reference(activity: str):
    ref = get_pro_reference(activity)
    if not ref:
        raise HTTPException(status_code=404, detail=f"No reference for activity: {activity}")
    return ref


@app.get("/activities")
def list_activities():
    return {
        "activities": [
            {"id": "tennis_forehand", "label": "Tennis Forehand"},
            {"id": "tennis_serve", "label": "Tennis Serve"},
            {"id": "squat", "label": "Barbell Squat"},
            {"id": "running", "label": "Running Form"},
        ]
    }