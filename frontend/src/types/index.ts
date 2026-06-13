// Type definitions mirroring the backend Pydantic schemas
// (app/schemas/analysis.py, app/schemas/response.py)

export type Severity = "low" | "medium" | "high";

export interface BugItem {
  line: number;
  issue: string;
  severity: Severity;
  fix: string;
}

export interface SecurityIssueItem {
  line: number;
  issue: string;
  severity: Severity;
  fix: string;
}

export interface Complexity {
  time: string;
  space: string;
}

export interface ScoreBreakdown {
  correctness: number;
  readability: number;
  security: number;
  performance: number;
  documentation: number;
  overall: number;
}

export interface AnalysisResult {
  bugs: BugItem[];
  security_issues: SecurityIssueItem[];
  complexity: Complexity;
  optimized_code: string;
  docstring: string;
  score: ScoreBreakdown;
}

export interface AnalyzeResponse {
  id: string;
  created_at: string;
  result: AnalysisResult;
}

export interface AnalyzeRequest {
  code: string;
  language: string;
  filename?: string;
}

export interface HistoryItem {
  id: string;
  created_at: string;
  language: string;
  filename: string | null;
  overall_score: number;
  snippet: string;
}

export interface HistoryResponse {
  total: number;
  items: HistoryItem[];
}

export type StageStatus = "pending" | "running" | "done" | "error";

export interface StageState {
  name: string;
  status: StageStatus;
  detail?: string;
}

export const PIPELINE_STAGES: { key: string; label: string }[] = [
  { key: "syntax_checker", label: "Syntax Validation" },
  { key: "bug_detector", label: "Bug Detection" },
  { key: "security_scanner", label: "Security Scanning" },
  { key: "complexity_analyzer", label: "Complexity Analysis" },
  { key: "optimizer", label: "Code Optimization" },
  { key: "docstring_generator", label: "Docstring Generation" },
  { key: "scorer", label: "Scoring" },
];
