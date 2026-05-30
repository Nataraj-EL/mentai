import { useState, useEffect } from 'react';
import { API } from '../src/utils/api';
import Editor from '@monaco-editor/react';

export default function DebugCoursePage() {
  const [course, setCourse] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [currentModule, setCurrentModule] = useState(0);

  useEffect(() => {
    const fetchCourse = async () => {
      try {
        console.log("Debug page: sending direct local API post request for 'Java'...");
        const res = await API.post('/generate-course/', {
          topic: 'Java'
        });
        console.log("Debug page: received API response status:", res.status);
        console.log("Debug page: received data keys:", Object.keys(res.data || {}));
        setCourse(res.data);
      } catch (err: any) {
        console.error("Debug page: API request failed:", err);
        setError(err.message || "Failed to fetch course data");
      } finally {
        setLoading(false);
      }
    };
    fetchCourse();
  }, []);

  if (loading) {
    return <div style={{ color: "black", padding: 20 }}>Loading raw debug page... Check browser console logs.</div>;
  }

  if (error) {
    return (
      <div style={{ color: "red", padding: 20 }}>
        <h2>Error loading course</h2>
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>Retry</button>
      </div>
    );
  }

  if (!course) {
    return <div style={{ color: "black", padding: 20 }}>No course returned from API.</div>;
  }

  const module = course.modules?.[currentModule];

  return (
    <div style={{ background: "#1a202c", color: "#f7fafc", padding: "20px", fontFamily: "monospace", minHeight: "100vh" }}>
      <h1 style={{ borderBottom: "2px solid #4a5568", paddingBottom: "10px" }}>MentAI Debug & Visual Verification Page</h1>
      
      <div style={{ display: "flex", gap: "20px", margin: "20px 0" }}>
        <div style={{ flex: 1, border: "1px solid #4a5568", padding: "15px", borderRadius: "8px", background: "#2d3748" }}>
          <h2>1. SELECT MODULE</h2>
          <select 
            value={currentModule} 
            onChange={(e) => setCurrentModule(parseInt(e.target.value))}
            style={{ padding: "8px", width: "100%", background: "#1a202c", color: "white", border: "1px solid #4a5568", borderRadius: "4px" }}
          >
            {course.modules?.map((m: any, idx: number) => (
              <option key={m.id} value={idx}>Module {idx + 1}: {m.name}</option>
            ))}
          </select>

          {module && (
            <div style={{ marginTop: "20px" }}>
              <h3>Active Module: {module.name}</h3>
              <p>Difficulty: {module.difficulty}</p>
              <p>Description: {module.description}</p>
            </div>
          )}
        </div>

        <div style={{ flex: 1, border: "1px solid #4a5568", padding: "15px", borderRadius: "8px", background: "#2d3748" }}>
          <h2>2. RAW API STATS</h2>
          <ul>
            <li>Course Title: {course.title}</li>
            <li>Topic Slug: {course.topic}</li>
            <li>Modules Count: {course.modules?.length || 0}</li>
            {module && (
              <>
                <li>Theory length: {module.theory?.length || 0}</li>
                <li>Mini Labs count: {module.mini_labs?.length || 0}</li>
                <li>Quizzes count: {module.quizzes?.length || 0}</li>
              </>
            )}
          </ul>
        </div>
      </div>

      <div style={{ border: "1px solid #4a5568", padding: "15px", borderRadius: "8px", margin: "20px 0", background: "#2d3748" }}>
        <h2>3. RAW STATE JSON PREVIEW (<pre style={{ display: "inline" }}>JSON.stringify</pre>)</h2>
        {module ? (
          <pre style={{ background: "#1a202c", padding: "10px", borderRadius: "4px", overflow: "auto", maxHeight: "300px", fontSize: "12px", border: "1px solid #4a5568" }}>
            {JSON.stringify({
              id: module.id,
              name: module.name,
              theory_exists: module.theory !== undefined,
              theory_length: module.theory?.length || 0,
              mini_labs: module.mini_labs,
              quizzes: module.quizzes,
              keys: Object.keys(module)
            }, null, 2)}
          </pre>
        ) : (
          <p>No active module selected.</p>
        )}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", margin: "20px 0" }}>
        
        {/* Left Side: Markdown Theory & Quizzes */}
        <div style={{ border: "1px solid #4a5568", padding: "15px", borderRadius: "8px", background: "#2d3748" }}>
          <h2>4. THEORY / EXPLANATION TEXT</h2>
          {module?.theory ? (
            <div style={{ background: "#1a202c", padding: "15px", borderRadius: "4px", maxHeight: "400px", overflowY: "auto", border: "1px solid #4a5568", whiteSpace: "pre-wrap" }}>
              {module.theory}
            </div>
          ) : (
            <p style={{ color: "#feb2b2" }}>❌ No theory content exists in module state.</p>
          )}

          <h2 style={{ marginTop: "30px" }}>5. QUIZZES (QUESTIONS & OPTIONS)</h2>
          {module?.quizzes && module.quizzes.length > 0 ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "15px", maxHeight: "400px", overflowY: "auto" }}>
              {module.quizzes.map((q: any, idx: number) => (
                <div key={q.id || idx} style={{ background: "#1a202c", padding: "12px", borderRadius: "4px", border: "1px solid #4a5568" }}>
                  <p style={{ fontWeight: "bold", margin: "0 0 8px 0" }}>Q{idx + 1}: {q.question}</p>
                  <ul style={{ paddingLeft: "20px", margin: 0 }}>
                    {q.options?.map((opt: string, i: number) => (
                      <li key={i} style={{ margin: "4px 0" }}>{opt}</li>
                    ))}
                  </ul>
                  <p style={{ color: "#9ae6b4", fontSize: "12px", margin: "8px 0 0 0" }}>Correct Answer: {q.correct_answer || q.answer}</p>
                  {q.explanation && <p style={{ color: "#a0aec0", fontSize: "12px", margin: "4px 0 0 0" }}>Explanation: {q.explanation}</p>}
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: "#feb2b2" }}>❌ No quizzes exist in module state.</p>
          )}
        </div>

        {/* Right Side: Monaco Editor & Labs */}
        <div style={{ border: "1px solid #4a5568", padding: "15px", borderRadius: "8px", background: "#2d3748" }}>
          <h2>6. MONACO COMPILER EDITOR</h2>
          <div style={{ height: "350px", border: "1px solid #4a5568", borderRadius: "4px", overflow: "hidden" }}>
            <Editor
              height="100%"
              defaultLanguage="java"
              value={
                module?.mini_labs?.[0]?.preloaded_code || 
                module?.preloaded_code || 
                `public class Main {\n    public static void main(String[] args) {\n        System.out.println("MentAI Standalone Test");\n    }\n}`
              }
              theme="vs-dark"
              options={{ minimap: { enabled: false } }}
            />
          </div>

          <h2 style={{ marginTop: "30px" }}>7. MINI LAB DETAILS</h2>
          {module?.mini_labs && module.mini_labs.length > 0 ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "15px" }}>
              {module.mini_labs.map((lab: any, idx: number) => (
                <div key={idx} style={{ background: "#1a202c", padding: "12px", borderRadius: "4px", border: "1px solid #4a5568" }}>
                  <h4 style={{ margin: "0 0 6px 0", color: "#63b3ed" }}>Lab {idx + 1}: {lab.title}</h4>
                  <p style={{ margin: "0 0 8px 0" }}>{lab.description}</p>
                  <pre style={{ background: "#2d3748", padding: "8px", fontSize: "11px", borderRadius: "4px", overflow: "auto" }}>
                    {lab.preloaded_code}
                  </pre>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: "#feb2b2" }}>❌ No mini labs exist in module state.</p>
          )}
        </div>

      </div>

      <div style={{ border: "1px solid #4a5568", padding: "15px", borderRadius: "8px", marginTop: "40px", background: "#2d3748" }}>
        <h2>8. COMPLETE RAW COURSE OBJECT JSON</h2>
        <pre style={{ background: "#1a202c", padding: "15px", borderRadius: "4px", overflow: "auto", maxHeight: "400px", fontSize: "11px", border: "1px solid #4a5568" }}>
          {JSON.stringify(course, null, 2)}
        </pre>
      </div>

    </div>
  );
}
