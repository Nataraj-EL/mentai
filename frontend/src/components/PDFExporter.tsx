"use client"
import { useState } from 'react';
import { motion } from 'framer-motion';

interface MiniLab {
  title: string;
  description: string;
  preloaded_code?: string;
}

interface MiniProject {
  title: string;
  description: string;
  tasks: string[];
}

interface PracticeProblem {
  name: string;
  url: string;
}

interface QuizQuestion {
  question: string;
  options: string[];
  correct_answer?: string;
  answer?: string;
  correct_option?: string;
  explanation?: string;
}

interface QuizResult {
  question?: string;
  question_id: number;
  user_answer: string;
  correct_answer: string;
  is_correct: boolean;
  explanation?: string;
}

interface Module {
  name: string;
  description?: string;
  theory?: string;
  content?: string;
  preloaded_code?: string;
  mini_labs?: MiniLab[];
  mini_project?: MiniProject;
  practice_problems?: PracticeProblem[];
  quizzes?: { questions: QuizQuestion[] } | QuizQuestion[];
  quiz?: { questions: QuizQuestion[] } | QuizQuestion[];
}

interface PDFExporterProps {
  courseData?: {
    course_title?: string;
    course_content?: string;
    topic?: string;
    modules?: Module[];
  };
  quizResults?: {
    module_name?: string;
    results?: QuizResult[];
    total_questions?: number;
    correct_answers?: number;
    score_percentage?: number;
  };
  type: 'course' | 'quiz';
}

