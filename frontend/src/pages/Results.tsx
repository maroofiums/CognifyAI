import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getAnalysis } from "../api/client";
import DiffViewer from "../components/DiffViewer";
import FindingsTable from "../components/FindingsTable";
import ScoreDashboard from "../components/ScoreDashboard";
import { useAnalysis } from "../context/AnalysisContext";
import type { AnalyzeResponse } from "../types";

export default function ResultsPage() {
  const { id } = useParams<{ id: string }>();
  const { currentAnalysis, currentCode, currentLanguage } = useAnalysis();

  const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(
    id ? null : currentAnalysis
  );
  const [originalCode, setOriginalCode] = useState<string>(currentCode);
  const [loading, setLoading] = useState<boolean>(!!id);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;

    setLoading(true);
    getAnalysis(id)
      .then((data) => {
        setAnalysis(data);
        // Historical records don't return the original source separately from
        // this endpoint in a dedicated field for the diff's "before" side, so
        // fall back to the optimized code if no original is cached locally.
        setOriginalCode(currentCode || data.result.optimized_code);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load analysis."))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  if (loading) {
    return <div className="page-loading">Loading analysis...</div>;
  }

  if (error) {
    return <div className="error-banner">{error}</div>;
  }

  if (!analysis) {
    return (
      <div className="empty-state">
        <p>No analysis to display yet.</p>
        <Link className="btn-primary" to="/">
          Analyze some code
        </Link>
      </div>
    );
  }

  const { result } = analysis;

  return (
    <div className="results-page">
      <section className="results-header">
        <div>
          <h2>Analysis Results</h2>
          <p className="results-meta">
            ID: <code>{analysis.id}</code> &middot;{" "}
            {new Date(analysis.created_at).toLocaleString()}
          </p>
        </div>
        <ScoreDashboard score={result.score} />
      </section>

      <section className="complexity-card">
        <h3>Complexity</h3>
        <div className="complexity-values">
          <div>
            <span className="complexity-label">Time</span>
            <span className="complexity-value">{result.complexity.time}</span>
          </div>
          <div>
            <span className="complexity-label">Space</span>
            <span className="complexity-value">{result.complexity.space}</span>
          </div>
        </div>
      </section>

      <section className="findings-grid">
        <FindingsTable title="Bugs" items={result.bugs} emptyMessage="No bugs detected. 🎉" />
        <FindingsTable
          title="Security Issues"
          items={result.security_issues}
          emptyMessage="No security issues detected. 🔒"
        />
      </section>

      <section className="docstring-card">
        <h3>Generated Docstring</h3>
        <pre>{result.docstring}</pre>
      </section>

      <section className="diff-card">
        <h3>Original vs. Optimized Code</h3>
        <DiffViewer original={originalCode} modified={result.optimized_code} language={currentLanguage} />
      </section>
    </div>
  );
}
