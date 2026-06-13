import axios from "axios";
import type {
  AnalyzeRequest,
  AnalyzeResponse,
  HistoryResponse,
  StageState,
} from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

/** POST /api/analyze - synchronous, non-streaming analysis. */
export async function analyzeCode(payload: AnalyzeRequest): Promise<AnalyzeResponse> {
  const response = await apiClient.post<AnalyzeResponse>("/analyze", payload);
  return response.data;
}

/** GET /api/history - paginated list of past analyses. */
export async function getHistory(skip = 0, limit = 20): Promise<HistoryResponse> {
  const response = await apiClient.get<HistoryResponse>("/history", {
    params: { skip, limit },
  });
  return response.data;
}

/** GET /api/analysis/{id} - fetch a single stored analysis. */
export async function getAnalysis(id: string): Promise<AnalyzeResponse> {
  const response = await apiClient.get<AnalyzeResponse>(`/analysis/${id}`);
  return response.data;
}

/**
 * POST /api/analyze/stream - real-time streaming analysis.
 *
 * Consumes the newline-delimited JSON stream emitted by the backend using
 * the Fetch Streams API and invokes `onStage` for each pipeline stage
 * status update, and `onResult` once the final result arrives.
 */
export async function analyzeCodeStream(
  payload: AnalyzeRequest,
  onStage: (stage: StageState) => void,
  onResult: (result: AnalyzeResponse) => void,
  signal?: AbortSignal
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/analyze/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal,
  });

  if (!response.ok || !response.body) {
    const text = await response.text().catch(() => "");
    throw new Error(`Analysis request failed (${response.status}): ${text}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (!line.trim()) continue;
      const event = JSON.parse(line) as
        | { type: "stage"; stage: string; status: string; detail?: string }
        | { type: "result"; data: AnalyzeResponse };

      if (event.type === "stage") {
        onStage({
          name: event.stage,
          status: event.status as StageState["status"],
          detail: event.detail,
        });
      } else if (event.type === "result") {
        onResult(event.data);
      }
    }
  }

  if (buffer.trim()) {
    const event = JSON.parse(buffer) as { type: "result"; data: AnalyzeResponse };
    if (event.type === "result") {
      onResult(event.data);
    }
  }
}
