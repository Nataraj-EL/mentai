"use client"
import { useState, useRef, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import { motion } from 'framer-motion';
import axios from 'axios';
import { API } from '../utils/api';

interface CodeEditorProps {
  code: string;
  language: string;
  title: string;
  explanation: string;
  topic: string; // Add topic prop
  onCodeChange?: (code: string) => void;
  readOnly?: boolean;
}

const CodeEditor: React.FC<CodeEditorProps> = ({
  code,
  language,
  title,
  explanation,
  topic, // Destructure topic
  onCodeChange,
  readOnly = false
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [output, setOutput] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const editorRef = useRef<import('monaco-editor').editor.IStandaloneCodeEditor | null>(null);

  const handleEditorDidMount = (editor: import('monaco-editor').editor.IStandaloneCodeEditor) => {
    editorRef.current = editor;
  };

  // Sync editor content when code prop changes
  useEffect(() => {
    if (editorRef.current && code) {
      const currentValue = editorRef.current.getValue();
      if (currentValue !== code) {
        editorRef.current.setValue(code);
      }
    }
  }, [code]);


  const runCode = async () => {
    if (!editorRef.current) return;

    setIsLoading(true);
    const currentCode = editorRef.current.getValue();

    try {
      // Use backend API for all languages (Judge0)
      const response = await API.post(`/execute-code/`, {
        code: currentCode,
        language: language,
        topic: topic // Include topic in payload
      });
      const data = response.data;
      let outputText = '';
      if (data.stdout) outputText += data.stdout;
      if (data.stderr) outputText += `\n[stderr]:\n${data.stderr}`;
      if (data.compile_output) outputText += `\n[compile_output]:\n${data.compile_output}`;
      if (data.status && data.status.description && data.status.description !== "Accepted")
        outputText += `\n[status]: ${data.status.description}`;
      if (!outputText.trim()) outputText = 'No output';
      setOutput(outputText);
    } catch (error: unknown) {
      if (axios.isAxiosError(error) && error.response?.data?.result) {
        setOutput(error.response.data.result);
      } else if (axios.isAxiosError(error) && error.response?.data?.error) {
        setOutput(`Error: ${error.response.data.error}`);
      } else if (error instanceof Error) {
        setOutput(`Error: ${error.message || 'Code execution failed'}`);
      } else {
        setOutput(`Error: Code execution failed`);
      }
    } finally {
      setIsLoading(false); // Use isLoading for button state
    }
  };



  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden"
    >
      {/* Header */}
      <div className="bg-white px-4 py-3 border-b border-gray-150">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-[#111827]">{title || "Interactive Code Sandbox"}</h3>
            <p className="text-[11px] text-gray-400 font-mono font-medium">{(language || '').toUpperCase()}</p>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="px-2.5 py-1 text-xs font-semibold text-gray-600 hover:text-gray-900 border border-gray-200 rounded hover:bg-gray-50 transition-colors"
            >
              {isExpanded ? 'Collapse' : 'Expand'}
            </button>
          </div>
        </div>
      </div>

      {/* Explanation */}
      <div className="p-4 bg-gray-50 border-b border-gray-200">
        <p className="text-sm text-gray-600 leading-relaxed">{explanation}</p>
      </div>

      {/* Code Editor */}
      <div className={`transition-all duration-300 ${isExpanded ? 'h-96' : 'h-64'}`}>
        <Editor
          height="100%"
          defaultLanguage={language || 'plaintext'}
          defaultValue={code}
          theme="vs-dark"
          onMount={handleEditorDidMount}
          onChange={(value) => onCodeChange?.(value || '')}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            roundedSelection: false,
            scrollBeyondLastLine: false,
            automaticLayout: true,
            readOnly: readOnly, // Apply readOnly prop here
          }}
        />
      </div>

      {/* Controls */}
      <div className="p-4 bg-gray-50 border-t border-gray-200">
        <div className="flex items-center justify-between">
          {/* Only show Run/Clear buttons if not readOnly */}
          {!readOnly && (
            <div className="flex gap-2">
              <button
                onClick={runCode}
                disabled={isLoading}
                className="px-4 py-1.5 bg-[#06B6D4] text-[#111827] rounded text-sm font-semibold hover:bg-[#06b6d4]/90 disabled:opacity-50 flex items-center gap-2 shadow-sm transition-all"
              >
                {isLoading ? (
                  <>
                    <div className="w-3.5 h-3.5 border-2 border-[#111827]/30 border-t-[#111827] rounded-full animate-spin" />
                    <span>Running...</span>
                  </>
                ) : (
                  <span>Run Code</span>
                )}
              </button>

              <button
                onClick={() => setOutput('')}
                className="px-3 py-1.5 text-gray-500 hover:text-gray-700 text-sm font-medium"
              >
                Clear
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Output */}
      {output && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="p-4 bg-[#111827] text-green-400 font-mono text-sm border-t border-gray-200"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="font-semibold text-gray-300">Output:</span>
            <button
              onClick={() => setOutput('')}
              className="text-gray-400 hover:text-white"
            >
              ✕
            </button>
          </div>
          <pre className="whitespace-pre-wrap">{output}</pre>
        </motion.div>
      )}
    </motion.div>
  );
}
export default CodeEditor;
