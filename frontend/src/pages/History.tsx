import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getHistory } from "../api/client";
import type { HistoryItem } from "../types";

const PAGE_SIZE = 10;

function scoreClass(score: number): string {
  if (score >= 85) return "history-score-good";
  if (score >= 60) return "history-score-warn";
  return "history-score-bad";
}

export default function HistoryPage() {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [total, setTotal] = useState(0);
  const [skip, setSkip] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    getHistory(skip, PAGE_SIZE)
      .then((data) => {
        setItems(data.items);
        setTotal(data.total);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load history."))
      .finally(() => setLoading(false));
  }, [skip]);

  return (
    <div className="history-page">
      <h2>Analysis History</h2>

      {error && <div className="error-banner">{error}</div>}

      {loading ? (
        <div className="page-loading">Loading history...</div>
      ) : items.length === 0 ? (
        <div className="empty-state">
          <p>No analyses yet.</p>
          <Link className="btn-primary" to="/">
            Run your first analysis
          </Link>
        </div>
      ) : (
        <>
          <table className="history-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Language</th>
                <th>Filename</th>
                <th>Snippet</th>
                <th>Score</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id}>
                  <td>{new Date(item.created_at).toLocaleString()}</td>
                  <td>{item.language}</td>
                  <td>{item.filename ?? "-"}</td>
                  <td className="history-snippet">
                    <code>{item.snippet}</code>
                  </td>
                  <td>
                    <span className={`history-score-badge ${scoreClass(item.overall_score)}`}>
                      {Math.round(item.overall_score)}
                    </span>
                  </td>
                  <td>
                    <Link to={`/analysis/${item.id}`}>View</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="pagination">
            <button disabled={skip === 0} onClick={() => setSkip(Math.max(0, skip - PAGE_SIZE))}>
              Previous
            </button>
            <span>
              {skip + 1}-{Math.min(skip + PAGE_SIZE, total)} of {total}
            </span>
            <button disabled={skip + PAGE_SIZE >= total} onClick={() => setSkip(skip + PAGE_SIZE)}>
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
}
