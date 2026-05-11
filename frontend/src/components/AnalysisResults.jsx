import { useState, useRef, useEffect } from "react";
import PoseOverlay from "./PoseOverlay";
import FeedbackPanel from "./FeedbackPanel";
import AngleChart from "./AngleChart";

const FLAG_COLORS = {
  good: "#22c55e",
  warning: "#f59e0b",
  poor: "#ef4444",
  undetected: "#6b7280",
};

const JOINT_LABELS = {
  right_elbow_angle: "R. Elbow",
  left_elbow_angle: "L. Elbow",
  right_shoulder_angle: "R. Shoulder",
  left_shoulder_angle: "L. Shoulder",
  right_knee_angle: "R. Knee",
  left_knee_angle: "L. Knee",
  right_hip_angle: "R. Hip",
  left_hip_angle: "L. Hip",
  hip_rotation: "Hip Rotation",
};

export default function AnalysisResults({ data, videoUrl }) {
  const {
    efficiency_score,
    comparison,
    feedback,
    metrics,
    keypoint_frames,
    activity,
    frame_count,
  } = data;

  const [currentFrame, setCurrentFrame] = useState(0);
  const videoRef = useRef(null);

  const handleVideoTime = () => {
    if (!videoRef.current || !keypoint_frames?.length) return;
    const pct = videoRef.current.currentTime / videoRef.current.duration;
    const idx = Math.min(
      Math.floor(pct * keypoint_frames.length),
      keypoint_frames.length - 1
    );
    setCurrentFrame(idx);
  };

  const grade = comparison?.grade || "N/A";
  const scoreColor =
    efficiency_score >= 75 ? "#22c55e" :
    efficiency_score >= 50 ? "#f59e0b" : "#ef4444";

  return (
    <div className="results-page">
      {/* Score Header */}
      <div className="score-header">
        <div className="score-block">
          <div className="score-number" style={{ color: scoreColor }}>
            {efficiency_score}
          </div>
          <div className="score-label">Efficiency Score</div>
          <div className="score-grade" style={{ color: scoreColor }}>{grade}</div>
        </div>
        <div className="score-meta">
          <div className="meta-item">
            <span className="meta-key">Activity</span>
            <span className="meta-val">{activity.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase())}</span>
          </div>
          <div className="meta-item">
            <span className="meta-key">Frames Analyzed</span>
            <span className="meta-val">{frame_count}</span>
          </div>
          <div className="meta-item">
            <span className="meta-key">Duration</span>
            <span className="meta-val">{(metrics?.duration_ms / 1000).toFixed(1)}s</span>
          </div>
        </div>
      </div>

      {/* Video + Drills */}
      <div className="section-label">Movement Analysis</div>
      <div className="video-row">
        <div className="video-panel">
          <div className="panel-title">Your Video</div>
          <div className="video-wrapper">
            <video
              ref={videoRef}
              src={videoUrl}
              className="result-video"
              controls
              muted
              playsInline
              onTimeUpdate={handleVideoTime}
            />
            {keypoint_frames?.length > 0 && (
              <PoseOverlay
                keypoints={keypoint_frames[currentFrame]?.keypoints}
                comparison={comparison?.joint_comparison}
              />
            )}
          </div>
        </div>

        <div className="video-panel drill-panel">
          <div className="panel-title">Recommended Drills</div>
          <DrillSuggestions activity={activity} feedback={feedback} />
        </div>
      </div>

      {/* Joint Comparison */}
      <div className="section-label">Joint-by-Joint Comparison</div>
      <div className="joint-grid">

        {/* Trunk Lean — pulled directly from metrics.hip_score */}
        {metrics?.hip_score != null && (() => {
          const score = metrics.hip_score;
          const color = score >= 75 ? "#22c55e" : score >= 50 ? "#f59e0b" : "#ef4444";
          const flag = score >= 75 ? "GOOD" : score >= 50 ? "WARNING" : "POOR";
          return (
            <div className="joint-card" style={{ borderColor: color }}>
              <div className="joint-name">Trunk Lean</div>
              <div className="joint-score" style={{ color }}>{score}/100</div>
              <div className="joint-comparison">
                <div className="jc-row"><span className="jc-label">Score</span><span className="jc-val">{score}</span></div>
                <div className="jc-row"><span className="jc-label">Ideal</span><span className="jc-val">10–25°</span></div>
                <div className="jc-row"><span className="jc-label">Lean</span><span className="jc-val">{metrics?.spine_lean?.mean ?? "—"}°</span></div>
              </div>
              <div className="joint-flag" style={{ background: color }}>{flag}</div>
            </div>
          );
        })()}

        {/* All other joints from comparison */}
        {Object.entries(comparison?.joint_comparison || {}).filter(([joint]) => joint !== "hip_rotation").map(([joint, data]) => {
          if (!data || data.status === "undetected") return null;
          const color = FLAG_COLORS[data.flag] || "#6b7280";
          return (
            <div key={joint} className="joint-card" style={{ borderColor: color }}>
              <div className="joint-name">{JOINT_LABELS[joint] || joint}</div>
              <div className="joint-score" style={{ color }}>{data.score}/100</div>
              <div className="joint-comparison">
                <div className="jc-row">
                  <span className="jc-label">You</span>
                  <span className="jc-val">{data.user_mean}°</span>
                </div>
                <div className="jc-row">
                  <span className="jc-label">Pro</span>
                  <span className="jc-val">{data.pro_mean}°</span>
                </div>
                <div className="jc-row">
                  <span className="jc-label">Δ</span>
                  <span className="jc-val" style={{ color }}>{data.deviation_degrees}°</span>
                </div>
              </div>
              <div className="joint-flag" style={{ background: color }}>
                {data.flag.toUpperCase()}
              </div>
            </div>
          );
        })}
      </div>

      {/* Angle Chart */}
      {metrics?.angle_timeseries?.length > 0 && (
        <>
          <div className="section-label">Angle Over Time</div>
          <AngleChart timeseries={metrics.angle_timeseries} />
        </>
      )}

      {/* Feedback */}
      <div className="section-label">Actionable Corrections</div>
      <FeedbackPanel feedback={feedback} />
    </div>
  );
}

