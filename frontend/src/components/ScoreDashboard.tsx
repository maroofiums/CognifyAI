import type { ScoreBreakdown } from "../types";

interface ScoreDashboardProps {
  score: ScoreBreakdown;
}

const SCORE_LABELS: { key: keyof ScoreBreakdown; label: string }[] = [
  { key: "correctness", label: "Correctness" },
  { key: "readability", label: "Readability" },
  { key: "security", label: "Security" },
  { key: "performance", label: "Performance" },
  { key: "documentation", label: "Documentation" },
];

function scoreColor(value: number): string {
  if (value >= 85) return "var(--score-good)";
  if (value >= 60) return "var(--score-warn)";
  return "var(--score-bad)";
}

/** Visual dashboard summarizing the AI score breakdown (0-100 each). */
export default function ScoreDashboard({ score }: ScoreDashboardProps) {
  return (
    <div className="score-dashboard">
      <div className="score-overall" style={{ borderColor: scoreColor(score.overall) }}>
        <div className="score-overall-value" style={{ color: scoreColor(score.overall) }}>
          {Math.round(score.overall)}
        </div>
        <div className="score-overall-label">Overall Score</div>
      </div>

      <div className="score-bars">
        {SCORE_LABELS.map(({ key, label }) => {
          const value = score[key];
          return (
            <div className="score-bar-row" key={key}>
              <div className="score-bar-label">
                <span>{label}</span>
                <span>{Math.round(value)}</span>
              </div>
              <div className="score-bar-track">
                <div
                  className="score-bar-fill"
                  style={{ width: `${value}%`, backgroundColor: scoreColor(value) }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
