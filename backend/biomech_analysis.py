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
    """
    ba = (a[0] - b[0], a[1] - b[1])
    bc = (c[0] - b[0], c[1] - b[1])

    dot = ba[0] * bc[0] + ba[1] * bc[1]
    mag_ba = math.sqrt(ba[0]**2 + ba[1]**2)
    mag_bc = math.sqrt(bc[0]**2 + bc[1]**2)

    if mag_ba < 1e-6 or mag_bc < 1e-6:
        return 0.0

    cos_angle = max(-1.0, min(1.0, dot / (mag_ba * mag_bc)))
    return round(math.degrees(math.acos(cos_angle)), 1)


def _trunk_lean(kp: dict, side: str) -> Optional[float]:
    """Trunk lean in degrees from vertical, measured at the hip."""
    hip = get_point(kp, f"{side}_hip")
    shoulder = get_point(kp, f"{side}_shoulder")
    if not (hip and shoulder):
        return None
    vertical_ref = (hip[0], hip[1] - 0.1)  # 0.1 in normalized coords (~10% of frame height)
    return compute_angle(vertical_ref, hip, shoulder)


def compute_joint_angles_per_frame(frame: Dict) -> Dict[str, Optional[float]]:
    """
    Given a single frame's keypoints, compute all relevant joint angles.
    """
    kp = frame["keypoints"]

    def angle_or_none(a_name, b_name, c_name, side="right"):
        a = get_point(kp, f"{side}_{a_name}")
        b = get_point(kp, f"{side}_{b_name}")
        c = get_point(kp, f"{side}_{c_name}")
        if a and b and c:
            return compute_angle(a, b, c)
        return None

    return {
        "right_elbow_angle": angle_or_none("shoulder", "elbow", "wrist", "right"),
        "right_shoulder_angle": angle_or_none("hip", "shoulder", "elbow", "right"),
        "left_elbow_angle": angle_or_none("shoulder", "elbow", "wrist", "left"),
        "left_shoulder_angle": angle_or_none("hip", "shoulder", "elbow", "left"),
        "right_knee_angle": angle_or_none("hip", "knee", "ankle", "right"),
        "left_knee_angle": angle_or_none("hip", "knee", "ankle", "left"),
        "right_hip_angle": angle_or_none("shoulder", "hip", "knee", "right"),
        "left_hip_angle": angle_or_none("shoulder", "hip", "knee", "left"),
        "right_trunk_lean_angle": _trunk_lean(kp, "right"),
        "left_trunk_lean_angle": _trunk_lean(kp, "left"),
    }


def compute_hip_rotation(frame: Dict) -> Optional[float]:
    """
    Estimate hip rotation as ratio of hip width to shoulder width.
    Smaller value = more hip turn.
    """
    kp = frame["keypoints"]
    lh = get_point(kp, "left_hip")
    rh = get_point(kp, "right_hip")
    if lh and rh:
        ls = get_point(kp, "left_shoulder")
        rs = get_point(kp, "right_shoulder")
        hip_width = abs(lh[0] - rh[0])
        if ls and rs:
            shoulder_width = abs(ls[0] - rs[0])
            if shoulder_width > 1e-6:
                return round(min(hip_width / shoulder_width, 1.0), 4)
        return round(min(hip_width * 5, 1.0), 4)
    return None


def compute_spine_lean(frame: Dict) -> Optional[float]:
    """
    Compute trunk/spine lean angle against vertical.
    """
    kp = frame["keypoints"]
    ls = get_point(kp, "left_shoulder")
    rs = get_point(kp, "right_shoulder")
    lh = get_point(kp, "left_hip")
    rh = get_point(kp, "right_hip")

    if not (ls and rs and lh and rh):
        return None

    shoulder_mid = ((ls[0] + rs[0]) / 2, (ls[1] + rs[1]) / 2)
    hip_mid = ((lh[0] + rh[0]) / 2, (lh[1] + rh[1]) / 2)
    spine = (shoulder_mid[0] - hip_mid[0], shoulder_mid[1] - hip_mid[1])

    vertical = (0, -1)
    dot = spine[0] * vertical[0] + spine[1] * vertical[1]
    mag = math.sqrt(spine[0]**2 + spine[1]**2)
    if mag < 1e-6:
        return None

    cos_a = max(-1.0, min(1.0, dot / mag))
    return round(math.degrees(math.acos(cos_a)), 1)


def aggregate_angles(angle_sequence: List[Dict]) -> Dict[str, Dict]:
    """
    Compute summary stats (min, max, mean, range) across all frames for each joint.
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


