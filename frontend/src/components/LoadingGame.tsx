"use client"
import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface Question {
  id: number;
  snippet: string;
  options: string[];
  answer: string;
  explanation: string;
}

interface LanguageQuestions {
  [language: string]: Question[];
}

const QUESTION_BANK: LanguageQuestions = {
  python: [
    {
      id: 1,
      snippet: "def greet(name)\n    print(\"Hello \" + name)",
      options: [
        "A) Add a colon : after greet(name)",
        "B) Change def to function",
        "C) Replace + with &"
      ],
      answer: "A) Add a colon : after greet(name)",
      explanation: "In Python, colons are mandatory to initiate compound statements like functions, loops, and conditionals. Missing them raises a SyntaxError!"
    },
    {
      id: 2,
      snippet: "my_list = [1, 2, 3]\nvalue = my_list[1.5]",
      options: [
        "A) Change my_list to a tuple",
        "B) Use an integer index like my_list[1] or my_list[2]",
        "C) Use curly brackets my_list{1.5}"
      ],
      answer: "B) Use an integer index like my_list[1] or my_list[2]",
      explanation: "Python list indices must strictly be integers or slices, not floats. Using a decimal float raises a TypeError!"
    },
    {
      id: 3,
      snippet: "numbers = [1, 2]\nnumbers.append(3, 4)",
      options: [
        "A) Use numbers.extend([3, 4]) or make separate append calls",
        "B) Change append to add",
        "C) Re-declare numbers as a dictionary"
      ],
      answer: "A) Use numbers.extend([3, 4]) or make separate append calls",
      explanation: "The append() method accepts exactly one item to add to the list. To add multiple items, you must use extend() with an array argument."
    }
  ],
  java: [
    {
      id: 1,
      snippet: "String str1 = new String(\"hello\");\nif (str1 == \"hello\") {\n    System.out.println(\"Match!\");\n}",
      options: [
        "A) Change == to str1.equals(\"hello\")",
        "B) Remove the parentheses around the if condition",
        "C) Change String to string (lowercase)"
      ],
      answer: "A) Change == to str1.equals(\"hello\")",
      explanation: "In Java, the == operator compares heap memory references, not value strings. To compare the character contents, str1.equals() must be used."
    },
    {
      id: 2,
      snippet: "int arr = new int[5];",
      options: [
        "A) Change int arr to int[] arr",
        "B) Change new int[5] to new array(5)",
        "C) Remove the new keyword"
      ],
      answer: "A) Change int arr to int[] arr",
      explanation: "In Java, array type declarations require square brackets (e.g., int[] or int arr[]). Declaring it as 'int arr' raises a type mismatch compilation error."
    },
    {
      id: 3,
      snippet: "public class Main {\n    public void show() {\n        System.out.println(\"Java\");\n    }\n    public static void main(String[] args) {\n        show();\n    }\n}",
      options: [
        "A) Change public class Main to static class Main",
        "B) Declare show() as static (e.g., public static void show()) or instantiate Main",
        "C) Remove the show() call"
      ],
      answer: "B) Declare show() as static (e.g., public static void show()) or instantiate Main",
      explanation: "Non-static methods exist on class instances. You cannot call them directly from a static block like main() without instantiating Main first or marking the method static."
    }
  ],
  javascript: [
    {
      id: 1,
      snippet: "const total = 100;\ntotal = total + 50;\nconsole.log(total);",
      options: [
        "A) Replace const with let or var",
        "B) Remove the console.log statement",
        "C) Change total + 50 to total += 50"
      ],
      answer: "A) Replace const with let or var",
      explanation: "Variables declared with const are block-scoped constants and cannot be re-assigned. Modifying them raises a TypeError at runtime!"
    },
    {
      id: 2,
      snippet: "const data = [];\nif (typeof data === 'array') {\n    console.log('Got an array');\n}",
      options: [
        "A) Use Array.isArray(data)",
        "B) Change === to ==",
        "C) Change 'array' to 'list'"
      ],
      answer: "A) Use Array.isArray(data)",
      explanation: "In JavaScript, arrays are categorized under the primitive type 'object'. Thus, typeof [] returns 'object'. Use Array.isArray() to correctly check for array structures."
    },
    {
      id: 3,
      snippet: "function fetchUserData() {\n    const user = await API.get('/user');\n    console.log(user);\n}",
      options: [
        "A) Add the async keyword before function (e.g., async function)",
        "B) Remove the await keyword",
        "C) Wrap API.get in quotes"
      ],
      answer: "A) Add the async keyword before function (e.g., async function)",
      explanation: "The await keyword is strictly permitted only within async functions. Omitting async raises a SyntaxError during parsing."
    }
  ],
  rust: [
    {
      id: 1,
      snippet: "fn main() {\n    let x = 5;\n    x = 10;\n    println!(\"{}\", x);\n}",
      options: [
        "A) Declare x as mutable using let mut x = 5;",
        "B) Remove println!",
        "C) Replace fn main() with void main()"
      ],
      answer: "A) Declare x as mutable using let mut x = 5;",
      explanation: "In Rust, all variables are strictly immutable by default to ensure thread safety. Mark variables mutable using the 'mut' keyword if they need re-assignment."
    },
    {
      id: 2,
      snippet: "fn main() {\n    let message = \"Hello\";\n    println!(message);\n}",
      options: [
        "A) Use println!(\"{}\", message);",
        "B) Change let to var",
        "C) Remove the exclamation mark !"
      ],
      answer: "A) Use println!(\"{}\", message);",
      explanation: "The println! macro strictly expects a string literal format argument. Passing a dynamic variable directly without format brackets causes a compilation error."
    },
    {
      id: 3,
      snippet: "fn add(a: i32, b: i32) {\n    a + b\n}",
      options: [
        "A) Specify the return type (e.g., fn add(a: i32, b: i32) -> i32)",
        "B) Add a semicolon after a + b",
        "C) Put brackets around a + b"
      ],
      answer: "A) Specify the return type (e.g., fn add(a: i32, b: i32) -> i32)",
      explanation: "Rust functions that return values require the return arrow -> type signature. Leaving it empty implicitly returns (), causing type mismatches."
    }
  ],
  cpp: [
    {
      id: 1,
      snippet: "#include <iostream>\nint main() {\n    std::cout << \"Welcome\" std::endl;\n    return 0;\n}",
      options: [
        "A) Insert stream insertion operator << before std::endl",
        "B) Change std::cout to printf",
        "C) Remove standard namespace std"
      ],
      answer: "A) Insert stream insertion operator << before std::endl",
      explanation: "Stream chaining in C++ requires standard insertion operators (<<) between all expressions. Omitting them throws a compiler parse error."
    },
    {
      id: 2,
      snippet: "int x = 10;\nint* ptr = x;",
      options: [
        "A) Assign the address of x using int* ptr = &x;",
        "B) Change int* to int",
        "C) Change ptr to &ptr"
      ],
      answer: "A) Assign the address of x using int* ptr = &x;",
      explanation: "Pointers (int*) hold memory addresses, not direct integers. You must use the address-of operator (&) to retrieve the location of x."
    },
    {
      id: 3,
      snippet: "class Box {\n    int width;\n}",
      options: [
        "A) Add a semicolon ; after the closing curly brace of the class",
        "B) Change class to struct",
        "C) Make width static"
      ],
      answer: "A) Add a semicolon ; after the closing curly brace of the class",
      explanation: "In C++, class and struct definitions must be terminated with a semicolon after the closing brace. Missing them triggers standard compiler syntax errors."
    }
  ],
  sql: [
    {
      id: 1,
      snippet: "SELECT department, AVG(salary)\nFROM employees\nWHERE AVG(salary) > 50000\nGROUP BY department;",
      options: [
        "A) Use HAVING clause instead of WHERE for aggregates (HAVING AVG(salary) > 50000)",
        "B) Remove GROUP BY",
        "C) Change SELECT to GET"
      ],
      answer: "A) Use HAVING clause instead of WHERE for aggregates (HAVING AVG(salary) > 50000)",
      explanation: "SQL evaluations execute standard row filters (WHERE) *before* rows are aggregated. To filter aggregated results, the HAVING clause must be evaluated after GROUP BY."
    },
    {
      id: 2,
      snippet: "SELECT id name FROM users;",
      options: [
        "A) Add a comma between id and name (id, name)",
        "B) Remove FROM users",
        "C) Put id in quotes"
      ],
      answer: "A) Add a comma between id and name (id, name)",
      explanation: "Querying multiple columns requires separate projections split by commas. Omitting the comma tells SQL to treat 'name' as a column alias for 'id', leading to errors."
    },
    {
      id: 3,
      snippet: "SELECT * FROM orders WHERE status = NULL;",
      options: [
        "A) Use IS NULL operator (WHERE status IS NULL)",
        "B) Change status to null status",
        "C) Use status == NULL"
      ],
      answer: "A) Use IS NULL operator (WHERE status IS NULL)",
      explanation: "In SQL, NULL is treated as the absence of data, meaning comparisons using the standard = operator evaluate to UNKNOWN. To check for empty records, use IS NULL."
    }
  ],
  mongodb: [
    {
      id: 1,
      snippet: "db.users.updateOne(\n  { email: 'user@domain.com' },\n  { status: 'active' }\n);",
      options: [
        "A) Wrap field updates inside the $set modifier",
        "B) Remove the email selector filter",
        "C) Change updateOne to updateRow"
      ],
      answer: "A) Wrap field updates inside the $set modifier",
      explanation: "In MongoDB, update queries expect update modifier operators (like $set). Passing direct keys without $set replaces the entire document structure, raising errors in updateOne."
    },
    {
      id: 2,
      snippet: "db.users.find({ age: { >: 21 } });",
      options: [
        "A) Use query operator $gt (e.g., age: { $gt: 21 })",
        "B) Remove the braces around age",
        "C) Change find to query"
      ],
      answer: "A) Use query operator $gt (e.g., age: { $gt: 21 })",
      explanation: "MongoDB queries use structured BSON operators rather than raw mathematical symbols. Use the Greater Than ($gt) operator inside query selectors."
    },
    {
      id: 3,
      snippet: "db.users.find({ roles: 'admin', roles: 'editor' });",
      options: [
        "A) Use the $all operator or $and condition",
        "B) Remove role criteria",
        "C) Re-index collections"
      ],
      answer: "A) Use the $all operator or $and condition",
      explanation: "Having duplicate key entries inside single JavaScript queries overwrites previous selections. To query for arrays holding multiple elements, utilize the $all operator."
    }
  ],
  react: [
    {
      id: 1,
      snippet: "const [count, setCount] = useState(0);\nfunction increment() {\n    count = count + 1;\n}",
      options: [
        "A) Call the state setter function (e.g., setCount(count + 1))",
        "B) Remove count declaration",
        "C) Use count++ directly"
      ],
      answer: "A) Call the state setter function (e.g., setCount(count + 1))",
      explanation: "React relies on immutable state structures. Re-assigning variables directly bypasses React's virtual DOM reconciliation and fails to trigger a view re-render."
    },
    {
      id: 2,
      snippet: "return (\n    <div class=\"container\">\n        <h1>Title</h1>\n    </div>\n);",
      options: [
        "A) Replace class with className in HTML/JSX tags",
        "B) Remove the div tag entirely",
        "C) Wrap container inside quotes only"
      ],
      answer: "A) Replace class with className in HTML/JSX tags",
      explanation: "JSX compiles directly into JavaScript function parameters. Because 'class' is a reserved OOP keyword in JavaScript, class names are specified via className."
    },
    {
      id: 3,
      snippet: "if (isLoading) {\n    const [data, setData] = useState(null);\n}",
      options: [
        "A) Move the hook declaration to the top-level of the functional component",
        "B) Remove the useState parameters",
        "C) Re-declare hooks as class properties"
      ],
      answer: "A) Move the hook declaration to the top-level of the functional component",
      explanation: "React Hooks rely on a stable, index-based execution order. Calling hooks conditionally inside if blocks throws an invariant compilation error."
    }
  ],
  html: [
    {
      id: 1,
      snippet: "<img src=\"avatar.png\">",
      options: [
        "A) Add an alt attribute to provide alternate text for accessibility",
        "B) Add an unclosed tag",
        "C) Put img inside script tags"
      ],
      answer: "A) Add an alt attribute to provide alternate text for accessibility",
      explanation: "HTML5 images require descriptive 'alt' attributes to meet web accessibility guidelines and ensure screen-readers can explain the context."
    },
    {
      id: 2,
      snippet: "<link href=\"styles.css\">",
      options: [
        "A) Add a rel=\"stylesheet\" attribute",
        "B) Use src instead of href",
        "C) Close tag with </link>"
      ],
      answer: "A) Add a rel=\"stylesheet\" attribute",
      explanation: "The link tag loads resource relationships. To parse stylesheet assets, browsers rely on rel='stylesheet' to execute render formatting."
    },
    {
      id: 3,
      snippet: "<div style=\"background-color: red; font-size: 20px;\">",
      options: [
        "A) Safe standard HTML, but when compiling under React JSX, style must be passed as an object (style={{backgroundColor: 'red', fontSize: 20}})",
        "B) Use style=color:red",
        "C) Remove background-color"
      ],
      answer: "A) Safe standard HTML, but when compiling under React JSX, style must be passed as an object (style={{backgroundColor: 'red', fontSize: 20}})",
      explanation: "Standard style blocks work in raw HTML, but React JSX expects style variables formatted as CamelCase camelObjects."
    }
  ],
  css: [
    {
      id: 1,
      snippet: "body {\n    background: color red;\n}",
      options: [
        "A) Change background: color red; to background-color: red; or background: red;",
        "B) Change background to back",
        "C) Remove the curly braces {}"
      ],
      answer: "A) Change background: color red; to background-color: red; or background: red;",
      explanation: "In CSS, background-color properties accept direct color values. background: color red is a syntax error."
    },
    {
      id: 2,
      snippet: ".card {\n    margin: 10px 20px 30px;\n}",
      options: [
        "A) This is valid! It sets margin-top: 10px, left/right: 20px, and bottom: 30px",
        "B) Invalid, CSS margins only accept 2 or 4 parameters",
        "C) Semicolon is disallowed here"
      ],
      answer: "A) This is valid! It sets margin-top: 10px, left/right: 20px, and bottom: 30px",
      explanation: "CSS 3-value margins represent top, left/right (symmetric), and bottom dimensions successfully."
    },
    {
      id: 3,
      snippet: ".container {\n    display: flex;\n    justify-items: center;\n}",
      options: [
        "A) Change justify-items to justify-content to align flex-items horizontally",
        "B) Remove display: flex",
        "C) Change display: flex to display: block"
      ],
      answer: "A) Change justify-items to justify-content to align flex-items horizontally",
      explanation: "Flexbox aligns content distribution via justify-content. justify-items is ignored inside standard flex parents."
    }
  ],
  general: [
    {
      id: 1,
      snippet: "for (let i = 0; i <= array.length; i++) {\n    console.log(array[i]);\n}",
      options: [
        "A) Change i <= array.length to i < array.length to avoid Out of Bounds errors",
        "B) Change let to const",
        "C) Change i++ to i--"
      ],
      answer: "A) Change i <= array.length to i < array.length to avoid Out of Bounds errors",
      explanation: "Arrays are 0-indexed structures. The last index resides at length - 1. Loop indices evaluating i == length attempt index out of bounds, returning undefined or crashing."
    },
    {
      id: 2,
      snippet: "function checkActive(status) {\n    if (status = 'active') {\n        return true;\n    }\n    return false;\n}",
      options: [
        "A) Use comparison operators (== or ===) instead of assignment (=)",
        "B) Remove the status parameter",
        "C) Change if to when"
      ],
      answer: "A) Use comparison operators (== or ===) instead of assignment (=)",
      explanation: "Using the assignment operator (=) inside conditionals assigns status to 'active' which evaluates to truthy, making the condition evaluate true under all scenarios."
    },
    {
      id: 3,
      snippet: "let user = null;\nconsole.log(user.name);",
      options: [
        "A) Safeguard properties using optional chaining (user?.name) or null checks",
        "B) Remove console.log",
        "C) Change let to const"
      ],
      answer: "A) Safeguard properties using optional chaining (user?.name) or null checks",
      explanation: "Accessing sub-properties of null or undefined references throws a NullPointerException / TypeError at runtime, halting execution."
    }
  ]
};

