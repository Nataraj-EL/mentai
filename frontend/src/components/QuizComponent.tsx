import React, { useState } from "react";

type QuizQuestion = {
  question: string;
  options: string[];
  answer: string;
};

type Props = {
  quiz: QuizQuestion[];
};

const QuizComponent: React.FC<Props> = ({ quiz }) => {
  const [selected, setSelected] = useState<(number | null)[]>(Array(quiz.length).fill(null));
  const [submitted, setSubmitted] = useState(false);

  const handleSelect = (qIdx: number, oIdx: number) => {
    if (!submitted) {
      setSelected((prev) => {
        const copy = [...prev];
        copy[qIdx] = oIdx;
        return copy;
      });
    }
  };

  const handleSubmit = () => {
    setSubmitted(true);
  };

  const getScore = () => {
    let score = 0;
    quiz.forEach((q, i) => {
      if (selected[i] !== null && q.options[selected[i]!] === q.answer) score++;
    });
    return score;
  };

  return (
    <div className="bg-white p-6 rounded shadow">
      {submitted && (
        <h2 className="text-xl font-semibold text-center my-4 text-green-600">
          You scored {getScore()}/{quiz.length}
        </h2>
      )}
      <form
        onSubmit={e => {
          e.preventDefault();
          handleSubmit();
        }}
        className="space-y-8"
      >
        {quiz.map((q, qIdx) => (
          <div key={qIdx} className="mb-4">
            <div className="font-semibold mb-2">
              {qIdx + 1}. {q.question}
            </div>
            <div className="grid grid-cols-1 gap-2">
              {q.options.map((opt, oIdx) => {
                const isSelected = selected[qIdx] === oIdx;
                const isCorrect = submitted && opt === q.answer;
                return (
                  <label
                    key={oIdx}
                    className={`flex items-center p-2 rounded cursor-pointer border transition
                      ${isSelected ? 'border-blue-600 bg-blue-50' : 'border-gray-200'}
                      ${submitted && isCorrect ? 'border-green-600 bg-green-50' : ''}
                    `}
                  >
                    <div
                      className={`border rounded-full w-4 h-4 flex items-center justify-center mr-2
                        ${isSelected ? 'bg-blue-500 border-blue-600' : 'border-gray-400'}
                      `}
                    >
                      {isSelected && <div className="w-2 h-2 bg-white rounded-full" />}
                    </div>
                    <input
                      type="radio"
                      name={`q${qIdx}`}
                      checked={isSelected}
                      onChange={() => handleSelect(qIdx, oIdx)}
                      className="hidden"
                      disabled={submitted}
                    />
                    <span className="text-gray-800">{opt}</span>
                  </label>
                );
              })}
            </div>
            {submitted && (
              <div className="mt-2 text-green-600">
                Correct answer: {q.answer}
              </div>
            )}
          </div>
        ))}
        {!submitted && (
          <button
            type="submit"
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition w-full mt-4"
          >
            Submit
          </button>
        )}
      </form>
    </div>
  );
};

export default QuizComponent; 