const DRILLS = {
  tennis_forehand: [
    { title: "Shadow Swing Slow-Mo", focus: "Arm Mechanics", description: "Stand at the baseline with no ball. Swing in slow motion, pausing at takeback, contact, and follow-through. Hold each position for 3 seconds.", reps: "3 sets × 10 swings" },
    { title: "Hip-Hands Separation", focus: "Kinetic Chain", description: "Hold racket at waist with both hands. Rotate hips fully toward the net BEFORE your arms move. Trains the hips-lead-hands sequence.", reps: "3 sets × 15 reps" },
    { title: "Wall Bounce Contact Point", focus: "Contact Position", description: "Stand 1m from a wall, bounce ball off it at waist height. Focus on contact in front of your body with elbow slightly bent.", reps: "5 min continuous" },
    { title: "Knee Bend Load Drill", focus: "Leg Drive", description: "Before each shadow swing, explicitly bend knees and push upward through contact. Exaggerate the leg drive.", reps: "3 sets × 10 swings" },
  ],
  tennis_serve: [
    { title: "Trophy Position Hold", focus: "Arm Position", description: "Toss the ball and freeze in the trophy position for 3 seconds before swinging. Builds muscle memory for the loaded position.", reps: "3 sets × 8 serves" },
    { title: "Toss Consistency Drill", focus: "Toss Mechanics", description: "Practice tossing without hitting — aim to land the ball on a target in front of your lead foot.", reps: "50 tosses" },
    { title: "Serve Without Racket", focus: "Shoulder Rotation", description: "Mimic the full serve motion with just your arm. Focuses on body rotation and shoulder turn rather than contact.", reps: "3 sets × 10 reps" },
  ],
  squat: [
    { title: "Box Squat to Depth", focus: "Depth", description: "Squat to a box set at parallel. Pause fully at the bottom then stand. Trains depth awareness without relying on momentum.", reps: "4 sets × 6 reps" },
    { title: "Goblet Squat", focus: "Hip Mechanics", description: "Hold a light weight at your chest and squat. The counterbalance forces an upright torso and proper hip hinge.", reps: "3 sets × 10 reps" },
    { title: "Ankle Mobility Wall Drill", focus: "Depth", description: "Stand facing a wall, toes 5cm away. Drive your knee toward the wall without heel lifting. Directly improves squat depth.", reps: "3 × 10 each side" },
  ],
  running: [
    { title: "High Knee March", focus: "Stride Mechanics", description: "March in place driving each knee to hip height. Slow and deliberate. Builds the pattern for proper stride mechanics.", reps: "4 × 30 seconds" },
    { title: "Arm Swing Drill", focus: "Arm Mechanics", description: "Stand still, practice arm swing only — elbows at 90°, driving straight back and forward. No crossing the midline.", reps: "3 × 30 seconds" },
    { title: "Metronome Run", focus: "Cadence", description: "Run to a metronome at 170–180 BPM. Forces higher cadence and naturally reduces overstriding.", reps: "10 min easy run" },
  ],
  golf_swing: [
  { title: "Slow Motion Backswing", focus: "Shoulder Turn", description: "Swing to the top in 5 seconds, pause, then swing down normally. Builds awareness of shoulder rotation and club position at the top.", reps: "3 sets × 10 swings" },
  { title: "Trail Arm Only Drill", focus: "Lead Arm Extension", description: "Hit short shots using only your trail arm. Forces the lead arm to stay extended and builds width in the swing arc.", reps: "20 balls" },
  { title: "Hip Bump Drill", focus: "Hip Rotation", description: "At the top of your backswing, consciously bump your lead hip toward the target before anything else moves. Trains proper downswing sequencing.", reps: "3 sets × 10 swings" },
  { title: "Feet Together Drill", focus: "Knee Stability", description: "Hit short shots with feet together. Forces balance and a centered rotation, eliminating sway.", reps: "20 balls" },
],
golf_putt: [
  { title: "Gate Drill", focus: "Stroke Path", description: "Place two tees just wider than your putter head on either side of the ball. Stroke through the gate without hitting either tee. Trains a straight pendulum path.", reps: "20 putts" },
  { title: "Eyes Closed Putting", focus: "Feel & Consistency", description: "Set up normally then close your eyes before stroking. Removes visual distraction and builds feel for a repeatable pendulum motion.", reps: "10 putts" },
  { title: "Metronome Stroke Drill", focus: "Arm Consistency", description: "Use a metronome app at 76 BPM. Stroke back on one beat, through on the next. Builds a consistent tempo and equal-length stroke.", reps: "15 putts" },
  { title: "Shoulder Rock Drill", focus: "Lower Body Stability", description: "Place a club across your chest under your arms. Practice rocking your shoulders without any hip or knee movement. The club should stay level.", reps: "3 sets × 10 reps" },
],
};

function DrillSuggestions({ activity, feedback }) {
  const drills = DRILLS[activity] || DRILLS.tennis_forehand;
  const weakFocuses = feedback?.map(f => f.category) || [];
  const sorted = [...drills].sort((a, b) => {
    const aMatch = weakFocuses.some(f => a.focus.includes(f) || f.includes(a.focus));
    const bMatch = weakFocuses.some(f => b.focus.includes(f) || f.includes(b.focus));
    return bMatch - aMatch;
  });
  return (
    <div className="drill-list">
      {sorted.map((drill, i) => {
        const isRecommended = weakFocuses.some(f => drill.focus.includes(f) || f.includes(drill.focus));
        return (
          <div key={i} className={`drill-card ${isRecommended ? "drill-recommended" : ""}`}>
            {isRecommended && <div className="drill-badge">Recommended for you</div>}
            <div className="drill-header">
              <span className="drill-title">{drill.title}</span>
              <span className="drill-focus">{drill.focus}</span>
            </div>
            <p className="drill-description">{drill.description}</p>
            <div className="drill-reps">{drill.reps}</div>
          </div>
        );
      })}
    </div>
  );
}