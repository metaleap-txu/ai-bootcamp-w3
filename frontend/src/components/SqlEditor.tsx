/**
 * SQL Editor component using Monaco Editor.
 * 
 * Features:
 * - SQL syntax highlighting with PostgreSQL dialect
 * - Keyboard shortcut: Cmd/Ctrl+Enter to execute query
 * - Automatic indentation and bracket matching
 * - Line numbers and minimap for large queries
 * - Dark theme optimized for code editing
 * 
 * Props:
 * - value: Current SQL text content
 * - onChange: Callback when SQL text changes
 * - onExecute: Callback when Cmd/Ctrl+Enter pressed
 * - height: Editor height (default: 300px)
 * - readOnly: Disable editing (default: false)
 */
import React, { useRef, useEffect } from 'react';
import Editor, { OnMount } from '@monaco-editor/react';
import type { editor } from 'monaco-editor';

interface SqlEditorProps {
  value: string;
  onChange: (value: string) => void;
  onExecute?: () => void;
  readOnly?: boolean;
  height?: string;
  errors?: Array<{ line: number; message: string }>;
}

export const SqlEditor: React.FC<SqlEditorProps> = ({
  value,
  onChange,
  onExecute,
  readOnly = false,
  height = '300px',
  errors = [],
}) => {
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);

  const handleEditorDidMount: OnMount = (editor, monaco) => {
    editorRef.current = editor;

    // Add Cmd+Enter / Ctrl+Enter keybinding for execute
    if (onExecute) {
      editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
        onExecute();
      });
    }

    // Configure SQL language features
    monaco.languages.setLanguageConfiguration('sql', {
      comments: {
        lineComment: '--',
        blockComment: ['/*', '*/'],
      },
      brackets: [
        ['(', ')'],
        ['[', ']'],
      ],
      autoClosingPairs: [
        { open: '(', close: ')' },
        { open: '[', close: ']' },
        { open: "'", close: "'" },
        { open: '"', close: '"' },
      ],
    });
  };

  useEffect(() => {
    if (editorRef.current && errors.length > 0) {
      const monaco = (window as any).monaco;
      if (!monaco) return;

      const model = editorRef.current.getModel();
      if (!model) return;

      // Create error markers
      const markers = errors.map((error) => ({
        severity: monaco.MarkerSeverity.Error,
        startLineNumber: error.line,
        startColumn: 1,
        endLineNumber: error.line,
        endColumn: model.getLineMaxColumn(error.line),
        message: error.message,
      }));

      monaco.editor.setModelMarkers(model, 'sql-validation', markers);
    } else if (editorRef.current) {
      // Clear markers
      const monaco = (window as any).monaco;
      if (monaco) {
        const model = editorRef.current.getModel();
        if (model) {
          monaco.editor.setModelMarkers(model, 'sql-validation', []);
        }
      }
    }
  }, [errors]);

  return (
    <Editor
      height={height}
      defaultLanguage="sql"
      value={value}
      onChange={(newValue) => onChange(newValue || '')}
      onMount={handleEditorDidMount}
      options={{
        readOnly,
        minimap: { enabled: false },
        fontSize: 14,
        lineNumbers: 'on',
        renderLineHighlight: 'all',
        scrollBeyondLastLine: false,
        automaticLayout: true,
        tabSize: 2,
        wordWrap: 'on',
        quickSuggestions: true,
        suggestOnTriggerCharacters: true,
        acceptSuggestionOnEnter: 'on',
      }}
      theme="vs-dark"
    />
  );
};
