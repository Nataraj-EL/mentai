"use client";

import React, { useState } from 'react';

type Quiz = {
  question: string;
  options: string[];
  correct_answer: string;
};

type Props = {
  quiz: Quiz[];
};

const QuizSection: React.FC<Props> = ({ quiz }) => {
  const [selected, setSelected] = useState<{ [key: number]: string }>({});
  const [showResult, setShowResult] = useState(false);

  const handleSelect = (qIdx: number, option: string) => {
    setSelected({ ...selected, [qIdx]: option });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setShowResult(true);
  };

  return (
    <form onSubmit={handleSubmit} className="bg-gray-50 p-4 rounded shadow mb-6">
      <h3 className="text-xl font-semibold mb-4">Quiz</h3>
      {quiz.map((q, idx) => (
        <div key={idx} className="mb-4">
          <p className="font-medium mb-2">{q.question}</p>
          <div className="space-y-1">
            {q.options.map((opt, oIdx) => (
              <label key={oIdx} className="block">
                <input
                  type="radio"
                  name={`q${idx}`}
                  value={opt}
                  checked={selected[idx] === opt}
                  onChange={() => handleSelect(idx, opt)}
                  className="mr-2"
                  disabled={showResult}
                />
                {opt}
                {showResult && selected[idx] === opt && (
                  <span className={
                    opt === q.correct_answer
                      ? 'text-green-600 ml-2'
                      : 'text-red-600 ml-2'
                  }>
                    {opt === q.correct_answer ? '✔' : '✗'}
                  </span>
                )}
              </label>
            ))}
          </div>
        </div>
      ))}
      {!showResult && (
        <button type="submit" className="bg-blue-600 text-white py-2 px-4 rounded">
          Submit
        </button>
      )}
      {showResult && (
        <div className="mt-4 font-semibold">
          Score: {quiz.filter((q, idx) => selected[idx] === q.correct_answer).length} / {quiz.length}
        </div>
      )}
    </form>
  );
};

export default QuizSection; 