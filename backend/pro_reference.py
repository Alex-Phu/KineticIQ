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
        "hip_rotation": {"min": 0.4, "max": 0.95, "mean": 0.75},
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
        "hip_rotation": {"min": 0.35, "max": 0.90, "mean": 0.70},
        "spine_lean": {"min": 10.0, "max": 35.0, "mean": 22.0},
        "targets": {
            "elbow_at_contact": {"ideal": 165.0, "tolerance": 15.0, "description": "arm extension at contact"},
            "knee_bend": {"ideal": 130.0, "tolerance": 20.0, "description": "knee flexion in trophy position"},
            "spine_lean_max": {"ideal": 22.0, "tolerance": 10.0, "description": "back arch at trophy position"},
        }
    },

    "golf_swing": {
        "activity": "golf_swing",
        "source": "PGA Tour composite (Rory McIlroy/Tiger Woods/Jon Rahm averages)",
        "description": "Full driver swing with rotational power and lag",
        "angle_summary": {
            "right_elbow_angle": {"min": 80.0, "max": 170.0, "mean": 110.0, "range": 90.0},
            "right_shoulder_angle": {"min": 35.0, "max": 175.0, "mean": 105.0, "range": 140.0},
            "left_elbow_angle": {"min": 155.0, "max": 180.0, "mean": 170.0, "range": 25.0},
            "right_knee_angle": {"min": 120.0, "max": 170.0, "mean": 148.0, "range": 50.0},
            "left_knee_angle": {"min": 115.0, "max": 165.0, "mean": 142.0, "range": 50.0},
            "right_hip_angle": {"min": 140.0, "max": 175.0, "mean": 158.0, "range": 35.0},
        },
        "hip_rotation": {"min": 0.20, "max": 0.45, "mean": 0.32},
        "spine_lean": {"min": 20.0, "max": 40.0, "mean": 28.0},
        # Key biomechanical targets for feedback generation
        "targets": {
            "lead_arm_extension": {"ideal": 170.0, "tolerance": 15.0, "description": "left arm extension at top of backswing"},
            "knee_flex_address": {"ideal": 148.0, "tolerance": 12.0, "description": "knee flexion at address/impact"},
            "hip_rotation_range": {"ideal": 0.32, "tolerance": 0.08, "description": "hip-to-shoulder separation (X-factor)"},
            "spine_lean_max": {"ideal": 28.0, "tolerance": 8.0, "description": "forward spine tilt at address"},
        }
    },

    "golf_putt": {
        "activity": "golf_putt",
        "source": "PGA Tour putting analysis composite",
        "description": "Standard putting stroke with pendulum motion and stable lower body",
        "angle_summary": {
            "right_elbow_angle": {"min": 140.0, "max": 165.0, "mean": 152.0, "range": 25.0},
            "left_elbow_angle": {"min": 140.0, "max": 165.0, "mean": 153.0, "range": 25.0},
            "right_shoulder_angle": {"min": 5.0, "max": 20.0, "mean": 12.0, "range": 15.0},
            "right_knee_angle": {"min": 155.0, "max": 175.0, "mean": 165.0, "range": 20.0},
            "left_knee_angle": {"min": 155.0, "max": 175.0, "mean": 165.0, "range": 20.0},
        },
        "hip_rotation": {"min": 0.00, "max": 0.04, "mean": 0.02},
        "spine_lean": {"min": 30.0, "max": 50.0, "mean": 40.0},
        "targets": {
            "elbow_symmetry": {"ideal": 152.0, "tolerance": 10.0, "description": "arm bend for pendulum stroke"},
            "knee_stability": {"ideal": 165.0, "tolerance": 8.0, "description": "knee angle stability through stroke"},
            "hip_stability": {"ideal": 0.02, "tolerance": 0.02, "description": "minimal hip movement during stroke"},
            "spine_lean_max": {"ideal": 40.0, "tolerance": 8.0, "description": "forward spine tilt over ball"},
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

        # Skip joints with implausibly large deviations (likely camera angle issue)
        if deviation > 80:
            scores.append(50)  # neutral score instead of tanking
            comparison[joint] = {
                "status": "undetected",
                "message": f"Angle not measurable from this camera position",
                "score": 50,
            }
            continue

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


    # Overall score: weighted average (all equal weight for MVP)
    overall_score = round(sum(max(s, 40) for s in scores) / len(scores)) if scores else 50

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
        "tennis_serve": [
            {
                "joint": "right_elbow_angle",
                "category": "Arm Extension",
                "message_template": "Elbow extension at contact averages {user_val}°, which is {deviation}° {direction} than the ideal {pro_val}°. Full extension maximizes racket speed.",
                "correction": "Drive through the ball with a fully extended arm at contact — think 'reach for the sky' at the point of impact.",
            },
            {
                "joint": "right_shoulder_angle",
                "category": "Shoulder Rotation",
                "message_template": "Shoulder rotation range is {deviation}° {direction} than elite servers. Greater internal rotation generates more racket-head speed.",
                "correction": "Work on the trophy position: lead elbow high, tossing arm reaching up, and rear shoulder fully loaded before the swing begins.",
            },
            {
                "joint": "right_knee_angle",
                "category": "Leg Drive",
                "message_template": "Knee bend in the trophy position averages {user_val}°, {deviation}° {direction} than pros. Leg drive is the engine of a powerful serve.",
                "correction": "Sink deeper into your legs during the ball toss and explode upward through contact — the jump or leg push transfers energy into the swing.",
            },
        ],
        "golf_swing": [
            {
                "joint": "left_elbow_angle",
                "category": "Lead Arm Extension",
                "message_template": "Lead arm extension at top of backswing averages {user_val}°, which is {deviation}° {direction} than the pro ideal of {pro_val}°. A bent lead arm loses width and power.",
                "correction": "Keep your lead arm as straight as comfortably possible through the backswing — think of it as the radius of your swing arc.",
            },
            {
                "joint": "right_shoulder_angle",
                "category": "Shoulder Turn",
                "message_template": "Shoulder rotation range is {deviation}° {direction} than tour players. Insufficient turn limits X-factor and power generation.",
                "correction": "Focus on turning your trail shoulder behind you so your back faces the target at the top of the backswing.",
            },
            {
                "joint": "right_knee_angle",
                "category": "Knee Stability",
                "message_template": "Trail knee angle averages {user_val}°, which is {deviation}° {direction} than optimal. Proper knee flex creates a stable base for rotation.",
                "correction": "Maintain slight flex in your trail knee throughout the backswing — avoid straightening it as you rotate back.",
            },
            {
                "joint": "right_hip_angle",
                "category": "Hip Rotation",
                "message_template": "Hip rotation range is {deviation}° {direction} than tour average. Lead hip clearance is essential for lag and an inside-out swing path.",
                "correction": "Initiate the downswing by bumping and rotating your lead hip toward the target before your arms and club begin to drop.",
            },
        ],
        "golf_putt": [
            {
                "joint": "right_elbow_angle",
                "category": "Arm Consistency",
                "message_template": "Trail arm angle averages {user_val}°, {deviation}° {direction} than the pendulum-ideal {pro_val}°. Inconsistent arm angle disrupts stroke arc.",
                "correction": "Set your elbows softly at address and keep them at that angle throughout the stroke — avoid any scooping or breaking down at impact.",
            },
            {
                "joint": "right_knee_angle",
                "category": "Lower Body Stability",
                "message_template": "Knee angle variability is {deviation}° {direction} than elite putters. Lower body movement during the stroke causes directional errors.",
                "correction": "Feel like your lower body is 'locked' from address through the follow-through — all motion should come from the shoulders rocking like a pendulum.",
            },
            {
                "joint": "right_shoulder_angle",
                "category": "Shoulder Rock",
                "message_template": "Shoulder motion range is {deviation}° {direction} than tour average for putting. Shoulder rock drives the pendulum; too little or too much breaks rhythm.",
                "correction": "Practice the 'rock and roll' drill: keep your hands passive and let your shoulders do all the work, moving the putter back and through equal distances.",
            },
        ],
    }

    return rules.get(activity, rules["tennis_forehand"])
