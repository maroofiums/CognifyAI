import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { analyzeCodeStream } from "../api/client";
import CodeEditor from "../components/CodeEditor";
import StatusStream from "../components/StatusStream";
import { useAnalysis } from "../context/AnalysisContext";
import type { StageStatus } from "../types";

const DEFAULT_CODE = `def calculate_total(items, discount=None):
    if discount == None:
        discount = 0

    total = 0
    for item in items:
        total = total + item["price"] * item["quantity"]

    try:
        total = total - (total * discount)
    except:
        pass

    return total
`;

const LANGUAGES = ["python", "javascript", "typescript", "java", "go"];

export default function HomePage() {
  const navigate = useNavigate();
  const { setCurrentAnalysis, setCurrentCode, setCurrentLanguage, currentLanguage } = useAnalysis();

  const [code, setCode] = useState<string>(DEFAULT_CODE);
  const [language, setLanguage] = useState<string>(currentLanguage);
  const [filename, setFilename] = useState<string>("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stages, setStages] = useState<Record<string, StageStatus>>({});

  async function handleAnalyze() {
    if (!code.trim()) {
      setError("Please paste some code to analyze.");
      return;
    }

    setError(null);
    setIsAnalyzing(true);
    setStages({});

    try {
      await analyzeCodeStream(
        { code, language, filename: filename || undefined },
        (stage) => {
          setStages((prev) => ({ ...prev, [stage.name]: stage.status }));
        },
        (result) => {
          setCurrentAnalysis(result);
          setCurrentCode(code);
          setCurrentLanguage(language);
          navigate("/results");
        }
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed. Is the backend running?");
    } finally {
      setIsAnalyzing(false);
    }
  }

  return (
    <div className="home-page">
      <section className="hero">
        <h1>AI Code Optimiser</h1>
        <p>
          Paste your source code below. CognifyAI runs a sequential pipeline - syntax validation, bug
          detection, security scanning, complexity analysis, optimization and documentation - and
          returns a structured report with an actionable score.
        </p>
      </section>

      <section className="editor-toolbar">
        <div className="toolbar-controls">
          <label>
            Language
            <select value={language} onChange={(e) => setLanguage(e.target.value)}>
              {LANGUAGES.map((lang) => (
                <option key={lang} value={lang}>
                  {lang}
                </option>
              ))}
            </select>
          </label>
          <label>
            Filename (optional)
            <input
              type="text"
              placeholder="e.g. checkout.py"
              value={filename}
              onChange={(e) => setFilename(e.target.value)}
            />
          </label>
        </div>
        <button className="btn-primary" onClick={handleAnalyze} disabled={isAnalyzing}>
          {isAnalyzing ? "Analyzing..." : "Analyze Code"}
        </button>
      </section>

      {error && <div className="error-banner">{error}</div>}

      <section className="editor-and-status">
        <CodeEditor value={code} onChange={setCode} language={language} />
        {isAnalyzing && (
          <div className="status-panel">
            <h3>Pipeline Progress</h3>
            <StatusStream stages={stages} />
          </div>
        )}
      </section>
    </div>
  );
}
