import Editor from "@monaco-editor/react";

interface CodeEditorProps {
  value: string;
  onChange?: (value: string) => void;
  language?: string;
  height?: string;
  readOnly?: boolean;
}

/** Thin wrapper around the Monaco editor with sensible defaults. */
export default function CodeEditor({
  value,
  onChange,
  language = "python",
  height = "420px",
  readOnly = false,
}: CodeEditorProps) {
  return (
    <div className="code-editor-wrapper">
      <Editor
        height={height}
        language={language}
        theme="vs-dark"
        value={value}
        onChange={(val) => onChange?.(val ?? "")}
        options={{
          readOnly,
          minimap: { enabled: false },
          fontSize: 14,
          scrollBeyondLastLine: false,
          wordWrap: "on",
          automaticLayout: true,
          tabSize: 4,
        }}
      />
    </div>
  );
}