def score_trunk_lean(trunk_lean_angle: Optional[float]) -> float:
    """Score trunk-lean angle (0=upright) on a 0-100 scale."""
    if trunk_lean_angle is None:
        return 0.0
    IDEAL_MIN, IDEAL_MAX, WARN_BOUND = 10.0, 25.0, 40.0
    a = trunk_lean_angle
    if IDEAL_MIN <= a <= IDEAL_MAX:
        mid = (IDEAL_MIN + IDEAL_MAX) / 2.0
        return round(100.0 - abs(a - mid) / ((IDEAL_MAX - IDEAL_MIN) / 2.0) * 20.0, 1)
    if a < IDEAL_MIN:
        return round(80.0 * (a / IDEAL_MIN), 1)
    if a <= WARN_BOUND:
        return round(80.0 - 60.0 * ((a - IDEAL_MAX) / (WARN_BOUND - IDEAL_MAX)), 1)
    return round(max(0.0, 20.0 - (a - WARN_BOUND) * 2.0), 1)


def compute_biomech_metrics(keypoint_frames: List[Dict]) -> Dict[str, Any]:
    """
    Main function: compute all biomechanics metrics from the full video.
    """
    if not keypoint_frames:
        return {}

    frame_angles = [compute_joint_angles_per_frame(f) for f in keypoint_frames]
    angle_summary = aggregate_angles(frame_angles)

    hip_rotations = [compute_hip_rotation(f) for f in keypoint_frames]
    spine_leans = [compute_spine_lean(f) for f in keypoint_frames]

    hip_rotations_clean = [v for v in hip_rotations if v is not None]
    spine_leans_clean = [v for v in spine_leans if v is not None]

    hip_peak_frame = None
    if hip_rotations_clean:
        min_rot = min(hip_rotations_clean)
        hip_peak_frame = hip_rotations.index(min_rot)

    # Trunk lean score averaged across all frames
    lean_scores = []
    for fa in frame_angles:
        leans = [v for v in [fa.get("right_trunk_lean_angle"), fa.get("left_trunk_lean_angle")] if v is not None]
        if leans:
            lean_scores.append(score_trunk_lean(sum(leans) / len(leans)))
    hip_score = round(sum(lean_scores) / len(lean_scores), 1) if lean_scores else None

    return {
        "total_frames_analyzed": len(keypoint_frames),
        "duration_ms": keypoint_frames[-1]["timestamp_ms"] if keypoint_frames else 0,
        "angle_summary": angle_summary,
        "hip_score": hip_score,
        "hip_rotation": {
            "min": round(min(hip_rotations_clean), 4) if hip_rotations_clean else None,
            "max": round(max(hip_rotations_clean), 4) if hip_rotations_clean else None,
            "mean": round(sum(hip_rotations_clean) / len(hip_rotations_clean), 4) if hip_rotations_clean else None,
            "peak_frame": hip_peak_frame,
        },
        "spine_lean": {
            "min": round(min(spine_leans_clean), 1) if spine_leans_clean else None,
            "max": round(max(spine_leans_clean), 1) if spine_leans_clean else None,
            "mean": round(sum(spine_leans_clean) / len(spine_leans_clean), 1) if spine_leans_clean else None,
        },
        "angle_timeseries": frame_angles,
    }