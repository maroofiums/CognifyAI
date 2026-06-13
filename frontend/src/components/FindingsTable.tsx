import type { BugItem, SecurityIssueItem } from "../types";

interface FindingsTableProps {
  title: string;
  items: (BugItem | SecurityIssueItem)[];
  emptyMessage: string;
}

const SEVERITY_CLASS: Record<string, string> = {
  low: "severity-low",
  medium: "severity-medium",
  high: "severity-high",
};

/** Renders a list of bug / security findings with line numbers, severity and fixes. */
export default function FindingsTable({ title, items, emptyMessage }: FindingsTableProps) {
  return (
    <div className="findings-card">
      <h3>{title}</h3>
      {items.length === 0 ? (
        <p className="findings-empty">{emptyMessage}</p>
      ) : (
        <ul className="findings-list">
          {items.map((item, idx) => (
            <li key={idx} className="findings-item">
              <div className="findings-item-header">
                <span className="findings-line">Line {item.line}</span>
                <span className={`severity-badge ${SEVERITY_CLASS[item.severity] ?? ""}`}>
                  {item.severity.toUpperCase()}
                </span>
              </div>
              <p className="findings-issue">{item.issue}</p>
              <p className="findings-fix">
                <strong>Fix:</strong> {item.fix}
              </p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
