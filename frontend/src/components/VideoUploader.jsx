import { useState, useRef } from "react";

const ACTIVITIES = [
  { id: "tennis_forehand", label: "Tennis Forehand" },
  { id: "tennis_serve", label: "Tennis Serve" },
  { id: "golf_swing", label: "Golf Swing" },
  { id: "golf_putt", label: "Golf Putt" },
];

export default function VideoUploader({ onAnalyze, error }) {
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [activity, setActivity] = useState("tennis_forehand");
  const [previewUrl, setPreviewUrl] = useState(null);
  const fileInputRef = useRef(null);

  const handleFile = (file) => {
    if (!file) return;
    const allowed = ["video/mp4", "video/quicktime", "video/x-msvideo"];
    if (!allowed.includes(file.type)) {
      alert("Please upload an MP4 or MOV video file.");
      return;
    }
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false)
    const file = e.dataTransfer.files[0];
    handleFile(file);
  };

  const handleSubmit = () => {
    if (selectedFile) onAnalyze(selectedFile, activity);
  };

  return (
    <div className="uploader-page">
      <div className="uploader-hero">
        <h1 className="hero-title">
          Upload HERE<br />
          <span className="hero-accent"></span>
        </h1>
        <p className="hero-desc">
        </p>
      </div>

      <div className="uploader-card">
        {/* Activity Selector */}
        <div className="field">
          <label className="field-label">Activity</label>
          <div className="activity-grid">
            {ACTIVITIES.map((a) => (
              <button
                key={a.id}
                className={`activity-btn ${activity === a.id ? "active" : ""}`}
                onClick={() => setActivity(a.id)}
              >
                {a.label}
              </button>
            ))}
          </div>
        </div>

        {/* Drop Zone */}
        <div className="field">
          <label className="field-label">Video File</label>
          <div
            className={`drop-zone ${dragOver ? "drag-over" : ""} ${selectedFile ? "has-file" : ""}`}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="video/mp4,video/quicktime"
              style={{ display: "none" }}
              onChange={(e) => handleFile(e.target.files[0])}
            />
            {previewUrl ? (
              <div className="preview-container">
                <video
                  src={previewUrl}
                  className="video-preview"
                  muted
                  playsInline
                  controls
                />
                <p className="preview-name">{selectedFile?.name}</p>
              </div>
            ) : (
              <div className="drop-placeholder">
                <div className="drop-icon">▲</div>
                <p className="drop-text">Drop video here <span className="drop-link"></span></p>
                <p className="drop-hint"></p>
              </div>
            )}
          </div>
        </div>

        {error && (
          <div className="error-banner">
            <strong>Error:</strong> {error}
          </div>
        )}

        <button
          className="btn-primary"
          disabled={!selectedFile}
          onClick={handleSubmit}
        >
          Run
        </button> 
      </div>
    </div>
  );
}
