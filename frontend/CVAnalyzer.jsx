const { useState, useRef, useEffect } = React;

const API_URL = `http://${window.location.hostname || "127.0.0.1"}:5000/upload`;

// ─── Score Ring ────────────────────────────────────────────────────────────
function ScoreRing({ score }) {
  const circumference = 314;
  const offset = circumference - (score / 100) * circumference;
  const color =
    score >= 70 ? "#4ade80" : score >= 45 ? "#facc15" : "#f87171";

  return (
    <div style={{ position: "relative", width: 120, height: 120 }}>
      <svg viewBox="0 0 120 120" width="120" height="120">
        <circle cx="60" cy="60" r="50" fill="none" stroke="#1a1a2e" strokeWidth="10" />
        <circle
          cx="60" cy="60" r="50" fill="none"
          stroke={color} strokeWidth="10"
          strokeDasharray="314"
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform="rotate(-90 60 60)"
          style={{ transition: "stroke-dashoffset 1.4s cubic-bezier(0.22,1,0.36,1)" }}
        />
      </svg>
      <div style={{
        position: "absolute", inset: 0,
        display: "flex", alignItems: "center", justifyContent: "center",
        fontFamily: "'Syne', sans-serif", fontSize: 28, fontWeight: 800, color,
      }}>
        {score}
      </div>
    </div>
  );
}

// ─── Feedback Card ──────────────────────────────────────────────────────────
function FeedbackCard({ item, delay }) {
  const tagColors = {
    positive: "#4ade80",
    warning: "#facc15",
    negative: "#f87171",
  };
  const borderColors = {
    positive: "#4ade80",
    warning: "#facc15",
    negative: "#f87171",
  };
  const labels = {
    positive: "✓ Good",
    warning: "⚡ Tip",
    negative: "✗ Missing",
  };

  return (
    <div style={{
      background: "#0f1120",
      border: "1px solid #252840",
      borderLeft: `4px solid ${borderColors[item.type] || "#252840"}`,
      borderRadius: 16,
      padding: "20px 22px",
      animation: `fadeUp 0.4s ease ${delay}ms both`,
    }}>
      <div style={{
        fontSize: 10, fontWeight: 500, textTransform: "uppercase",
        letterSpacing: 1, marginBottom: 8, color: tagColors[item.type],
      }}>
        {labels[item.type] || "⚡ Tip"}
      </div>
      <div style={{ fontSize: 13, lineHeight: 1.6, color: "#e8eaf6" }}>
        {item.message}
      </div>
    </div>
  );
}

