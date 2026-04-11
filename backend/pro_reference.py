"""
Pro Reference System
Contains pre-extracted biomechanics metrics from professional athletes.
In a real system, these would be derived from actual pro video analysis.
The comparison engine scores the user's movement against these baselines.
"""

from typing import Dict, Any, List


# ============================================================
# PRO REFERENCE DATASET
# These are realistic target ranges derived from sports science literature.
# Structure mirrors what compute_biomech_metrics() returns.
# ============================================================

PRO_REFERENCES = {
    "tennis_forehand": {
        "activity": "tennis_forehand",
        "source": "ATP Tour composite (Federer/Alcaraz/Djokovic averages)",
        "description": "Modern open-stance forehand with heavy topspin",
        "angle_summary": {
            "right_elbow_angle": {"min": 85.0, "max": 155.0, "mean": 120.0, "range": 70.0},
            "right_shoulder_angle": {"min": 40.0, "max": 160.0, "mean": 100.0, "range": 120.0},
            "left_elbow_angle": {"min": 90.0, "max": 145.0, "mean": 115.0, "range": 55.0},
            "right_knee_angle": {"min": 115.0, "max": 165.0, "mean": 140.0, "range": 50.0},
            "left_knee_angle": {"min": 120.0, "max": 170.0, "mean": 145.0, "range": 50.0},
            "right_hip_angle": {"min": 140.0, "max": 175.0, "mean": 160.0, "range": 35.0},
        },
        "hip_rotation": {"min": 0.05, "max": 0.18, "mean": 0.10},
        "spine_lean": {"min": 5.0, "max": 25.0, "mean": 14.0},
        # Key biomechanical targets for feedback generation
        "targets": {
            "elbow_at_contact": {"ideal": 120.0, "tolerance": 20.0, "description": "elbow angle at ball contact"},
            "knee_bend": {"ideal": 140.0, "tolerance": 15.0, "description": "knee flexion during loading"},
            "hip_rotation_range": {"ideal": 0.10, "tolerance": 0.05, "description": "hip rotation amplitude"},
            "spine_lean_max": {"ideal": 14.0, "tolerance": 8.0, "description": "forward trunk lean"},
        }
    },

    "tennis_serve": {
        "activity": "tennis_serve",
        "source": "ATP Tour serve analysis composite",
        "description": "Flat/kick serve with trophy position and full extension",
        "angle_summary": {
            "right_elbow_angle": {"min": 60.0, "max": 170.0, "mean": 110.0, "range": 110.0},
            "right_shoulder_angle": {"min": 30.0, "max": 175.0, "mean": 120.0, "range": 145.0},
            "right_knee_angle": {"min": 100.0, "max": 170.0, "mean": 135.0, "range": 70.0},
        },
        "hip_rotation": {"min": 0.04, "max": 0.15, "mean": 0.08},
        "spine_lean": {"min": 10.0, "max": 35.0, "mean": 22.0},
        "targets": {
            "elbow_at_contact": {"ideal": 165.0, "tolerance": 15.0, "description": "arm extension at contact"},
            "knee_bend": {"ideal": 130.0, "tolerance": 20.0, "description": "knee flexion in trophy position"},
            "spine_lean_max": {"ideal": 22.0, "tolerance": 10.0, "description": "back arch at trophy position"},
        }
    },

    "squat": {
        "activity": "squat",
        "source": "Elite powerlifting composite",
        "description": "Parallel or below-parallel back squat",
        "angle_summary": {
            "right_knee_angle": {"min": 70.0, "max": 175.0, "mean": 120.0, "range": 105.0},
            "left_knee_angle": {"min": 70.0, "max": 175.0, "mean": 120.0, "range": 105.0},
            "right_hip_angle": {"min": 65.0, "max": 175.0, "mean": 115.0, "range": 110.0},
            "left_hip_angle": {"min": 65.0, "max": 175.0, "mean": 115.0, "range": 110.0},
        },
        "hip_rotation": {"min": 0.12, "max": 0.22, "mean": 0.17},
        "spine_lean": {"min": 15.0, "max": 30.0, "mean": 22.0},
        "targets": {
            "knee_at_bottom": {"ideal": 75.0, "tolerance": 15.0, "description": "knee angle at depth"},
            "hip_at_bottom": {"ideal": 70.0, "tolerance": 15.0, "description": "hip flexion at depth"},
            "spine_lean_max": {"ideal": 22.0, "tolerance": 8.0, "description": "forward torso lean"},
        }
    },

    "running": {
        "activity": "running",
        "source": "Elite distance runner composite",
        "description": "Mid-foot strike, economical running form",
        "angle_summary": {
            "right_knee_angle": {"min": 90.0, "max": 165.0, "mean": 130.0, "range": 75.0},
            "left_knee_angle": {"min": 90.0, "max": 165.0, "mean": 130.0, "range": 75.0},
            "right_elbow_angle": {"min": 80.0, "max": 100.0, "mean": 90.0, "range": 20.0},
        },
        "hip_rotation": {"min": 0.15, "max": 0.28, "mean": 0.20},
        "spine_lean": {"min": 5.0, "max": 12.0, "mean": 8.0},
        "targets": {
            "knee_drive": {"ideal": 130.0, "tolerance": 15.0, "description": "knee lift angle during swing"},
            "elbow_angle": {"ideal": 90.0, "tolerance": 10.0, "description": "arm bend for efficiency"},
            "spine_lean_max": {"ideal": 8.0, "tolerance": 4.0, "description": "forward lean angle"},
        }
    },
}


