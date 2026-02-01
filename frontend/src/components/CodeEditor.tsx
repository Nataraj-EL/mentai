"use client"
import { useState, useRef, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import { motion } from 'framer-motion';
import axios from 'axios';

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
      const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/execute-code/`, {
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
      className="bg-white rounded-lg shadow-lg overflow-hidden"
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold">{title}</h3>
            <p className="text-blue-100 text-sm">{(language || '').toUpperCase()}</p>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-2 hover:bg-white/20 rounded-lg transition-colors"
            >
              {isExpanded ? 'Collapse' : 'Expand'}
            </button>
          </div>
        </div>
      </div>

      {/* Explanation */}
      <div className="p-4 bg-gray-50 border-b">
        <p className="text-gray-700">{explanation}</p>
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
      <div className="p-4 bg-gray-50 border-t">
        <div className="flex items-center justify-between">
          {/* Only show Run/Clear buttons if not readOnly */}
          {!readOnly && (
            <div className="flex gap-2">
              <button
                onClick={runCode}
                disabled={isLoading}
                className="px-4 py-1.5 bg-green-600 text-white rounded text-sm font-medium hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
              >
                {isLoading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Running...
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Run Code
                  </>
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
          className="p-4 bg-gray-900 text-green-400 font-mono text-sm border-t"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="font-semibold">Output:</span>
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
