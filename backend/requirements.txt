# KinetIQ

KinetIQ analyzes athletic movement from uploaded video using AI pose estimation, scores each joint against pro baselines, and gives you actionable drill suggestions to fix your form.

YOLO/MediaPipe heavy model not included in repo due to file size — downloaded automatically on first run.

## Features

- Detects 13 body landmarks per frame using Google MediaPipe Pose
- Computes real joint angles (elbow, shoulder, hip, knee, trunk lean) using biomechanics math
- Scores each joint 0–100 against pro athlete reference data
- Color-coded skeleton overlay synced to video playback
- Drill suggestions ranked by your weakest detected areas
- Supports Tennis (forehand, serve) and Golf (full swing, putt)

## Requirements

- Python 3.9
- Node.js 18+
- OpenCV
- MediaPipe
- FastAPI + Uvicorn

## Install

Clone the repo:

```bash
git clone https://github.com/Technocations2027/KineticIQ.git
cd KineticIQ
```

Backend:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn python-multipart opencv-python-headless matplotlib
pip install mediapipe --no-deps
pip install flatbuffers protobuf absl-py attrs
uvicorn main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 in your browser.