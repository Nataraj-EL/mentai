"use client"
import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";
import CodeEditor from "../src/components/CodeEditor";
import PDFExporter from "../src/components/PDFExporter";

interface Subsection {
  title: string;
  content: string;
}



interface RealWorldExample {
  title: string;
  description: string;
  solution: string;
  learning_outcome: string;
}

interface MiniLab {
  title: string;
  description: string;
  tasks: string[];
  expected_outcome: string;
  preloaded_code?: string;
}

interface PracticeProblem {
  name: string;
  url: string;
}

interface MiniProject {
  title: string;
  description: string;
  tasks: string[];
}

interface Module {
  id: number;
  name: string;
  description: string;
  content: string;
  difficulty: string;
  order: number;
  duration: string;
  subsections: Subsection[];
  theory?: string;
  mini_project?: MiniProject;
  real_world_examples: RealWorldExample[];
  mini_labs: MiniLab[];
  practice_problems?: PracticeProblem[];
  quizzes: unknown[];
  preloaded_code?: string | null;
}

interface CourseMetadata {
  language: string;
  execution_enabled: boolean;
  topic_type: string;
}


interface CourseData {
  id: number;
  course_title: string;
  course_content: string;
  topic: string;
  modules: Module[];
  metadata?: CourseMetadata;
}