// ─── Main App ─────────────────────────────────────────────────────────────
function CVAnalyzer() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [results, setResults] = useState(null);
  const fileInputRef = useRef(null);
  const chartRef = useRef(null);
  const chartInstance = useRef(null);

  useEffect(() => {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap";
    document.head.appendChild(link);

    const style = document.createElement("style");
    style.textContent = `
      @keyframes fadeUp {
        from { opacity: 0; transform: translateY(20px); }
        to   { opacity: 1; transform: translateY(0); }
      }
      @keyframes spin {
        to { transform: rotate(360deg); }
      }
    `;
    document.head.appendChild(style);
  }, []);

  useEffect(() => {
    if (!results || !chartRef.current || typeof Chart === "undefined") {
      return;
    }

    const labels = Object.keys(results.breakdown || {});
    const data = Object.values(results.breakdown || {});

    if (chartInstance.current) {
      chartInstance.current.data.labels = labels;
      chartInstance.current.data.datasets[0].data = data;
      chartInstance.current.update();
      return;
    }

    chartInstance.current = new Chart(chartRef.current, {
      type: "radar",
      data: {
        labels,
        datasets: [
          {
            label: "CV category strength",
            data,
            backgroundColor: "rgba(124, 106, 255, 0.18)",
            borderColor: "#7c6aff",
            borderWidth: 2,
            pointBackgroundColor: "#ffffff",
            pointBorderColor: "#7c6aff",
            pointHoverBackgroundColor: "#ffffff",
            pointHoverBorderColor: "#7c6aff",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            beginAtZero: true,
            suggestedMin: 0,
            suggestedMax: 100,
            ticks: {
              stepSize: 20,
              color: "#a8adcc",
            },
            pointLabels: {
              color: "#e8eaf6",
              font: {
                size: 12,
              },
            },
            grid: {
              color: "rgba(124, 106, 255, 0.18)",
            },
            angleLines: {
              color: "rgba(124, 106, 255, 0.12)",
            },
          },
        },
        plugins: {
          legend: {
            display: false,
          },
        },
      },
    });
  }, [results]);

  useEffect(() => {
    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
        chartInstance.current = null;
      }
    };
  }, []);

  function handleFile(file) {
    setError("");
    if (file.type !== "application/pdf") {
      setError("Only PDF files are accepted.");
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setError("File size must be under 10MB.");
      return;
    }
    setSelectedFile(file);
  }

  function resetUpload() {
    setSelectedFile(null);
    setError("");
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  async function handleAnalyze() {
    if (!selectedFile) return;
    setLoading(true);
    setError("");

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch(API_URL, { method: "POST", body: formData });
      const text = await response.text();
      let data = null;

      if (text) {
        try {
          data = JSON.parse(text);
        } catch (parseError) {
          data = null;
        }
      }

      if (!response.ok) {
        const message = data?.error || `Server error: ${response.status}`;
        throw new Error(message);
      }

      if (!data) {
        throw new Error("Unexpected server response received.");
      }

      setResults(data);
    } catch (err) {
      setError(
        err.message || "Failed to connect to the backend. Make sure the Flask server is running on port 5000."
      );
    } finally {
      setLoading(false);
    }
  }

  function handleReset() {
    setResults(null);
    resetUpload();
  }

  const baseStyle = {
    fontFamily: "'DM Mono', monospace",
    background: "#07080f",
    color: "#e8eaf6",
    minHeight: "100vh",
    overflowX: "hidden",
    position: "relative",
  };

  const status = results
    ? results.score >= 70 ? "✅ Strong" : results.score >= 45 ? "⚠️ Average" : "❌ Needs Work"
    : "—";

  return (
    <div style={baseStyle}>
      <div style={{
        position: "fixed", inset: 0,
        backgroundImage: "linear-gradient(rgba(124,106,255,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(124,106,255,0.04) 1px, transparent 1px)",
        backgroundSize: "48px 48px",
        pointerEvents: "none", zIndex: 0,
      }} />

      <header style={{
        position: "relative", zIndex: 10,
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "24px 48px", borderBottom: "1px solid #252840",
      }}>
        <div style={{ fontFamily: "'Syne', sans-serif", fontSize: 22, fontWeight: 800, letterSpacing: -0.5 }}>
          CV<span style={{ color: "#7c6aff" }}>Analyzer</span>
        </div>
        <div style={{
          fontSize: 11, fontWeight: 500, letterSpacing: 1, textTransform: "uppercase",
          background: "rgba(124,106,255,0.12)", color: "#7c6aff",
          border: "1px solid rgba(124,106,255,0.25)", padding: "4px 12px", borderRadius: 100,
        }}>
          Phase 1 · Demo
        </div>
      </header>

      <main style={{ position: "relative", zIndex: 5, maxWidth: 780, margin: "0 auto", padding: "64px 24px 48px" }}>
        <section style={{ textAlign: "center", marginBottom: 48 }}>
          <h1 style={{
            fontFamily: "'Syne', sans-serif",
            fontSize: "clamp(36px, 6vw, 64px)",
            fontWeight: 800, lineHeight: 1.1, letterSpacing: -2, marginBottom: 16,
          }}>
            Analyze Your<br />
            <em style={{
              fontStyle: "normal",
              background: "linear-gradient(135deg, #7c6aff, #ff6a8e)",
              WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
            }}>
              Resume Instantly
            </em>
          </h1>
          <p style={{ color: "#6b6f9e", fontSize: 14, lineHeight: 1.7, maxWidth: 520, margin: "0 auto" }}>
            Upload your CV in PDF format and get a structured score with actionable feedback — powered by rule-based analysis.
          </p>
        </section>

        {!results && (
          <section style={{
            background: "#0f1120", border: "1px solid #252840",
            borderRadius: 24, padding: 32,
            display: "flex", flexDirection: "column", gap: 20,
          }}>
            {!selectedFile ? (
              <div
                onClick={() => fileInputRef.current?.click()}
                onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
                onDragLeave={() => setDragging(false)}
                onDrop={(e) => {
                  e.preventDefault(); setDragging(false);
                  if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]);
                }}
                style={{
                  border: `2px dashed ${dragging ? "#7c6aff" : "#252840"}`,
                  borderRadius: 16, padding: "48px 24px", textAlign: "center",
                  cursor: "pointer",
                  background: dragging ? "rgba(124,106,255,0.06)" : "transparent",
                  transition: "all 0.25s ease",
                  display: "flex", flexDirection: "column", alignItems: "center", gap: 10,
                  color: dragging ? "#e8eaf6" : "#6b6f9e",
                }}>
                <div style={{
                  width: 56, height: 56, background: "rgba(124,106,255,0.1)",
                  borderRadius: 14, display: "flex", alignItems: "center",
                  justifyContent: "center", color: "#7c6aff", marginBottom: 4,
                }}>
                  <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                    <path d="M24 4L24 32M24 4L14 14M24 4L34 14" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M6 36V40C6 42.2 7.8 44 10 44H38C40.2 44 42 42.2 42 40V36" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"/>
                  </svg>
                </div>
                <p style={{ fontFamily: "'Syne', sans-serif", fontSize: 18, fontWeight: 700, color: "#e8eaf6" }}>
                  Drop your CV here
                </p>
                <p style={{ fontSize: 12, color: "#6b6f9e" }}>or click to browse — PDF only</p>
                <input ref={fileInputRef} type="file" accept=".pdf" hidden onChange={(e) => { if (e.target.files[0]) handleFile(e.target.files[0]); }} />
              </div>
            ) : (
              <div style={{
                background: "#161829", border: "1px solid #252840",
                borderRadius: 16, padding: "14px 20px",
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                  <span style={{ fontSize: 20 }}>📄</span>
                  <span style={{
                    flex: 1, fontSize: 13, color: "#e8eaf6",
                    whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis",
                  }}>
                    {selectedFile.name}
                  </span>
                  <button onClick={resetUpload} style={{
                    background: "none", border: "none", color: "#6b6f9e",
                    cursor: "pointer", fontSize: 14, padding: "4px 8px", borderRadius: 6,
                  }}>✕</button>
                </div>
              </div>
            )}

            <button
              onClick={handleAnalyze}
              disabled={!selectedFile || loading}
              style={{
                background: "linear-gradient(135deg, #7c6aff, #9b6fff)",
                color: "#fff", border: "none", borderRadius: 16,
                padding: "16px 32px",
                fontFamily: "'Syne', sans-serif", fontSize: 16, fontWeight: 700,
                cursor: selectedFile && !loading ? "pointer" : "not-allowed",
                opacity: !selectedFile || loading ? 0.4 : 1,
                display: "flex", alignItems: "center", justifyContent: "center", gap: 12,
                transition: "all 0.25s ease",
              }}>
              {loading ? (
                <>
                  <div style={{
                    width: 18, height: 18, border: "2px solid rgba(255,255,255,0.3)",
                    borderTopColor: "#fff", borderRadius: "50%",
                    animation: "spin 0.7s linear infinite",
                  }} />
                  Analyzing...
                </>
              ) : "Analyze CV"}
            </button>

            {error && (
              <p style={{ fontSize: 12, color: "#f87171", textAlign: "center" }}>{error}</p>
            )}
          </section>
        )}

        {results && (
          <section style={{ marginTop: 0, animation: "fadeUp 0.5s ease forwards" }}>
            <div style={{
              display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 28,
            }}>
              <h2 style={{ fontFamily: "'Syne', sans-serif", fontSize: 26, fontWeight: 800, letterSpacing: -0.5 }}>
                Analysis Results
              </h2>
              <button onClick={handleReset} style={{
                background: "#161829", border: "1px solid #252840", color: "#6b6f9e",
                borderRadius: 10, padding: "8px 16px", fontFamily: "'DM Mono', monospace",
                fontSize: 12, cursor: "pointer",
              }}>
                ↩ Analyze Another
              </button>
            </div>

            <div style={{
              display: "grid", gridTemplateColumns: "200px 1fr", gap: 20, marginBottom: 24,
            }}>
              <div style={{
                background: "#0f1120", border: "1px solid #252840",
                borderRadius: 20, padding: "28px 20px",
                display: "flex", flexDirection: "column", alignItems: "center", gap: 12,
              }}>
                <ScoreRing score={results.score || 0} />
                <div style={{ fontSize: 12, color: "#6b6f9e", textTransform: "uppercase", letterSpacing: 1 }}>
                  Overall Score
                </div>
              </div>

              <div style={{
                background: "#0f1120", border: "1px solid #252840",
                borderRadius: 20, padding: "24px 28px",
                display: "flex", flexDirection: "column", justifyContent: "center", gap: 16,
              }}>
                {[
                  ["Status", status],
                  ["Sections Found", results.sections_found ?? "—"],
                  ["Skills Detected", results.skills_count ?? "—"],
                  ["Word Count", results.word_count ?? "—"],
                ].map(([label, val], i, arr) => (
                  <div key={label} style={{
                    display: "flex", alignItems: "center", justifyContent: "space-between",
                    borderBottom: i < arr.length - 1 ? "1px solid #252840" : "none",
                    paddingBottom: i < arr.length - 1 ? 12 : 0,
                  }}>
                    <span style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: 1, color: "#6b6f9e" }}>
                      {label}
                    </span>
                    <span style={{ fontFamily: "'Syne', sans-serif", fontSize: 14, fontWeight: 600 }}>
                      {val}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div style={{
              background: "#0f1120",
              border: "1px solid #252840",
              borderRadius: 20,
              padding: 20,
              marginBottom: 24,
              minHeight: 320,
            }}>
              <div style={{ fontSize: 13, color: "#e8eaf6", marginBottom: 16, fontWeight: 700 }}>
                Category radar chart
              </div>
              <div style={{ width: "100%", height: 260 }}>
                <canvas ref={chartRef} />
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
              {(results.feedback || []).map((item, i) => (
                <FeedbackCard key={i} item={item} delay={i * 80} />
              ))}
            </div>
          </section>
        )}
      </main>

      <footer style={{
        position: "relative", zIndex: 5, textAlign: "center",
        padding: 24, borderTop: "1px solid #252840",
        color: "#6b6f9e", fontSize: 11, letterSpacing: 0.5,
      }}>
        CV Analyzer · Phase 1 Demo · Built with Flask + React
      </footer>
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<CVAnalyzer />);
