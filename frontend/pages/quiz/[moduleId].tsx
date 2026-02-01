"use client"
import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import { useSession } from "next-auth/react";
import { motion } from "framer-motion";
import { API } from "../../src/utils/api";
import PDFExporter from "../../src/components/PDFExporter";

interface Question {
  id: number;
  question: string;
  options: string[];
  question_type: string;
}

interface QuizResult {
  question_id: number;
  question: string;
  user_answer: string;
  correct_answer: string;
  is_correct: boolean;
  explanation?: string;
}

interface QuizResponse {
  module_name: string;
  module_description: string;
  questions: Question[];
}

interface SubmitResponse {
  module_name: string;
  total_questions: number;
  correct_answers: number;
  score_percentage: number;
  results: QuizResult[];
}

export default function QuizPage() {
  const router = useRouter();
  const { moduleId } = router.query;
  const { data: session } = useSession();

  const [quizData, setQuizData] = useState<QuizResponse | null>(null);
  const [answers, setAnswers] = useState<{ [key: number]: string }>({});
  const [submitted, setSubmitted] = useState<boolean>(false);
  const [results, setResults] = useState<SubmitResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [showAnswers, setShowAnswers] = useState<boolean>(true);
  const [currentQuestion, setCurrentQuestion] = useState<number>(0);
  /* eslint-disable-next-line @typescript-eslint/no-explicit-any */
  const [localQuizSource, setLocalQuizSource] = useState<any[]>([]);
  const [error, setError] = useState<string>("");

  // Function to get course information and construct back URL
  const getBackToTutorialUrl = () => {
    try {
      // Try to get course data from localStorage (set when course is generated)
      const courseData = localStorage.getItem('courseData');
      if (courseData) {
        const course = JSON.parse(courseData);
        const moduleIdNum = parseInt(moduleId as string);

        // Find the module index (0-9) based on moduleId
        const moduleIndex = course.modules.findIndex((m: Record<string, unknown>) => m.id === moduleIdNum);

        if (moduleIndex !== -1) {
          // Extract course slug from course title
          const courseSlug = course.topic.toLowerCase().replace(/\s+/g, '-');
          // Module number is 1-based for display
          const moduleNumber = moduleIndex + 1;

          // Construct URL to go back to the specific module
          return `/?course=${courseSlug}&module=${moduleNumber}`;
        }
      }
    } catch (error) {
      console.error('Error constructing back URL:', error);
    }

    // Fallback to home page if course data is not available
    return '/';
  };

  useEffect(() => {
    if (moduleId && router.isReady) {
      // Inline the call to avoid react-hooks/exhaustive-deps if it's too complex to wrap
      const loadQuiz = () => {
        try {
          const courseDataStr = localStorage.getItem('courseData');
          if (courseDataStr) {
            const courseData = JSON.parse(courseDataStr);
            const moduleIdNum = parseInt(moduleId as string);
            const activeM = courseData.modules.find((m: Record<string, unknown>) => m.id === moduleIdNum);
            if (activeM) {
              const quizDataSrc = activeM.quizzes || activeM.quiz;
              let questions: Question[] = [];
              if (Array.isArray(quizDataSrc)) {
                questions = quizDataSrc;
              } else if (quizDataSrc && Array.isArray(quizDataSrc.questions)) {
                questions = quizDataSrc.questions.map((q: Record<string, unknown>, idx: number) => ({
                  id: idx + 1,
                  question: q.question,
                  options: q.options,
                  answer: q.answer || q.correct_answer || q.correct_option
                }));
              }
              setQuizData({
                questions,
                /* eslint-disable-next-line @typescript-eslint/no-explicit-any */
                module_name: (activeM as any).name || "Module Quiz",
                /* eslint-disable-next-line @typescript-eslint/no-explicit-any */
                module_description: (activeM as any).description || ""
              });
              setAnswers({});
              setResults(null);
              setLocalQuizSource(questions);
              setLoading(false);
            }
          }
        } catch (err: unknown) {
          console.error("Quiz load error:", err);
          setError("Failed to load quiz.");
          setLoading(false);
        }
      };
      loadQuiz();
    }
  }, [moduleId, router.isReady]);

  // Removed redundant loadQuizFromLocalStorage



  const handleOptionSelect = (questionId: number, option: string) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: option
    }));
  };

  const handleSubmitQuiz = async () => {
    // Local submission logic
    let correctCount = 0;
    const quizResults: QuizResult[] = [];

    localQuizSource.forEach((q, idx) => {
      const qId = idx + 1; // Assuming 1-based index matches
      const userAnswer = answers[qId];
      const isCorrect = userAnswer === q.correct_answer;
      if (isCorrect) correctCount++;

      quizResults.push({
        question_id: qId,
        question: q.question,
        user_answer: userAnswer,
        correct_answer: q.correct_answer,
        is_correct: isCorrect,
        explanation: q.explanation
      });
    });

    const scorePct = (correctCount / localQuizSource.length) * 100;

    const submitResponse: SubmitResponse = {
      module_name: quizData?.module_name || "Quiz Results",
      total_questions: localQuizSource.length,
      correct_answers: correctCount,
      score_percentage: scorePct,
      results: quizResults
    };

    setResults(submitResponse);
    setSubmitted(true);

    // SAVE PROGRESS TO BACKEND (Platform Feature)
    if (session?.user?.email) {
      try {
        // Try to get topic from URL or fallback to localStorage
        let topicSlug = "";
        if (typeof router.query.topic === 'string') {
          topicSlug = router.query.topic;
        } else {
          // Fallback
          const saved = localStorage.getItem('courseData');
          if (saved) {
            topicSlug = JSON.parse(saved).topic || "";
          }
        }

        if (topicSlug) {
          await API.post(`/progress/update/`, {
            email: session.user.email,
            topic_slug: topicSlug.toLowerCase(),
            module_id: parseInt(moduleId as string),
            is_completed: true, // Mark completed on submission
            quiz_score: Math.round(scorePct)
          });
          console.log("Progress saved to MentAI Platform");
        }
      } catch (err: unknown) {
        console.error("Failed to save progress:", err instanceof Error ? err.message : "Unknown error");
      }
    }
  };

  const getScoreColor = (percentage: number) => {
    if (percentage >= 80) return "text-green-600";
    if (percentage >= 60) return "text-yellow-600";
    return "text-red-600";
  };

  const getScoreMessage = (percentage: number) => {
    if (percentage === 100) return "Perfect score! Amazing job!";
    if (percentage >= 80) return "Great job! You really know your stuff!";
    if (percentage >= 60) return "Good work! Keep learning!";
    return "Keep studying! You will get better with practice!";
  };

  const getQuestionStatus = (questionIndex: number) => {
    if (!quizData) return "unanswered";
    const questionId = quizData.questions[questionIndex]?.id;
    if (!questionId) return "unanswered";
    return answers[questionId] ? "answered" : "unanswered";
  };

  const scrollToQuestion = (questionIndex: number) => {
    setCurrentQuestion(questionIndex);
    const element = document.getElementById(`question-${questionIndex}`);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-lg text-gray-600">Loading quiz...</p>
        </motion.div>
      </div>
    );
  }

  if (!quizData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <p className="text-lg text-gray-600">Quiz not found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen relative overflow-hidden">
      <div className="relative z-10">
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-8 max-w-5xl mx-auto md:pl-72"
          >
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4 drop-shadow-lg">
              Quiz: {quizData.module_name}
            </h1>
            {quizData.module_description && quizData.module_description !== "Master this concept." && (
              <p className="text-lg text-white max-w-2xl mx-auto mb-6 drop-shadow">
                {quizData.module_description}
              </p>
            )}
            {error && <p className="text-red-400 font-bold">{error}</p>}
            <div className="flex justify-center gap-4">
              <button
                onClick={() => router.push(getBackToTutorialUrl())}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Back to Tutorial
              </button>
            </div>
          </motion.div>

          {!submitted ? (
            <div className="flex max-w-5xl mx-auto md:pl-72 gap-8">
              {/* Sidebar Navigation */}
              <aside className="hidden md:flex flex-col fixed left-8 top-1/2 -translate-y-1/2 h-auto w-64 bg-gradient-to-br from-white/80 to-blue-100/80 shadow-2xl rounded-3xl p-8 border border-blue-200 z-40 transition-all duration-300 backdrop-blur-lg">
                <h3 className="text-2xl font-extrabold font-sans text-gray-900 mb-10 text-center tracking-wide drop-shadow-lg">Question Navigation</h3>
                <div className="grid grid-cols-2 gap-6 mb-12">
                  {quizData.questions.map((_, index) => (
                    <button
                      key={index}
                      onClick={() => scrollToQuestion(index)}
                      className={`w-14 h-14 flex items-center justify-center rounded-full text-lg font-bold shadow-md border-2 focus:outline-none transition-all duration-200 backdrop-blur-lg ${currentQuestion === index
                        ? 'bg-gradient-to-tr from-blue-600 to-blue-400 text-white border-blue-400 shadow-xl ring-4 ring-blue-200 scale-110'
                        : getQuestionStatus(index) === 'answered'
                          ? 'bg-green-100 text-green-800 border-green-300 hover:bg-green-200'
                          : 'bg-white/80 text-gray-600 border-gray-200 hover:bg-blue-100/70'
                        }`}
                      style={{ boxShadow: currentQuestion === index ? '0 4px 24px 0 rgba(59,130,246,0.25)' : undefined }}
                    >
                      Q{index + 1}
                    </button>
                  ))}
                </div>
                <div className="mt-auto pt-8 border-t border-blue-200">
                  <div className="flex items-center justify-between text-base text-gray-700 mb-3 font-medium">
                    <span>Progress:</span>
                    <span>{Object.keys(answers).length} / {quizData.questions.length}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
                    <motion.div
                      className="h-4 rounded-full bg-gradient-to-r from-blue-400 via-blue-500 to-blue-600 shadow"
                      initial={{ width: 0 }}
                      animate={{ width: `${(Object.keys(answers).length / quizData.questions.length) * 100}%` }}
                      transition={{ duration: 0.5 }}
                    />
                  </div>
                </div>
              </aside>

              {/* Main Quiz Content */}
              <div className="flex-1 min-w-0 md:ml-0 ml-0">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-6"
                >
                  {/* Quiz Settings */}
                  <div className="bg-white rounded-lg shadow-lg p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-800">
                          Quiz Settings
                        </h3>
                        <p className="text-gray-600">Configure your quiz experience</p>
                      </div>
                      <label className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={showAnswers}
                          onChange={(e) => setShowAnswers(e.target.checked)}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span className="text-gray-700">Show answers after submission</span>
                      </label>
                    </div>
                  </div>

                  {/* Questions */}
                  {quizData.questions.map((question, index) => (
                    <motion.div
                      key={question.id}
                      id={`question-${index}`}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="bg-white rounded-lg shadow-lg p-6"
                    >
                      <div className="mb-4">
                        <span className="inline-block bg-blue-100 text-blue-800 text-sm font-medium px-3 py-1 rounded-full mb-3">
                          Question {index + 1} of {quizData.questions.length}
                        </span>
                        <p className="text-lg font-semibold text-gray-800">
                          {question.question}
                        </p>
                      </div>

                      <div className="space-y-3">
                        {question.options.map((option, optionIndex) => (
                          <motion.div
                            key={optionIndex}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={() => handleOptionSelect(question.id, option)}
                            className={`cursor-pointer p-4 rounded-lg border-2 transition-all duration-200 ${answers[question.id] === option
                              ? 'bg-blue-100 border-blue-500 shadow-md'
                              : 'bg-white border-gray-200 hover:bg-gray-50 hover:border-gray-300'
                              }`}
                          >
                            <div className="flex items-center">
                              <div className={`w-6 h-6 rounded-full mr-4 border-2 flex items-center justify-center ${answers[question.id] === option
                                ? 'bg-blue-600 border-blue-600'
                                : 'border-gray-300'
                                }`}>
                                {answers[question.id] === option && (
                                  <div className="w-3 h-3 bg-white rounded-full"></div>
                                )}
                              </div>
                              <span className={`font-medium ${answers[question.id] === option ? 'text-blue-800' : 'text-gray-700'
                                }`}>{option}</span>
                            </div>
                          </motion.div>
                        ))}
                      </div>
                    </motion.div>
                  ))}

                  {/* Submit Button */}
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center"
                  >
                    <button
                      onClick={handleSubmitQuiz}
                      disabled={Object.keys(answers).length < quizData.questions.length}
                      className="px-8 py-4 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors text-lg font-semibold"
                    >
                      Submit Quiz ({Object.keys(answers).length}/{quizData.questions.length})
                    </button>
                  </motion.div>
                </motion.div>
              </div>
            </div>
          ) : (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="max-w-4xl mx-auto"
            >
              {/* Results Summary */}
              <div className="bg-white rounded-lg shadow-lg p-8 mb-6 text-center">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
                  className="text-6xl mb-4"
                >
                  ✓
                </motion.div>
                <h2 className="text-3xl font-bold text-gray-800 mb-4">
                  Quiz Complete!
                </h2>
                <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-6 mb-6">
                  <p className="text-2xl text-gray-800 mb-2">
                    You scored <span className={`font-bold ${getScoreColor(results!.score_percentage)}`}>
                      {results!.correct_answers}
                    </span> out of <span className="font-bold text-blue-600">
                      {results!.total_questions}
                    </span>
                  </p>
                  <p className="text-xl text-gray-600">
                    ({results!.score_percentage.toFixed(1)}%)
                  </p>
                </div>
                <p className="text-lg text-gray-700 font-medium mb-6">
                  {getScoreMessage(results!.score_percentage)}
                </p>
                <div className="flex justify-center gap-4 mb-6">
                  <button
                    onClick={() => {
                      setSubmitted(false);
                      setAnswers({});
                      setResults(null);
                      setCurrentQuestion(0);
                    }}
                    className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Take Quiz Again
                  </button>
                  <button
                    onClick={() => router.push(getBackToTutorialUrl())}
                    className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                  >
                    Back to Tutorial
                  </button>
                </div>

                {/* PDF Export */}
                <div className="flex justify-center">
                  <PDFExporter quizResults={results || undefined} type="quiz" />
                </div>
              </div>

              {/* Detailed Results */}
              {showAnswers && (
                <div className="space-y-6">
                  <h3 className="text-2xl font-bold text-gray-800 text-center mb-6">
                    Detailed Results
                  </h3>

                  {results!.results.map((result, index) => (
                    <motion.div
                      key={result.question_id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className={`bg-white rounded-lg shadow-lg p-6 border-l-4 ${result.is_correct ? 'border-green-500' : 'border-red-500'
                        }`}
                    >
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center">
                          <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium mr-3 ${result.is_correct
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                            }`}>
                            {result.is_correct ? 'Correct' : 'Incorrect'}
                          </span>
                          <span className="text-gray-500">Question {index + 1}</span>
                        </div>
                      </div>

                      <p className="text-lg font-semibold text-gray-800 mb-4">
                        {result.question}
                      </p>

                      <div className="space-y-2">
                        <div className="flex items-center">
                          <span className="font-medium text-gray-700 w-24">Your Answer:</span>
                          <span className={`font-medium ${result.is_correct ? 'text-green-600' : 'text-red-600'
                            }`}>
                            {result.user_answer || 'Not answered'}
                          </span>
                        </div>

                        {!result.is_correct && (
                          <div className="flex items-center">
                            <span className="font-medium text-gray-700 w-24">Correct Answer:</span>
                            <span className="font-medium text-green-600">
                              {result.correct_answer}
                            </span>
                          </div>
                        )}

                        {result.explanation && (
                          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                            <p className="text-sm font-medium text-blue-800 mb-2">Explanation:</p>
                            <p className="text-blue-700">{result.explanation}</p>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
} 