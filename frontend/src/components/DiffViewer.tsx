import { DiffEditor } from "@monaco-editor/react";

interface DiffViewerProps {
  original: string;
  modified: string;
  language?: string;
  height?: string;
}

/** Side-by-side diff between the original and AI-optimized code. */
export default function DiffViewer({ original, modified, language = "python", height = "480px" }: DiffViewerProps) {
  return (
    <div className="diff-viewer-wrapper">
      <DiffEditor
        height={height}
        language={language}
        original={original}
        modified={modified}
        theme="vs-dark"
        options={{
          readOnly: true,
          renderSideBySide: true,
          minimap: { enabled: false },
          fontSize: 13,
          automaticLayout: true,
          wordWrap: "on",
        }}
      />
    </div>
  );
}
