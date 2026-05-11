"""
Pose Estimation Pipeline
Uses MediaPipe Pose Landmarker (new Tasks API, compatible with mediapipe >= 0.10)
to extract body keypoints from each video frame.
"""

import cv2
import urllib.request
import os
from typing import List, Dict, Any

import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python.vision import PoseLandmarker, PoseLandmarkerOptions, RunningMode

#MEDIAPIPE LABELLS
LANDMARK_NAMES = {
    0:  "nose",
    11: "left_shoulder",
    12: "right_shoulder",
    13: "left_elbow",
    14: "right_elbow",
    15: "left_wrist",
    16: "right_wrist",
    23: "left_hip",
    24: "right_hip",
    25: "left_knee",
    26: "right_knee",
    27: "left_ankle",
    28: "right_ankle",
}

TRACKED_INDICES = set(LANDMARK_NAMES.keys())

MODEL_PATH = "pose_landmarker_heavy.task"
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/latest/pose_landmarker_heavy.task"


def download_model():
    """Download the pose landmarker model file if not already present."""
    if not os.path.exists(MODEL_PATH):
        print("Downloading MediaPipe pose model (~5MB)...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("Model downloaded.")


def extract_pose_keypoints(video_path: str) -> List[Dict[str, Any]]:
    """
    Process a video file frame-by-frame using MediaPipe Pose Landmarker.
    Returns a list of frame dicts, each containing:
      - frame_index: int
      - timestamp_ms: float
      - keypoints: dict of landmark_name -> {x, y, z, visibility}
    """
    download_model()

    base_options = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
    options = PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=RunningMode.VIDEO,
        num_poses=1,
        min_pose_detection_confidence=0.5,
        min_pose_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frames_data = []
    frame_index = 0

    with PoseLandmarker.create_from_options(options) as landmarker:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=frame_rgb
            )

            timestamp_ms = int((frame_index / fps) * 1000)
            results = landmarker.detect_for_video(mp_image, timestamp_ms)

            if results.pose_landmarks and len(results.pose_landmarks) > 0:
                landmarks = results.pose_landmarks[0]
                keypoints = {}

                for idx, landmark in enumerate(landmarks):
                    if idx in TRACKED_INDICES:
                        name = LANDMARK_NAMES[idx]
                        keypoints[name] = {
                            "x": round(landmark.x, 4),
                            "y": round(landmark.y, 4),
                            "z": round(landmark.z, 4),
                            "visibility": round(landmark.visibility if hasattr(landmark, 'visibility') else 1.0, 3),
                        }

                frames_data.append({
                    "frame_index": frame_index,
                    "timestamp_ms": float(timestamp_ms),
                    "keypoints": keypoints,
                })

            frame_index += 1

    cap.release()
    return frames_data


def get_point(keypoints: Dict, name: str) -> tuple:
    """Return (x, y) for a named keypoint, or None if not detected."""
    kp = keypoints.get(name)
    if kp and kp.get("visibility", 0) > 0.3:
        return (kp["x"], kp["y"])
    return None