export default function PDFExporter({ courseData, quizResults, type }: PDFExporterProps) {
  const [isGenerating, setIsGenerating] = useState(false);

  const exportToPDF = async () => {
    setIsGenerating(true);
    try {
      const { jsPDF } = await import('jspdf');
      const doc = new jsPDF();
      const pageWidth = doc.internal.pageSize.getWidth();
      const margin = 20;
      const contentWidth = pageWidth - 2 * margin;
      let yPosition = 30;

      if (type === "course" && courseData) {
        // Course PDF Export
        doc.setFontSize(24);
        doc.setTextColor(0, 0, 0);
        doc.text(courseData.course_title || "Course", pageWidth / 2, yPosition, { align: "center" });
        yPosition += 20;

        doc.setFontSize(12);
        const descLines = doc.splitTextToSize(courseData.course_content || "Course content", contentWidth);
        doc.text(descLines, margin, yPosition);
        yPosition += descLines.length * 6 + 5;

        // Modules
        courseData.modules?.forEach((module: Module) => {
          if (yPosition > 250) {
            doc.addPage();
            yPosition = 20;
          }

          doc.setFontSize(16);
          doc.text(module.name || "Module", margin, yPosition);
          yPosition += 10;

          // Module Description/Explanation
          if (module.description) {
            doc.setFontSize(12);
            const descLines = doc.splitTextToSize(module.description, contentWidth);
            doc.text(descLines, margin, yPosition);
            yPosition += descLines.length * 6 + 4;
          }

          // Theory Section
          if (module.theory) {
            yPosition += 5;
            doc.setFontSize(14);
            doc.setTextColor(0, 0, 100);
            doc.text("Theory & Concepts:", margin, yPosition);
            yPosition += 8;

            doc.setFontSize(11);
            doc.setTextColor(0, 0, 0);
            // Simple markdown cleanup for PDF
            const cleanTheory = module.theory.replace(/#/g, '').replace(/\*\*/g, '');
            const theoryLines = doc.splitTextToSize(cleanTheory, contentWidth);

            // Check page break for theory
            if (yPosition + (theoryLines.length * 6) > 270) {
              doc.addPage();
              yPosition = 20;
            }

            doc.text(theoryLines, margin, yPosition);
            yPosition += theoryLines.length * 6 + 8;
          }

          // Module Content (Legacy/Extra)
          if (module.content) {
            doc.setFontSize(12);
            const contentLines = doc.splitTextToSize(module.content, contentWidth);
            doc.text(contentLines, margin, yPosition);
            yPosition += contentLines.length * 6 + 6;
          }

          // Preloaded Code (Interactive Lab)
          if (module.preloaded_code) {
            // ... (existing code, untouched) ...
          }

          // ... (code examples logic skipped/removed implicitly if array empty) ...

          // Mini Labs & Preloaded Code
          if (module.mini_labs && module.mini_labs.length > 0) {
            if (yPosition > 250) { doc.addPage(); yPosition = 20; }
            yPosition += 5;
            doc.setFontSize(14);
            doc.setTextColor(0, 100, 0);
            doc.text("Interactive Labs:", margin, yPosition);
            yPosition += 8;

            module.mini_labs.forEach((lab: MiniLab) => {
              if (yPosition > 230) { doc.addPage(); yPosition = 20; }

              doc.setFontSize(12);
              doc.setTextColor(0, 0, 0);
              doc.setFont("helvetica", "bold");
              doc.text(lab.title || "Interactive Lab", margin, yPosition);
              yPosition += 6;

              doc.setFont("helvetica", "normal");
              doc.text(lab.description, margin, yPosition);
              yPosition += 8;

              // Preloaded Code for this Lab
              if (lab.preloaded_code) {
                doc.setFontSize(10);
                doc.setTextColor(150, 0, 150);
                doc.text("Lab Code:", margin, yPosition);
                yPosition += 5;

                doc.setFont("courier", "normal");
                doc.setTextColor(0, 0, 0);
                const codeLines = doc.splitTextToSize(lab.preloaded_code, contentWidth - 10);
                doc.text(codeLines, margin + 5, yPosition);
                yPosition += codeLines.length * 5 + 8;
                doc.setFont("helvetica", "normal");
              }
              yPosition += 5;
            });
          }

          // Mini Project
          if (module.mini_project) {
            if (yPosition > 250) { doc.addPage(); yPosition = 20; }
            yPosition += 10;
            doc.setFontSize(14);
            doc.setTextColor(100, 0, 100); // Purple
            doc.text(`Mini Project: ${module.mini_project.title}`, margin, yPosition);
            yPosition += 8;

            doc.setFontSize(12);
            doc.setTextColor(0, 0, 0);
            const descendLines = doc.splitTextToSize(module.mini_project.description, contentWidth);
            doc.text(descendLines, margin, yPosition);
            yPosition += descendLines.length * 6 + 6;

            if (module.mini_project.tasks) {
              doc.setFont("helvetica", "bold");
              doc.text("Tasks:", margin, yPosition);
              yPosition += 6;
              doc.setFont("helvetica", "normal");

              module.mini_project.tasks.forEach((task: string, i: number) => {
                const taskText = `${i + 1}. ${task}`;
                const taskLines = doc.splitTextToSize(taskText, contentWidth - 5);
                doc.text(taskLines, margin + 5, yPosition);
                yPosition += taskLines.length * 6 + 2;
              });
            }
            yPosition += 5;
          }

          // Practice Problems
          if (module.practice_problems && module.practice_problems.length > 0) {
            if (yPosition > 250) { doc.addPage(); yPosition = 20; }
            yPosition += 5;
            doc.setFontSize(14);
            doc.setTextColor(200, 100, 0);
            doc.text("Practice Problems:", margin, yPosition);
            yPosition += 8;

            module.practice_problems.forEach((prob: PracticeProblem) => {
              doc.setFontSize(11);
              doc.setTextColor(0, 0, 200); // Link color
              doc.setFont("helvetica", "underline");
              doc.textWithLink(prob.name, margin, yPosition, { url: prob.url });
              yPosition += 6;
            });
            doc.setFont("helvetica", "normal");
            doc.setTextColor(0, 0, 0);
            yPosition += 5;
          }

          // Module Quiz
          const quizData = module.quizzes || module.quiz;
          let quizQuestions: QuizQuestion[] = [];

          if (Array.isArray(quizData)) {
            quizQuestions = quizData;
          } else if (quizData && quizData.questions && Array.isArray(quizData.questions)) {
            quizQuestions = quizData.questions;
          }

          if (quizQuestions.length > 0) {
            yPosition += 4;
            if (yPosition > 250) { doc.addPage(); yPosition = 20; }

            doc.setFontSize(13);
            doc.setTextColor(30, 30, 120);
            doc.text('Quiz:', margin, yPosition);
            yPosition += 8;
            doc.setFontSize(12);
            doc.setTextColor(0, 0, 0);

            quizQuestions.forEach((q: QuizQuestion, qIdx: number) => {
              if (yPosition > 250) { doc.addPage(); yPosition = 20; }
              // Question
              const qLines = doc.splitTextToSize(`Q${qIdx + 1}. ${q.question}`, contentWidth);
              doc.text(qLines, margin + 4, yPosition);
              yPosition += qLines.length * 6 + 2;

              // Options
              if (q.options && Array.isArray(q.options)) {
                q.options.forEach((opt: string, optIdx: number) => {
                  const prefix = String.fromCharCode(65 + optIdx) + ". ";
                  // Check correctness

                  doc.setTextColor(80, 80, 80);
                  const optLines = doc.splitTextToSize(prefix + opt, contentWidth - 10);
                  doc.text(optLines, margin + 12, yPosition);
                  yPosition += optLines.length * 6;
                });

                // Show Answer/Explanation
                yPosition += 2;
                if (yPosition > 250) { doc.addPage(); yPosition = 20; }

                doc.setFont('helvetica', 'bold');
                doc.setTextColor(0, 100, 0);
                doc.text(`Correct: ${q.correct_answer || q.answer || q.correct_option}`, margin + 12, yPosition);
                yPosition += 6;

                if (q.explanation) {
                  doc.setFont('helvetica', 'italic');
                  doc.setTextColor(60, 60, 60);
                  const expLines = doc.splitTextToSize(`Explanation: ${q.explanation}`, contentWidth - 15);
                  doc.text(expLines, margin + 12, yPosition);
                  yPosition += expLines.length * 6;
                }

                doc.setTextColor(0, 0, 0);
                doc.setFont('helvetica', 'normal');
              }
              yPosition += 4;
            });
            yPosition += 8;
          }

          yPosition += 10;
        }); // Close module loop
      } else if (type === "quiz") {
        // Quiz Results PDF Export
        doc.setFontSize(24);
        doc.setTextColor(0, 0, 0);
        doc.text("Quiz Results", pageWidth / 2, yPosition, { align: "center" });
        yPosition += 20;

        if (quizResults && quizResults.module_name) {
          doc.setFontSize(16);
          doc.text(quizResults.module_name, margin, yPosition);
          yPosition += 15;
        }

        if (quizResults && quizResults.results && quizResults.results.length > 0) {
          doc.setFontSize(12);
          quizResults.results.forEach((result: QuizResult, idx: number) => {
            if (idx > 0 && idx % 5 === 0) {
              doc.addPage();
              yPosition = 20;
            }

            // Question
            doc.setFontSize(12);
            doc.setTextColor(0, 0, 0);
            const questionText = result.question || `Question ${idx + 1}`;
            const qLines = doc.splitTextToSize(`Q${idx + 1}. ${questionText}`, contentWidth);
            doc.text(qLines, margin, yPosition);
            yPosition += qLines.length * 7 + 2;

            // Your Answer
            doc.setFont("helvetica", "bold");
            doc.setFontSize(11);
            doc.setTextColor(40, 40, 40);
            doc.text("Your Answer:", margin, yPosition);
            doc.setFont("helvetica", "normal");
            if (result.user_answer === result.correct_answer) {
              doc.setTextColor(0, 150, 0);
            } else {
              doc.setTextColor(200, 0, 0);
            }
            const userAnswer = result.user_answer || "Not answered";
            const uaLines = doc.splitTextToSize(userAnswer, contentWidth - 25);
            doc.text(uaLines, margin + 28, yPosition);
            yPosition += uaLines.length * 6 + 2;

            // Correct Answer
            doc.setFont("helvetica", "bold");
            doc.setFontSize(11);
            doc.setTextColor(40, 40, 40);
            doc.text("Correct Answer:", margin, yPosition);
            doc.setFont("helvetica", "normal");
            doc.setTextColor(0, 0, 0);
            const correctAnswer = result.correct_answer || "Not available";
            const caLines = doc.splitTextToSize(correctAnswer, contentWidth - 38);
            doc.text(caLines, margin + 38, yPosition);
            yPosition += caLines.length * 6 + 2;

            // Explanation
            if (result.explanation) {
              doc.setFont("helvetica", "bold");
              doc.setFontSize(11);
              doc.setTextColor(40, 40, 40);
              doc.text("Explanation:", margin, yPosition);
              doc.setFont("helvetica", "normal");
              doc.setTextColor(0, 0, 0);
              const expLines = doc.splitTextToSize(result.explanation, contentWidth - 32);
              doc.text(expLines, margin + 32, yPosition);
              yPosition += expLines.length * 6 + 2;
            }

            // Extra space before next question
            yPosition += 10;
          });

          // Score Summary
          if (quizResults.total_questions !== undefined) {
            yPosition += 10;
            doc.setFontSize(14);
            doc.text("Score Summary:", margin, yPosition);
            yPosition += 10;

            doc.setFontSize(12);
            doc.text(`Total Questions: ${quizResults.total_questions}`, margin, yPosition);
            yPosition += 8;
            doc.text(`Correct Answers: ${quizResults.correct_answers || 0}`, margin, yPosition);
            yPosition += 8;
            const score = quizResults.score_percentage || 0;
            doc.text(`Score: ${score.toFixed(1)}%`, margin, yPosition);
            yPosition += 15;
          }
        } else {
          // No results available
          doc.setFontSize(16);
          doc.text("No quiz results available.", pageWidth / 2, yPosition, { align: "center" });
          yPosition += 20;
          doc.setFontSize(12);
          doc.text("Complete a quiz to see your results here.", pageWidth / 2, yPosition, { align: "center" });
        }
      }

      let fileName = "MentAI_Export.pdf";
      if (type === "course") {
        const topicName = courseData?.topic || courseData?.course_title?.replace("Complete ", "").replace(" Mastery Course", "") || "Course";
        fileName = `MentAI - ${topicName} by ELN.pdf`;
      } else {
        fileName = `${quizResults?.module_name || 'Quiz'}_Report.pdf`;
      }

      doc.save(fileName);
    } catch (error) {
      console.error("Error generating PDF:", error);
      alert("Error generating PDF. Please try again.");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={exportToPDF}
      disabled={isGenerating}
      className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
    >
      {isGenerating ? (
        <>
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          <span>Generating PDF...</span>
        </>
      ) : (
        <>
          <span>Export {type === 'course' ? 'Course' : 'Quiz Report'} as PDF</span>
        </>
      )}
    </motion.button>
  );
} 