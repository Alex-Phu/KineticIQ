import { useState } from "react";

const JOINTS_TO_CHART = [
  { key: "right_elbow_angle", label: "R. Elbow", color: "#3b82f6" },
  { key: "right_knee_angle", label: "R. Knee", color: "#22c55e" },
  { key: "right_shoulder_angle", label: "R. Shoulder", color: "#f59e0b" },
  { key: "right_hip_angle", label: "R. Hip", color: "#a855f7" },
];

export default function AngleChart({ timeseries }) {
  const [activeJoints, setActiveJoints] = useState(
    new Set(["right_elbow_angle", "right_knee_angle"])
  );

  // Downsample to max 60 points for performance
  const sample = timeseries.filter((_, i) => i % Math.max(1, Math.floor(timeseries.length / 60)) === 0);

  const W = 800;
  const H = 200;
  const PAD = { top: 10, right: 20, bottom: 30, left: 40 };
  const chartW = W - PAD.left - PAD.right;
  const chartH = H - PAD.top - PAD.bottom;

  // Y axis: 0–180 degrees
  const toY = (angle) => PAD.top + chartH - (angle / 180) * chartH;
  const toX = (i) => PAD.left + (i / (sample.length - 1)) * chartW;

  const toggleJoint = (key) => {
    setActiveJoints((prev) => {
      const next = new Set(prev);
      next.has(key) ? next.delete(key) : next.add(key);
      return next;
    });
  };

  return (
    <div className="chart-wrapper">
      {/* Legend / toggles */}
      <div className="chart-legend">
        {JOINTS_TO_CHART.map(({ key, label, color }) => (
          <button
            key={key}
            className={`legend-btn ${activeJoints.has(key) ? "active" : "inactive"}`}
            style={activeJoints.has(key) ? { borderColor: color, color } : {}}
            onClick={() => toggleJoint(key)}
          >
            <span className="legend-dot" style={{ background: activeJoints.has(key) ? color : "#94a3b8" }} />
            {label}
          </button>
        ))}
      </div>

      {/* SVG Chart */}
      <svg
        viewBox={`0 0 ${W} ${H}`}
        className="angle-chart-svg"
        preserveAspectRatio="none"
      >
        {/* Grid lines */}
        {[0, 45, 90, 135, 180].map((deg) => (
          <g key={deg}>
            <line
              x1={PAD.left}
              y1={toY(deg)}
              x2={W - PAD.right}
              y2={toY(deg)}
              stroke="#e2e8f0"
              strokeWidth="1"
              strokeDasharray="4 4"
            />
            <text
              x={PAD.left - 5}
              y={toY(deg) + 4}
              textAnchor="end"
              fontSize="9"
              fill="#94a3b8"
              fontFamily="monospace"
            >
              {deg}°
            </text>
          </g>
        ))}

        {/* Time axis label */}
        <text x={W / 2} y={H - 2} textAnchor="middle" fontSize="9" fill="#94a3b8" fontFamily="monospace">
          Frame progression →
        </text>

        {/* Joint angle lines */}
        {JOINTS_TO_CHART.map(({ key, color }) => {
          if (!activeJoints.has(key)) return null;
          const points = sample
            .map((frame, i) => {
              const angle = frame[key];
              if (angle == null) return null;
              return `${toX(i)},${toY(angle)}`;
            })
            .filter(Boolean);

          if (points.length < 2) return null;

          return (
            <polyline
              key={key}
              points={points.join(" ")}
              fill="none"
              stroke={color}
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              opacity="0.85"
            />
          );
        })}
      </svg>
    </div>
  );
}