def get_pro_reference(activity: str) -> Dict[str, Any]:
    """Return the pro reference data for the specified activity."""
    return PRO_REFERENCES.get(activity, PRO_REFERENCES["tennis_forehand"])


def compare_to_pro(user_metrics: Dict, pro_ref: Dict) -> Dict[str, Any]:
    """
    Compare user's computed metrics to pro reference.
    For each joint, compute:
      - deviation: how far user's mean angle is from pro mean
      - score: 0–100 based on how close to pro range
      - flag: 'good', 'warning', 'poor'
    Returns overall_score and per-joint breakdown.
    """
    comparison = {}
    scores = []

    user_angles = user_metrics.get("angle_summary", {})
    pro_angles = pro_ref.get("angle_summary", {})

    for joint, pro_stats in pro_angles.items():
        if pro_stats is None:
            continue

        user_stats = user_angles.get(joint)

        if user_stats is None:
            # Joint not detected in user video
            comparison[joint] = {
                "status": "undetected",
                "message": f"Could not detect {joint.replace('_', ' ')} in video",
                "score": 50,  # neutral — don't penalize for detection failure
            }
            scores.append(50)
            continue

        pro_mean = pro_stats["mean"]
        pro_range = pro_stats.get("range", 30)
        user_mean = user_stats["mean"]
        user_range = user_stats.get("range", 0)

        # Deviation from pro mean
        deviation = abs(user_mean - pro_mean)

        # Score: full score if within pro range, degrades beyond
        half_range = pro_range / 2
        if deviation <= half_range:
            joint_score = 100 - (deviation / half_range) * 20  # 80–100
        elif deviation <= pro_range:
            joint_score = 80 - ((deviation - half_range) / half_range) * 30  # 50–80
        else:
            joint_score = max(0, 50 - (deviation - pro_range) * 1.5)

        joint_score = round(joint_score)

        # Range of motion comparison
        range_diff = user_range - pro_range

        flag = "good" if joint_score >= 75 else "warning" if joint_score >= 50 else "poor"

        comparison[joint] = {
            "user_mean": user_mean,
            "pro_mean": pro_mean,
            "deviation_degrees": round(deviation, 1),
            "range_diff": round(range_diff, 1),
            "score": joint_score,
            "flag": flag,
        }
        scores.append(joint_score)

    # Compare hip rotation
    user_hip = user_metrics.get("hip_rotation", {})
    pro_hip = pro_ref.get("hip_rotation", {})
    if user_hip.get("mean") and pro_hip.get("mean"):
        hip_dev = abs(user_hip["mean"] - pro_hip["mean"])
        hip_score = max(0, round(100 - (hip_dev / pro_hip["mean"]) * 100))
        comparison["hip_rotation"] = {
            "user_mean": user_hip["mean"],
            "pro_mean": pro_hip["mean"],
            "deviation": round(hip_dev, 4),
            "score": hip_score,
            "flag": "good" if hip_score >= 75 else "warning" if hip_score >= 50 else "poor",
        }
        scores.append(hip_score)

    # Overall score: weighted average (all equal weight for MVP)
    overall_score = round(sum(scores) / len(scores)) if scores else 50

    return {
        "overall_score": overall_score,
        "grade": score_to_grade(overall_score),
        "joint_comparison": comparison,
    }


def score_to_grade(score: int) -> str:
    if score >= 90: return "Elite"
    if score >= 75: return "Advanced"
    if score >= 60: return "Intermediate"
    if score >= 45: return "Beginner"
    return "Needs Work"


