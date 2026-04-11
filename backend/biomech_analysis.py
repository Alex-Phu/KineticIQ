"""
Biomechanics Analysis
Computes joint angles, timing metrics, and kinetic chain sequencing
from a sequence of pose keypoint frames.
"""

import math
from typing import List, Dict, Any, Optional
from pose_pipeline import get_point


def compute_angle(a: tuple, b: tuple, c: tuple) -> float:
    """
    Compute the angle (degrees) at joint B, formed by points A-B-C.
    This is the standard joint angle calculation used in biomechanics:
      - a, b, c are (x, y) tuples
      - returns angle at vertex B
    """
    # Vectors from B to A, and B to C
    ba = (a[0] - b[0], a[1] - b[1])
    bc = (c[0] - b[0], c[1] - b[1])

    # Dot product and magnitudes
    dot = ba[0] * bc[0] + ba[1] * bc[1]
    mag_ba = math.sqrt(ba[0]**2 + ba[1]**2)
    mag_bc = math.sqrt(bc[0]**2 + bc[1]**2)

    if mag_ba < 1e-6 or mag_bc < 1e-6:
        return 0.0

    # Clamp to [-1, 1] to avoid floating point errors in acos
    cos_angle = max(-1.0, min(1.0, dot / (mag_ba * mag_bc)))
    return round(math.degrees(math.acos(cos_angle)), 1)


def compute_joint_angles_per_frame(frame: Dict) -> Dict[str, Optional[float]]:
    """
    Given a single frame's keypoints, compute all relevant joint angles.
    Returns dict of joint_name -> angle_degrees (or None if keypoints missing).
    """
    kp = frame["keypoints"]

    def angle_or_none(a_name, b_name, c_name, side="right"):
        """Try to compute angle; return None if any keypoint is missing."""
        a = get_point(kp, f"{side}_{a_name}")
        b = get_point(kp, f"{side}_{b_name}")
        c = get_point(kp, f"{side}_{c_name}")
        if a and b and c:
            return compute_angle(a, b, c)
        return None

    return {
        # Right arm angles
        "right_elbow_angle": angle_or_none("shoulder", "elbow", "wrist", "right"),
        "right_shoulder_angle": angle_or_none("hip", "shoulder", "elbow", "right"),
        # Left arm angles
        "left_elbow_angle": angle_or_none("shoulder", "elbow", "wrist", "left"),
        "left_shoulder_angle": angle_or_none("hip", "shoulder", "elbow", "left"),
        # Leg angles
        "right_knee_angle": angle_or_none("hip", "knee", "ankle", "right"),
        "left_knee_angle": angle_or_none("hip", "knee", "ankle", "left"),
        # Hip angle (trunk lean) — uses shoulder-hip-knee chain
        "right_hip_angle": angle_or_none("shoulder", "hip", "knee", "right"),
        "left_hip_angle": angle_or_none("shoulder", "hip", "knee", "left"),
    }


def compute_hip_rotation(frame: Dict) -> Optional[float]:
    """
    Estimate hip rotation as the horizontal distance between left/right hips.
    A smaller x-distance indicates more hip turn (rotated away from camera).
    Returns normalized rotation value 0–1.
    """
    kp = frame["keypoints"]
    lh = get_point(kp, "left_hip")
    rh = get_point(kp, "right_hip")
    if lh and rh:
        return round(abs(lh[0] - rh[0]), 4)
    return None


def compute_spine_lean(frame: Dict) -> Optional[float]:
    """
    Compute trunk/spine lean angle.
    Uses midpoint of shoulders vs midpoint of hips as spine vector,
    then angles it against vertical.
    """
    kp = frame["keypoints"]
    ls = get_point(kp, "left_shoulder")
    rs = get_point(kp, "right_shoulder")
    lh = get_point(kp, "left_hip")
    rh = get_point(kp, "right_hip")

    if not (ls and rs and lh and rh):
        return None

    # Midpoints
    shoulder_mid = ((ls[0] + rs[0]) / 2, (ls[1] + rs[1]) / 2)
    hip_mid = ((lh[0] + rh[0]) / 2, (lh[1] + rh[1]) / 2)

    # Spine vector (hip → shoulder)
    spine = (shoulder_mid[0] - hip_mid[0], shoulder_mid[1] - hip_mid[1])

    # Angle against vertical (0, -1) — negative y because screen coords
    vertical = (0, -1)
    dot = spine[0]*vertical[0] + spine[1]*vertical[1]
    mag = math.sqrt(spine[0]**2 + spine[1]**2)
    if mag < 1e-6:
        return None

    cos_a = max(-1.0, min(1.0, dot / mag))
    return round(math.degrees(math.acos(cos_a)), 1)


def aggregate_angles(angle_sequence: List[Dict]) -> Dict[str, Dict]:
    """
    Given a list of per-frame angle dicts, compute summary stats:
    min, max, mean, and the value at peak frame (frame with largest total angle sum).
    """
    if not angle_sequence:
        return {}

    joint_names = list(angle_sequence[0].keys())
    summary = {}

    for joint in joint_names:
        values = [f[joint] for f in angle_sequence if f[joint] is not None]
        if values:
            summary[joint] = {
                "min": round(min(values), 1),
                "max": round(max(values), 1),
                "mean": round(sum(values) / len(values), 1),
                "range": round(max(values) - min(values), 1),
            }
        else:
            summary[joint] = None

    return summary


def compute_biomech_metrics(keypoint_frames: List[Dict]) -> Dict[str, Any]:
    """
    Main function: compute all biomechanics metrics from the full video.
    Returns structured metrics dict ready for comparison and feedback.
    """
    if not keypoint_frames:
        return {}

    # Per-frame angle computation
    frame_angles = [compute_joint_angles_per_frame(f) for f in keypoint_frames]

    # Summary stats across all frames
    angle_summary = aggregate_angles(frame_angles)

    # Hip rotation and spine lean at each frame
    hip_rotations = [compute_hip_rotation(f) for f in keypoint_frames]
    spine_leans = [compute_spine_lean(f) for f in keypoint_frames]

    hip_rotations_clean = [v for v in hip_rotations if v is not None]
    spine_leans_clean = [v for v in spine_leans if v is not None]

    # Kinetic chain sequencing: estimate timing of hip vs shoulder peak velocity
    # Simplified: find frame index where hip rotation is smallest (most rotated)
    hip_peak_frame = None
    if hip_rotations_clean:
        min_rot = min(hip_rotations_clean)
        hip_peak_frame = hip_rotations.index(min_rot)

    return {
        "total_frames_analyzed": len(keypoint_frames),
        "duration_ms": keypoint_frames[-1]["timestamp_ms"] if keypoint_frames else 0,
        "angle_summary": angle_summary,
        "hip_rotation": {
            "min": round(min(hip_rotations_clean), 4) if hip_rotations_clean else None,
            "max": round(max(hip_rotations_clean), 4) if hip_rotations_clean else None,
            "mean": round(sum(hip_rotations_clean)/len(hip_rotations_clean), 4) if hip_rotations_clean else None,
            "peak_frame": hip_peak_frame,
        },
        "spine_lean": {
            "min": round(min(spine_leans_clean), 1) if spine_leans_clean else None,
            "max": round(max(spine_leans_clean), 1) if spine_leans_clean else None,
            "mean": round(sum(spine_leans_clean)/len(spine_leans_clean), 1) if spine_leans_clean else None,
        },
        # Store the per-frame angle timeseries for charting in frontend
        "angle_timeseries": frame_angles,
    }