interface LoadingGameProps {
  topic: string;
  onComplete?: () => void;
}

export const LoadingGame: React.FC<LoadingGameProps> = ({ topic, onComplete }) => {
  const [currentQuestions, setCurrentQuestions] = useState<Question[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [score, setScore] = useState(0);
  const [showExplanation, setShowExplanation] = useState(false);
  const [isCorrect, setIsCorrect] = useState(false);
  const [gameFinished, setGameFinished] = useState(false);

  // Derive and filter questions based on the topic matching registry keys
  useEffect(() => {
    const topicLower = (topic || "").toLowerCase().trim();
    let langKey = "general";

    if (topicLower.includes("python")) langKey = "python";
    else if (topicLower.includes("java") && !topicLower.includes("script")) langKey = "java";
    else if (topicLower.includes("javascript") || topicLower.includes("js") || topicLower.includes("node")) langKey = "javascript";
    else if (topicLower.includes("rust")) langKey = "rust";
    else if (topicLower.includes("cpp") || topicLower.includes("c++")) langKey = "cpp";
    else if (topicLower.includes("sql")) langKey = "sql";
    else if (topicLower.includes("mongo")) langKey = "mongodb";
    else if (topicLower.includes("react")) langKey = "react";
    else if (topicLower.includes("html")) langKey = "html";
    else if (topicLower.includes("css")) langKey = "css";

    const questions = QUESTION_BANK[langKey] || QUESTION_BANK["general"];
    setCurrentQuestions(questions);
    setCurrentIndex(0);
    setSelectedOption(null);
    setShowExplanation(false);
    setScore(0);
    setGameFinished(false);
  }, [topic]);

  const handleOptionClick = (option: string) => {
    if (selectedOption) return; // Disallow double voting
    setSelectedOption(option);
    
    const currentQ = currentQuestions[currentIndex];
    const correct = currentQ.answer === option;
    setIsCorrect(correct);
    if (correct) {
      setScore(prev => prev + 1);
    }
    setShowExplanation(true);

    // Auto advance after 4.5 seconds
    setTimeout(() => {
      setSelectedOption(null);
      setShowExplanation(false);
      if (currentIndex === currentQuestions.length - 1) {
        if (onComplete) {
          onComplete();
        } else {
          setGameFinished(true);
        }
      } else {
        setCurrentIndex(prev => prev + 1);
      }
    }, 4500);
  };

  if (currentQuestions.length === 0) return null;

  if (gameFinished) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="w-full max-w-xl bg-white border border-gray-200 rounded-xl p-8 shadow-md text-center text-[#111827]"
      >
        <div className="mb-6 flex flex-col items-center">
          <div className="w-12 h-12 border-4 border-[#06B6D4]/30 border-t-[#06B6D4] rounded-full animate-spin mb-6" />
          <h3 className="text-xl font-bold text-gray-900 mb-2">Finalizing Course Creation</h3>
          <p className="text-sm text-gray-500 max-w-sm leading-relaxed mb-3">
            Bug Hunter speed-run complete. Score: <strong className="text-[#06B6D4]">{score}</strong> / {currentQuestions.length}.
          </p>
          <p className="text-sm text-gray-600 max-w-md leading-relaxed">
            Please wait while we put together your custom university-grade syllabus and coding modules. Your course will load automatically.
          </p>
        </div>
      </motion.div>
    );
  }

  const currentQuestion = currentQuestions[currentIndex];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="w-full max-w-xl bg-white border border-gray-200 rounded-xl p-6 shadow-md relative overflow-hidden text-[#111827]"
    >

      {/* Header Info */}
      <div className="flex justify-between items-center mb-4 border-b border-gray-200 pb-3">
        <div>
          <span className="bg-[#06B6D4]/10 text-[#06B6D4] font-mono text-xs font-semibold px-2.5 py-1 rounded-full uppercase tracking-wider">
            Bug Hunter Mini-Game
          </span>
        </div>
        <div className="text-right">
          <span className="text-sm font-mono font-medium text-gray-500">
            Score: <strong className="text-[#111827] text-base">{score}</strong> / {currentQuestions.length}
          </span>
        </div>
      </div>

      <h3 className="text-lg font-bold mb-3 text-[#111827] flex items-center">
        Challenge {currentIndex + 1}: Find and Fix the Bug!
      </h3>

      {/* Code Snippet Sandbox Preview */}
      <div className="bg-[#111827] border border-gray-800 rounded-lg p-4 mb-4 overflow-x-auto relative shadow-sm">
        <div className="absolute top-2 right-3 text-[10px] text-gray-500 font-mono select-none">CODE WRAPPER</div>
        <pre className="font-mono text-sm text-green-400 whitespace-pre leading-relaxed select-text">
          {currentQuestion.snippet}
        </pre>
      </div>

      {/* Options Selection Box */}
      <div className="space-y-2.5">
        {currentQuestion.options.map((option, idx) => {
          const isSelected = selectedOption === option;
          const isCorrectAns = currentQuestion.answer === option;

          let btnClass = "bg-white border-gray-200 text-gray-700 hover:bg-gray-50 hover:border-gray-300";
          
          if (selectedOption) {
            if (isSelected) {
              btnClass = isCorrect ? "bg-green-50 border-green-500 text-green-700 font-semibold" : "bg-red-50 border-red-500 text-red-700 font-semibold";
            } else if (isCorrectAns) {
              btnClass = "bg-green-50/50 border-green-500/30 text-green-700 font-medium";
            } else {
              btnClass = "opacity-40 bg-white border-gray-200 text-gray-400";
            }
          }

          return (
            <motion.button
              key={idx}
              whileHover={selectedOption ? {} : { scale: 1.015 }}
              whileTap={selectedOption ? {} : { scale: 0.985 }}
              onClick={() => handleOptionClick(option)}
              disabled={!!selectedOption}
              className={`w-full p-3 text-left rounded-xl border text-sm transition-all duration-200 flex items-start leading-relaxed ${btnClass}`}
            >
              <span className="inline-block mr-2 text-base select-none">
                {selectedOption ? (isSelected ? (isCorrect ? "✓" : "✗") : (isCorrectAns ? "✓" : "·")) : "·"}
              </span>
              {option}
            </motion.button>
          );
        })}
      </div>

      {/* Slide-out Explanation/Feedback Block */}
      <AnimatePresence>
        {showExplanation && (
          <motion.div
            initial={{ opacity: 0, height: 0, marginTop: 0 }}
            animate={{ opacity: 1, height: "auto", marginTop: 16 }}
            exit={{ opacity: 0, height: 0, marginTop: 0 }}
            className={`border rounded-lg p-4 text-xs leading-relaxed overflow-hidden ${
              isCorrect ? "bg-green-50 border-green-200 text-green-800" : "bg-red-50 border-red-200 text-red-800"
            }`}
          >
            <div className="flex items-center mb-1.5 font-bold text-sm">
              <span className="text-base mr-1.5">{isCorrect ? "Correct!" : "Let's learn!"}</span>
            </div>
            <p className="font-medium mb-1.5">{currentQuestion.explanation}</p>
            <p className="text-[10px] text-gray-400 italic border-t border-gray-200/50 pt-1 mt-1 font-mono">
              Auto-advancing to the next bug in 4 seconds...
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};
export default LoadingGame;
