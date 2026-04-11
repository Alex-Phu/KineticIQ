import { useEffect, useRef } from "react";

const SKELETON_CONNECTIONS = [
  ["left_shoulder", "right_shoulder"],
  ["left_shoulder", "left_elbow"],
  ["left_elbow", "left_wrist"],
  ["right_shoulder", "right_elbow"],
  ["right_elbow", "right_wrist"],
  ["left_shoulder", "left_hip"],
  ["right_shoulder", "right_hip"],
  ["left_hip", "right_hip"],
  ["left_hip", "left_knee"],
  ["left_knee", "left_ankle"],
  ["right_hip", "right_knee"],
  ["right_knee", "right_ankle"],
  ["nose", "left_shoulder"],
  ["nose", "right_shoulder"],
];

const FLAG_COLORS = {
  good: "#22c55e",
  warning: "#f59e0b",
  poor: "#ef4444",
  undetected: "#94a3b8",
};

const KP_TO_JOINT = {
  right_elbow: "right_elbow_angle",
  left_elbow: "left_elbow_angle",
  right_shoulder: "right_shoulder_angle",
  left_shoulder: "left_shoulder_angle",
  right_knee: "right_knee_angle",
  left_knee: "left_knee_angle",
  right_hip: "right_hip_angle",
  left_hip: "left_hip_angle",
};

function getJointColor(kpName, comparison) {
  if (!comparison) return "#38bdf8";
  const jointKey = KP_TO_JOINT[kpName];
  if (!jointKey) return "#38bdf8";
  const jointData = comparison[jointKey];
  if (!jointData || jointData.status === "undetected") return "#94a3b8";
  return FLAG_COLORS[jointData.flag] || "#38bdf8";
}

function drawSkeleton(canvas, keypoints, comparison) {
  if (!canvas || !keypoints) return;

  const rect = canvas.getBoundingClientRect();
  if (canvas.width !== rect.width || canvas.height !== rect.height) {
    canvas.width = rect.width;
    canvas.height = rect.height;
  }

  const W = canvas.width;
  const H = canvas.height;
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, W, H);

  const videoEl = canvas.parentElement?.querySelector("video");
  let offsetX = 0, offsetY = 0, scaleW = W, scaleH = H;

  if (videoEl && videoEl.videoWidth && videoEl.videoHeight) {
    const videoAspect = videoEl.videoWidth / videoEl.videoHeight;
    const containerAspect = W / H;

    if (videoAspect > containerAspect) {
      scaleW = W;
      scaleH = W / videoAspect;
      offsetX = 0;
      offsetY = (H - scaleH) / 2;
    } else {
      scaleH = H;
      scaleW = H * videoAspect;
      offsetX = (W - scaleW) / 2;
      offsetY = 0;
    }
  }

  const px = (kp) => [offsetX + kp.x * scaleW, offsetY + kp.y * scaleH];

  ctx.lineWidth = 2.5;
  ctx.lineCap = "round";

  for (const [a, b] of SKELETON_CONNECTIONS) {
    const kpA = keypoints[a];
    const kpB = keypoints[b];
    if (!kpA || !kpB) continue;
    if ((kpA.visibility ?? 1) < 0.3 || (kpB.visibility ?? 1) < 0.3) continue;

    const [ax, ay] = px(kpA);
    const [bx, by] = px(kpB);

    const colorA = getJointColor(a, comparison);
    const colorB = getJointColor(b, comparison);

    const grad = ctx.createLinearGradient(ax, ay, bx, by);
    grad.addColorStop(0, colorA + "cc");
    grad.addColorStop(1, colorB + "cc");

    ctx.strokeStyle = grad;
    ctx.beginPath();
    ctx.moveTo(ax, ay);
    ctx.lineTo(bx, by);
    ctx.stroke();
  }

  for (const [name, kp] of Object.entries(keypoints)) {
    if ((kp.visibility ?? 1) < 0.3) continue;
    const [x, y] = px(kp);
    const color = getJointColor(name, comparison);

    ctx.beginPath();
    ctx.arc(x, y, 6, 0, Math.PI * 2);
    ctx.fillStyle = color + "33";
    ctx.fill();

    ctx.beginPath();
    ctx.arc(x, y, 3.5, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();
  }
}

export default function PoseOverlay({ keypoints, comparison }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    drawSkeleton(canvasRef.current, keypoints, comparison);
  }, [keypoints, comparison]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const observer = new ResizeObserver(() => {
      drawSkeleton(canvas, keypoints, comparison);
    });
    observer.observe(canvas);
    return () => observer.disconnect();
  }, [keypoints, comparison]);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        pointerEvents: "none",
      }}
    />
  );
}