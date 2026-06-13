import { createContext, useContext, useState, type ReactNode } from "react";
import type { AnalyzeResponse } from "../types";

interface AnalysisContextValue {
  /** The most recently completed analysis, shown on the Results page. */
  currentAnalysis: AnalyzeResponse | null;
  setCurrentAnalysis: (analysis: AnalyzeResponse | null) => void;

  /** The source code that produced `currentAnalysis`, used for diffing. */
  currentCode: string;
  setCurrentCode: (code: string) => void;

  currentLanguage: string;
  setCurrentLanguage: (language: string) => void;
}

const AnalysisContext = createContext<AnalysisContextValue | undefined>(undefined);

export function AnalysisProvider({ children }: { children: ReactNode }) {
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalyzeResponse | null>(null);
  const [currentCode, setCurrentCode] = useState<string>("");
  const [currentLanguage, setCurrentLanguage] = useState<string>("python");

  return (
    <AnalysisContext.Provider
      value={{
        currentAnalysis,
        setCurrentAnalysis,
        currentCode,
        setCurrentCode,
        currentLanguage,
        setCurrentLanguage,
      }}
    >
      {children}
    </AnalysisContext.Provider>
  );
}

export function useAnalysis(): AnalysisContextValue {
  const ctx = useContext(AnalysisContext);
  if (!ctx) {
    throw new Error("useAnalysis must be used within an AnalysisProvider");
  }
  return ctx;
}