const SimpleMarkdown = ({ content }: { content: string }) => {
  if (!content) return null;
  return (
    <div className="prose prose-lg prose-blue max-w-none text-gray-700 space-y-6">
      {content.split('\n').map((line, i) => {
        if (line.startsWith('# ')) return <h2 key={i} className="text-3xl font-extrabold text-blue-900 mt-10 mb-6 pb-2 border-b border-blue-100">{line.replace('# ', '')}</h2>;
        if (line.startsWith('## ')) return <h3 key={i} className="text-2xl font-bold text-gray-800 mt-8 mb-4">{line.replace('## ', '')}</h3>;
        if (line.startsWith('### ')) return <h4 key={i} className="text-xl font-semibold text-gray-800 mt-6 mb-3">{line.replace('### ', '')}</h4>;
        if (line.startsWith('- ')) return <li key={i} className="ml-6 list-disc pl-2 text-lg mb-2">{line.replace('- ', '')}</li>;
        if (line.startsWith('> ')) return <blockquote key={i} className="bg-blue-50 border-l-4 border-blue-500 pl-4 py-2 italic text-gray-800 my-4 rounded-r">{line.replace('> ', '')}</blockquote>;
        if (line.startsWith('```')) return null; // We handle large code blocks separately if parsed correctly, but for simple split this skips fences

        // Handle code blocks manually if line starts with code indentation or similar, but for now simple lines
        const processedLine = line
          .replace(/\*\*(.*?)\*\*/g, '<strong class="text-gray-900">$1</strong>')
          .replace(/`([^`]+)`/g, '<code class="bg-gray-100 px-1.5 py-0.5 rounded text-pink-600 font-mono text-base border border-gray-200">$1</code>');

        return <p key={i} className="leading-relaxed text-lg" dangerouslySetInnerHTML={{ __html: processedLine }} />;
      })}
    </div>
  );
};

export default function Home() {
  const [error, setError] = useState<string>("");
  const router = useRouter();
  const [topic, setTopic] = useState<string>("");
  const [showSuggestions, setShowSuggestions] = useState(false);

  const POPULAR_TOPICS = [
    "Python", "JavaScript", "React", "Java", "C++",
    "HTML/CSS", "SQL", "Go", "Rust", "TypeScript",
    "Node.js", "Docker", "Kubernetes", "AWS", "Machine Learning"
  ];
  // Language is now derived from topic by backend
  const [course, setCourse] = useState<CourseData | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [loadingMessage, setLoadingMessage] = useState<string>("");
  const [currentModule, setCurrentModule] = useState<number>(0);
  const [activeLabIndex, setActiveLabIndex] = useState<number>(0);

  // Reset active lab when module changes
  useEffect(() => {
    setActiveLabIndex(0);
  }, [currentModule]);

  // Handle URL parameters for returning from quiz
  useEffect(() => {
    if (router.isReady) {
      const { course: courseParam, module: moduleParam } = router.query;

      // If we have course and module parameters, try to load the course and navigate to the module
      if (courseParam && moduleParam) {
        const courseData = localStorage.getItem('courseData');
        if (courseData) {
          try {
            const parsedCourse = JSON.parse(courseData);
            // Check if this is the same course (by topic)
            const courseSlug = parsedCourse.topic.toLowerCase().replace(/\s+/g, '-');
            if (courseSlug === courseParam) {
              setCourse(parsedCourse);
              // Set the current module (convert from 1-based to 0-based)
              const moduleNumber = parseInt(moduleParam as string);
              if (moduleNumber >= 1 && moduleNumber <= parsedCourse.modules.length) {
                setCurrentModule(moduleNumber - 1);
              }
            }
          } catch (error) {
            console.error('Error parsing course data from localStorage:', error);
          }
        }
      }
    }
  }, [router.isReady, router.query]);

  const handleGenerate = async () => {
    if (!topic.trim()) return;

    setError("");
    setLoading(true);
    setLoadingMessage("Initializing course generation...");

    // Clear any existing course data
    localStorage.removeItem('courseData');

    try {
      // Simulate progressive loading messages
      const messages = [
        "Analyzing topic requirements...",
        "Generating module structure...",
        "Creating learning content...",
        "Building interactive elements...",
        "Finalizing course materials..."
      ];

      let messageIndex = 0;
      const messageInterval = setInterval(() => {
        if (messageIndex < messages.length) {
          setLoadingMessage(messages[messageIndex]);
          messageIndex++;
        } else {
          clearInterval(messageInterval);
        }
      }, 1000);

      const res = await axios.post(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/generate-course/`, { topic });
      setCourse(res.data);
      setCurrentModule(0);

      // Store course data in localStorage for quiz navigation
      localStorage.setItem('courseData', JSON.stringify(res.data));

      clearInterval(messageInterval);
    } catch (error: unknown) {
      setCourse(null);
      let userMessage = "Sorry, the server is taking too long to respond. Please try again later.";

      if (axios.isAxiosError(error)) {
        console.error(error.message);
        if (error.response?.status === 504) {
          userMessage = "The server took too long to generate the course. Please try again in a few minutes.";
        } else if (error.response?.data?.error) {
          userMessage = error.response.data.error;
        } else if (error.message.toLowerCase().includes("timeout")) {
          userMessage = "The server timed out. Please try again later.";
        }
      } else if (error instanceof Error) {
        console.error(error.message);
      }

      setError(userMessage);
    } finally {
      setLoading(false);
      setLoadingMessage("");
    }
  };

  // Cleanup localStorage when component unmounts
  useEffect(() => {
    return () => {
      // Don't clear localStorage on unmount as we want to preserve course data for quiz navigation
    };
  }, []);

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-800';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800';
      case 'advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getDifficultyLabel = (difficulty: string) => {
    return difficulty.charAt(0).toUpperCase() + difficulty.slice(1);
  };

  return (
    <div className="min-h-screen relative overflow-hidden">
      <div className="relative z-10">
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4" role="alert">
            <span className="block sm:inline">{error}</span>
          </div>
        )
        }
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-8"
          >
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4 drop-shadow-2xl">
              MentAI
            </h1>
            <p className="text-lg text-white/90 max-w-2xl mx-auto drop-shadow-lg font-medium">
              Generate comprehensive courses with interactive modules, code examples, and engaging quizzes powered by AI
            </p>
          </motion.div>

          {/* Course Generation Form */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-2xl mx-auto mb-8"
          >
            <div className="bg-white/60 backdrop-blur-md rounded-lg shadow-lg p-6 border border-white/20 relative">
              <div className="flex flex-col gap-4">
                <div className="flex flex-col sm:flex-row gap-4 relative">
                  <div className="flex-1 relative">
                    <input
                      type="text"
                      autoFocus
                      placeholder="Enter a topic (e.g., Python, Java, React, HTML, C++)..."
                      value={topic}
                      onChange={(e) => {
                        setTopic(e.target.value);
                        setShowSuggestions(true);
                      }}
                      onFocus={() => setShowSuggestions(true)}
                      onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                      className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 bg-white placeholder-gray-500 text-lg shadow-inner"
                      onKeyPress={(e) => e.key === 'Enter' && handleGenerate()}
                    />
                    {/* Autocomplete Suggestions */}
                    {showSuggestions && topic.length > 0 && (
                      <div className="absolute top-full left-0 right-0 mt-1 bg-white rounded-lg shadow-xl border border-gray-100 overflow-hidden z-50 max-h-48 overflow-y-auto">
                        {POPULAR_TOPICS.filter(t => t.toLowerCase().includes(topic.toLowerCase())).map((t, i) => (
                          <div
                            key={i}
                            className="px-4 py-2 hover:bg-blue-50 cursor-pointer text-gray-700 font-medium transition-colors"
                            onClick={() => {
                              setTopic(t);
                              setShowSuggestions(false);
                            }}
                          >
                            {t}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleGenerate}
                  disabled={loading || !topic.trim()}
                  className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? 'Generating...' : 'Generate Course'}
                </motion.button>
              </div>
            </div>
          </motion.div>

          {/* Loading Animation */}
          <AnimatePresence>
            {loading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 z-50 flex flex-col items-center justify-center h-full w-full"
              >
                {/* Overlay */}
                <div className="absolute inset-0 bg-gradient-to-br from-blue-900/70 via-indigo-800/60 to-purple-900/70 backdrop-blur-sm"></div>
                {/* Spinner and text */}
                <div className="relative z-10 flex flex-col items-center">
                  <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-400 border-t-white shadow-lg mb-6"></div>
                  <p className="text-white text-lg font-semibold drop-shadow-lg mb-2">Generating your course. This may take up to a minute for new topics...</p>
                  <p className="text-blue-200 text-base font-medium drop-shadow-md">{loadingMessage}</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Course Display */}
          <AnimatePresence>
            {course && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="max-w-6xl mx-auto"
              >
                {/* Course Header */}
                <div className="bg-white/80 backdrop-blur-sm rounded-lg shadow-lg p-6 mb-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h2 className="text-3xl font-bold text-gray-800 mb-2">{course.course_title}</h2>
                      <p className="text-gray-700 leading-relaxed">{course.course_content}</p>
                    </div>
                    {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
                    <PDFExporter courseData={course as any} type="course" />
                  </div>
                </div>

                {/* Module Navigation */}
                <div className="bg-white/80 backdrop-blur-sm rounded-lg shadow-lg p-6 mb-6">
                  <h3 className="text-xl font-semibold text-gray-800 mb-4">Course Modules</h3>
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {course.modules.map((module: Module, index: number) => (
                      <motion.div
                        key={module.id}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => setCurrentModule(index)}
                        className={`cursor-pointer p-4 rounded-lg border-2 transition-all duration-200 ${currentModule === index
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 bg-white hover:border-gray-300'
                          }`}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(module.difficulty)}`}>
                            {getDifficultyLabel(module.difficulty)}
                          </span>
                        </div>
                        <h4 className="font-semibold text-gray-800 mb-2">{module.name}</h4>
                        {module.description && module.description !== "Master this concept." && (
                          <p className="text-sm text-gray-600 mb-2">{module.description}</p>
                        )}
                        <div className="text-xs text-gray-500">
                          Module {index + 1} of {course.modules.length}
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>

                {/* Current Module Content */}
                {course.modules[currentModule] && (
                  <motion.div
                    key={currentModule}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="bg-white/80 backdrop-blur-sm rounded-lg shadow-lg p-6 mb-6"
                  >
                    <div className="flex justify-between items-start mb-6">
                      <div>
                        <h3 className="text-2xl font-bold text-gray-800 mb-2">
                          {course.modules[currentModule].name}
                        </h3>
                        <div className="flex items-center gap-4 mb-2">
                          <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getDifficultyColor(course.modules[currentModule].difficulty)}`}>
                            {getDifficultyLabel(course.modules[currentModule].difficulty)}
                          </span>
                        </div>
                        {course.modules[currentModule].description && course.modules[currentModule].description !== "Master this concept." && (
                          <p className="text-gray-700 mb-4">{course.modules[currentModule].description}</p>
                        )}
                      </div>
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => router.push(`/quiz/${course.modules[currentModule].id}`)}
                        className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                      >
                        Take Quiz
                      </motion.button>
                    </div>



                    {/* 1. Theory Section (New) */}
                    {course.modules[currentModule].theory && (
                      <div className="mb-8">
                        <div className="bg-white/90 rounded-lg p-6 border-l-4 border-blue-500 shadow-sm">
                          <h4 className="flex items-center text-xl font-bold text-gray-800 mb-4">
                            <span className="mr-2">📖</span> Module Theory
                          </h4>
                          <SimpleMarkdown content={course.modules[currentModule].theory!} />
                        </div>
                      </div>
                    )}

                    {/* 2. Interactive Labs (Stable, Single Compiler) */}
                    {(course.modules[currentModule].preloaded_code || (course.modules[currentModule].mini_labs && course.modules[currentModule].mini_labs.length > 0)) && (
                      <div className="mb-8">
                        <h4 className="flex items-center text-xl font-bold text-gray-800 mb-4">
                          <span className="mr-2">💻</span> Interactive Labs
                        </h4>

                        {/* Lab Tabs */}
                        {course.modules[currentModule].mini_labs && course.modules[currentModule].mini_labs.length > 0 && (
                          <div className="flex space-x-2 mb-4 overflow-x-auto pb-2">
                            {course.modules[currentModule].mini_labs.map((lab: MiniLab, idx: number) => (
                              <button
                                key={idx}
                                onClick={() => setActiveLabIndex(idx)}
                                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeLabIndex === idx
                                  ? 'bg-blue-600 text-white shadow-md ring-2 ring-blue-300'
                                  : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
                                  }`}
                              >
                                {lab.title || `Lab ${idx + 1}`}
                              </button>
                            ))}
                          </div>
                        )}

                        <div className="bg-gray-900 rounded-lg overflow-hidden shadow-xl border border-gray-700">
                          {/* Lab Metadata Header */}
                          <div className="bg-gray-800 px-4 py-2 border-b border-gray-700 flex justify-between items-center">
                            <span className="text-gray-300 text-sm font-mono">
                              {(course.modules[currentModule].mini_labs && course.modules[currentModule].mini_labs[activeLabIndex])
                                ? course.modules[currentModule].mini_labs[activeLabIndex].title
                                : `Lab: ${course.modules[currentModule].name}`}
                            </span>
                            <span className="text-xs text-gray-500"> judge0 Execution Environment</span>
                          </div>

                          <CodeEditor
                            code={
                              (course.modules[currentModule].mini_labs && course.modules[currentModule].mini_labs[activeLabIndex] && course.modules[currentModule].mini_labs[activeLabIndex].preloaded_code)
                                ? course.modules[currentModule].mini_labs[activeLabIndex].preloaded_code
                                : (course.modules[currentModule].preloaded_code || "")
                            }
                            language={course.metadata?.language || 'python'}
                            title=""
                            explanation={
                              (course.modules[currentModule].mini_labs && course.modules[currentModule].mini_labs[activeLabIndex])
                                ? course.modules[currentModule].mini_labs[activeLabIndex].description
                                : "Experiment with this pre-loaded code."
                            }
                            topic={course.topic} // Pass topic prop
                            readOnly={course.metadata ? !course.metadata.execution_enabled : false}
                          />
                        </div>
                      </div>
                    )}

                    {/* 3. Mini Project (New) */}
                    {course.modules[currentModule].mini_project && (
                      <div className="mb-8">
                        <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg p-6 border border-purple-200 shadow-sm">
                          <h4 className="flex items-center text-xl font-bold text-purple-900 mb-4">
                            <span className="mr-2">🚀</span> Mini Project: {course.modules[currentModule].mini_project.title}
                          </h4>
                          <p className="text-gray-700 mb-4">{course.modules[currentModule].mini_project.description}</p>

                          <div className="bg-white/80 rounded-lg p-4">
                            <h6 className="font-semibold text-purple-800 mb-2">Project Tasks:</h6>
                            <ul className="space-y-2">
                              {course.modules[currentModule].mini_project.tasks.map((task: string, i: number) => (
                                <li key={i} className="flex items-start">
                                  <span className="inline-block w-5 h-5 rounded-full bg-purple-200 text-purple-700 flex items-center justify-center text-xs font-bold mr-3">{i + 1}</span>
                                  <span className="text-gray-700">{task}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* 4. Quiz Section CTA */}
                    <div className="mb-8">
                      <motion.div
                        whileHover={{ scale: 1.01 }}
                        className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-6 border border-green-200 shadow-sm flex flex-col md:flex-row items-center justify-between"
                      >
                        <div className="mb-4 md:mb-0">
                          <h4 className="flex items-center text-xl font-bold text-green-800 mb-2">
                            <span className="mr-2">📝</span> Knowledge Check
                          </h4>
                          <p className="text-green-700">Test your understanding with a {course.modules[currentModule].quizzes?.length || 10}-question quiz.</p>
                        </div>
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => router.push(`/quiz/${course.modules[currentModule].id}`)}
                          className="px-8 py-4 bg-green-600 text-white font-bold rounded-lg hover:bg-green-700 shadow-lg transition-colors flex items-center"
                        >
                          Take Quiz <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
                        </motion.button>
                      </motion.div>
                    </div>


                    {/* 5. Practice Problems */}
                    {course.modules[currentModule].practice_problems && course.modules[currentModule].practice_problems.length > 0 && (
                      <div className="mb-6">
                        <h4 className="flex items-center text-xl font-semibold text-gray-800 mb-4">
                          <span className="mr-2">⚡</span> Practice Problems
                        </h4>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                          {course.modules[currentModule].practice_problems.map((problem: PracticeProblem, index: number) => (
                            <motion.a
                              key={index}
                              href={problem.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              whileHover={{ scale: 1.02 }}
                              className="block p-4 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md hover:border-blue-300 transition-all group"
                            >
                              <div className="flex items-center justify-between">
                                <span className="font-medium text-gray-700 group-hover:text-blue-600">{problem.name}</span>
                                <svg className="w-4 h-4 text-gray-400 group-hover:text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                </svg>
                              </div>
                            </motion.a>
                          ))}
                        </div>
                      </div>
                    )}
                  </motion.div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div >
    </div >
  );
}