def generate_feedback(comparison: Dict, activity: str) -> List[Dict[str, str]]:
    """
    Generate 2–5 actionable feedback items based on comparison results.
    Each item has: category, severity, message, correction.
    """
    feedback = []
    joint_comp = comparison.get("joint_comparison", {})

    # Activity-specific feedback rules
    rules = _get_feedback_rules(activity)

    for rule in rules:
        joint = rule["joint"]
        data = joint_comp.get(joint)
        if not data or data.get("status") == "undetected":
            continue

        flag = data.get("flag", "good")
        deviation = data.get("deviation_degrees", 0)
        user_mean = data.get("user_mean", 0)
        pro_mean = data.get("pro_mean", 0)

        if flag in ("warning", "poor"):
            direction = "higher" if user_mean > pro_mean else "lower"
            severity = "high" if flag == "poor" else "medium"

            feedback.append({
                "joint": joint,
                "severity": severity,
                "category": rule["category"],
                "message": rule["message_template"].format(
                    direction=direction,
                    deviation=round(deviation),
                    user_val=round(user_mean),
                    pro_val=round(pro_mean),
                ),
                "correction": rule["correction"].format(direction=direction),
                "score": data["score"],
            })

    # Cap at 5 most important (sorted by severity)
    severity_order = {"high": 0, "medium": 1, "low": 2}
    feedback.sort(key=lambda x: severity_order.get(x["severity"], 2))
    return feedback[:5]


def _get_feedback_rules(activity: str) -> List[Dict]:
    """Return the feedback rule templates for a given activity."""
    rules = {
        "tennis_forehand": [
            {
                "joint": "right_elbow_angle",
                "category": "Arm Mechanics",
                "message_template": "Your elbow angle is {deviation}° {direction} than optimal ({user_val}° vs {pro_val}° pro average). This affects swing path and power generation.",
                "correction": "Focus on maintaining a relaxed, semi-bent elbow through the takeback and accelerate through contact with elbow leading slightly.",
            },
            {
                "joint": "right_shoulder_angle",
                "category": "Shoulder Rotation",
                "message_template": "Shoulder rotation range is {direction} than pros by {deviation}°. You're averaging {user_val}° vs {pro_val}°.",
                "correction": "Work on fuller shoulder turn during takeback — your non-dominant shoulder should point toward the target zone on the takeback.",
            },
            {
                "joint": "right_knee_angle",
                "category": "Leg Drive",
                "message_template": "Knee flexion during your swing averages {user_val}°, which is {deviation}° {direction} than pros. Leg load directly affects upward power transfer.",
                "correction": "Bend your knees more during the loading phase and push upward through contact to drive power from the ground up.",
            },
            {
                "joint": "right_hip_angle",
                "category": "Hip Mechanics",
                "message_template": "Hip rotation range is {deviation}° {direction} than pro baseline. Hips should drive the kinetic chain before shoulders unwind.",
                "correction": "Initiate the forward swing with your hips rotating toward the net before your arm follows — think 'hips then hands'.",
            },
        ],
        "squat": [
            {
                "joint": "right_knee_angle",
                "category": "Depth",
                "message_template": "Knee angle at bottom averages {user_val}°, {deviation}° {direction} than parallel ({pro_val}°). Full depth maximizes muscle activation.",
                "correction": "Work on ankle mobility and hip flexibility to achieve greater depth. Box squats to depth can help pattern the movement.",
            },
            {
                "joint": "right_hip_angle",
                "category": "Hip Hinge",
                "message_template": "Hip flexion ({user_val}°) is {deviation}° {direction} than target. Proper hip crease ensures a true squat, not a knee-dominant pattern.",
                "correction": "Push your knees out and sit between your legs rather than just bending at the knees. Think 'sit down and back'.",
            },
        ],
        "running": [
            {
                "joint": "right_elbow_angle",
                "category": "Arm Mechanics",
                "message_template": "Arm bend averages {user_val}°, {deviation}° {direction} from the efficient 90° position. Arm mechanics directly affect energy economy.",
                "correction": "Keep elbows at roughly 90° and drive them straight back and forward, not across the body.",
            },
            {
                "joint": "right_knee_angle",
                "category": "Stride Mechanics",
                "message_template": "Knee drive angle is {deviation}° {direction} than elite runners. Insufficient knee lift reduces stride length and power.",
                "correction": "Focus on driving your knee upward to hip height on each stride, especially when fatigued.",
            },
        ],
    }

    return rules.get(activity, rules["tennis_forehand"])
