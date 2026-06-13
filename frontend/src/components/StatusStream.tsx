import { PIPELINE_STAGES, type StageState, type StageStatus } from "../types";

interface StatusStreamProps {
  stages: Record<string, StageStatus>;
}

const STATUS_ICON: Record<StageStatus, string> = {
  pending: "○",
  running: "◐",
  done: "●",
  error: "✕",
};

/** Real-time pipeline progress indicator, updated as SSE-like NDJSON events arrive. */
export default function StatusStream({ stages }: StatusStreamProps) {
  return (
    <ul className="status-stream">
      {PIPELINE_STAGES.filter((s) => s.key !== "scorer").map((stage) => {
        const status: StageStatus = stages[stage.key] ?? "pending";
        return (
          <li key={stage.key} className={`status-item status-${status}`}>
            <span className="status-icon">{STATUS_ICON[status]}</span>
            <span className="status-label">{stage.label}</span>
          </li>
        );
      })}
    </ul>
  );
}

export type { StageState };
