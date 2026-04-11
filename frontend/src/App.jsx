import { useState } from "react";
import VideoUploader from "./components/VideoUploader";
import AnalysisResults from "./components/AnalysisResults";
import "./index.css";

export default function App() {
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadedVideo, setUploadedVideo] = useState(null);

  const handleAnalysis = async (file, activity) => {
    setLoading(true);
    setError(null);
    setAnalysisData(null);
    setUploadedVideo(URL.createObjectURL(file));

    const formData = new FormData();
    formData.append("video", file);
    formData.append("activity", activity);

    try {
      const res = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Analysis failed");
      }

      const data = await res.json();
      setAnalysisData(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-inner">
          <div className="logo">
            <span className="logo-mark">⬡</span>
            <span className="logo-text">KINETIC<em>IQ</em></span>
          </div>
          <p className="header-sub">Biomechanics </p>
        </div>
      </header>

      <main className="main">
        {!analysisData && !loading && (
          <VideoUploader onAnalyze={handleAnalysis} error={error} />
        )}

        {loading && (
          <div className="loading-screen">
            <div className="loading-spinner" />
            <p className="loading-label">Analyzing</p>
            <p className="loading-sub"></p>
          </div>
        )}

        {analysisData && (
          <>
            <AnalysisResults data={analysisData} videoUrl={uploadedVideo} />
            <button
              className="btn-secondary reset-btn"
              onClick={() => {
                setAnalysisData(null);
                setUploadedVideo(null);
                setError(null);
              }}
            >
              ← Analyze Another Video
            </button>
          </>
        )}
      </main>
    </div>
  );
}
