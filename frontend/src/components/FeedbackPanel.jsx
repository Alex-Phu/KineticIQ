const SEVERITY_CONFIG = {
  high: { label: "Critical", color: "#ef4444", bg: "#fef2f2", border: "#fca5a5" },
  medium: { label: "Improve", color: "#f59e0b", bg: "#fffbeb", border: "#fcd34d" },
  low: { label: "Minor", color: "#3b82f6", bg: "#eff6ff", border: "#93c5fd" },
};

export default function FeedbackPanel({ feedback }) {
  if (!feedback || feedback.length === 0) {
    return (
      <div className="feedback-empty">
        <p>No FEEDBACK </p>
      </div>
    );
  }

  return (
    <div className="feedback-list">
      {feedback.map((item, i) => {
        const config = SEVERITY_CONFIG[item.severity] || SEVERITY_CONFIG.low;
        return (
          <div
            key={i}
            className="feedback-card"
            style={{ borderLeftColor: config.color }}
          >
            <div className="feedback-header">
              <span className="feedback-category">{item.category}</span>
              <span
                className="feedback-severity"
                style={{ color: config.color, background: config.bg, border: `1px solid ${config.border}` }}
              >
                {config.label}
              </span>
              <span className="feedback-score">Score: {item.score}/100</span>
            </div>
            <p className="feedback-message">{item.message}</p>
            <div className="feedback-correction">
              <span className="correction-label">Correction →</span>
              <span className="correction-text">{item.correction}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
