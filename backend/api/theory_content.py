
# Detailed Theory Content Maps
# STRICTLY NO GENERIC FILLER. NO PYTHON IN NON-PYTHON.

# 1. PYTHON
python_theory = {
    1: """# Module 1: Python Introduction & Ecosystem
## 1. The Python Philosophy (PEP 20)
Python is defined by the "Zen of Python". It uses indentation for block structure, prioritizing readability and explicitness over complex syntax.
*   **Interpreted**: Code executes strictly line-by-line via the CPython reference implementation.
*   **Dynamic**: Types are resolved at runtime.
*   **Managed**: Automatic memory management via Reference Counting (primary) and Garbage Collection (cyclic).

## 2. Setting Up the Environment
To develop professionally, you need a robust environment:
1.  **Interpreter**: The `python` binary converts source to bytecode.
2.  **Package Manager**: `pip` facilitates installing third-party libraries from PyPI.
3.  **Virtual Environments**: `venv` is crucial to isolate project dependencies and avoid version conflicts.

## 3. Execution Flow
The journey of a Python script: `Source (.py)` -> `Compiler` -> `Bytecode (.pyc)` -> `PVM (Python Virtual Machine)`.
Understanding this flow helps identify why syntax errors are caught before runtime, while logical errors crash during execution.
""",
    2: """# Module 2: Variables & Memory Data Models
## 1. Everything is an Object
In Python, variables are not boxes that hold data; they are *labels* (references) pointing to objects in heap memory.
When you write `x = 10`, Python creates an integer object `10` at a specific address (e.g., `0x123`) and binds the name `x` to it.

## 2. Primitive vs Reference Types
*   **Immutable**: `int`, `float`, `str`, `tuple`. Modifying them creates a *new* object at a new address.
*   **Mutable**: `list`, `dict`, `set`. Modifying them changes the object *in-place*, affecting all references to it.

## 3. Type System
Python is **Strongly Typed** (no implicit coercion like JS—`"1"+1` raises TypeError) but **Dynamically Typed** (type checks happen at runtime).
This design prevents silent errors but requires disciplined testing.
""",
    3: """# Module 3: Control Flow & Logic
## 1. Branching Logic
The `if-elif-else` construct relies on "Truthiness".
*   Falsy values: `0`, `""`, `[]`, `None`, `False`.
*   Truthy values: Non-empty structures, non-zero numbers.
Contextual truthiness allows concise checks like `if my_list:` instead of `if len(my_list) > 0:`.

## 2. Advanced Iteration
*   **For Loops**: Python loops iterate over *iterables* (streams of data), not just counting numbers. You can loop over files, lists, or network sockets directly.
*   **While Loops**: Used for state-based iteration where the number of steps is unknown.
*   **Break/Continue**: Fine-grained loop control to exit early or skip steps.

## 3. Structural Pattern Matching (Python 3.10+)
The new `match-case` statement allows matching against data structure patterns, not just values.
It can deconstruct sequences (e.g., `case [x, y]:`) and bind variables inside the condition.
""",
    4: """# Module 4: Functions & Scope
## 1. First-Class Functions
In Python, functions are first-class citizens. They can be:
*   Assigned to variables (`f = print`).
*   Passed as arguments to other functions (Higher-Order Functions).
*   Returned from other functions (Closures).

## 2. Scope (LEGB Rule)
Variable resolution follows a strict hierarchy:
*   **L**ocal: Inside the current function.
*   **E**nclosing: Inside any nested parent functions.
*   **G**lobal: At the module level.
*   **B**uilt-in: Python standard names (`len`, `str`).

## 3. Arguments & Parameters
*   **Positional vs Keyword**: `func(10, b=20)`. Keyword arguments improve readability.
*   **Default Values**: Evaluated *once* at definition time. (Tip: Never use mutable defaults like `[]`).
*   **`*args` and `**kwargs`**: Allow functions to accept variable numbers of positional and keyword arguments.
""",
    5: """# Module 5: Data Structures (Lists, Tuples, Sets)
## 1. Lists (Dynamic Arrays)
Lists are the workhorse of Python. They are dynamic arrays of references.
*   **Performance**: Append is amortized O(1). Insert/Delete at the start is O(n) because all subsequent items must shift.
*   **Slicing**: `[start:stop:step]` offers powerful, concise manipulation.

## 2. Tuples (Immutable Sequences)
Tuples are faster and lighter than lists. They are used for fixed collections (coordinates, DB records).
*   **Hashability**: Unlike lists, tuples containing immutable items can be used as Dictionary keys.

## 3. Sets (Hash Sets)
Unordered collections of unique elements based on hash tables.
*   **Operations**: Union `|`, Intersection `&`, Difference `-` are highly optimized (O(1) average case).
*   **Use Case**: Deduplicating lists or fast membership testing (`if id in my_set`).
""",
    6: """# Module 6: Dictionaries & Hash Maps
## 1. The Engine of Python
Dictionaries are Python's most important structure. They drive namespaces, classes, and variable lookups.
*   **Keys**: Must be hashable (immutable) and unique.
*   **Values**: Can be any object.

## 2. Internal Mechanics
Dicts use a **Hash Table** with open addressing.
1.  Python computes `hash(key)`.
2.  It uses the hash to find a slot in the table.
3.  Collisions are handled via probing. Modern Python dicts are also ordered by insertion (since 3.7).

## 3. Dictionary Comprehensions
Concise syntax for creating dictionaries:
`{k: v for k, v in data if v > 0}`
This is more readable and faster than a for-loop with `dict[k] = v`.
""",
    7: """# Module 7: Object-Oriented Programming (OOP)
## 1. Classes & Instances
*   `class`: The blueprint defining attributes and behaviors.
*   `self`: Explicit reference to the specific instance being operated on.
*   `__init__`: The initializer (constructor) that sets up initial state.

## 2. The Four Pillars
1.  **Encapsulation**: Using `_protected` and `__private` naming conventions to hint access control.
2.  **Inheritance**: `class Child(Parent)` allows code reuse.
3.  **Polymorphism**: Dynamic dispatch via Duck Typing ("If it walks like a duck...").
4.  **Abstraction**: Hiding complex implementations behind simple interfaces.

## 3. Magic Methods (Dunder Methods)
Python's "Hooks" that let you customize object behavior:
*   `__str__` / `__repr__`: String representation.
*   `__add__`: Operator overloading (e.g., `obj1 + obj2`).
*   `__len__`: Custom length behavior.
""",
    8: """# Module 8: Advanced OOP & Decorators
## 1. Inheritance Patterns
*   **MRO (Method Resolution Order)**: Python uses the C3 Linearization algorithm to determine the order of method lookup in complex multiple inheritance scenarios.
*   **Mixins**: Small classes designed to add specific features to a class hierarchy without implying an "is-a" relationship.

## 2. Decorators
Decorators are functions that wrap other functions to modify their behavior without changing logic.
*   Syntax: `@my_decorator`.
*   Mechanism: `func = decorator(func)`.
*   Use cases: Logging, Authorization checks, Timing execution, Caching (Memoization).

## 3. Properties
Using `@property` allows you to control attribute access (Getters/Setters) pythonically.
It lets you start with a public attribute and later add validation logic without breaking the API.
""",
    9: """# Module 9: Error Handling & File I/O
## 1. The EAFP Principle
"Easier to Ask Forgiveness than Permission".
In Python, it is idiomatic to try an operation and catch the error, rather than checking `if exists` beforehand.
This avoids race conditions and is generally faster.

## 2. Exception Hierarchy
All errors inherit from `BaseException`.
*   Best Practice: Catch specific errors (`ValueError`, `FileNotFoundError`), never bare `except:`.
*   `raise`: Re-raising exceptions to propagate errors up the stack.

## 3. Context Managers
The `with` statement ensures resources (files, sockets, locks) are released deterministically.
*   It automatically calls `__enter__` and `__exit__`.
*   Crucial for preventing memory leaks and file lock issues.
""",
    10: """# Module 10: Advanced Libraries & Deployment
## 1. The Standard Library
Python is "Batteries Included".
*   `os`, `sys`: For system interaction and cli arguments.
*   `json`, `csv`: For robust data serialization.
*   `itertools`, `collections`: High-performance functional tools and containers.

## 2. Virtual Environments & Pip
Managing dependencies with `requirements.txt` or `Pipfile`.
*   Isolating environments prevents "Dependency Hell" where Project A needs Lib v1.0 and Project B needs Lib v2.0.

## 3. Deployment Concepts
*   **Packaging**: Creating `setup.py` or wheels.
*   **Logging**: Using the `logging` module instead of `print` for production apps.
*   **Testing**: Writing Unit Tests with `unittest` or `pytest` to ensure code reliability.
"""
}

# 2. JAVA
java_theory = {
    1: """# Module 1: Java Ecosystem & JVM
## 1. Write Once, Run Anywhere
Java's core promise relies on the JVM (Java Virtual Machine). Source code `.java` compiles to Bytecode `.class`, which the JVM interprets or JIT-compiles to native machine code for the specific OS.
*   **JDK (Development Kit)**: Compiler (`javac`), JRE, and tools.
*   **JRE (Runtime Environment)**: Libraries + JVM.
*   **JVM**: The engine that runs the code.

## 2. Class Structure
Every line of code in Java must live inside a class.
`public class Main { ... }`.
The filename must match the public class name. This enforcement ensures organized project structures.

## 3. Entry Point
`public static void main(String[] args)`.
*   `public`: Accessible by the JVM.
*   `static`: No object instance needed to start.
*   `void`: Returns nothing to the OS.
""",
    2: """# Module 2: Primitives & Variables
## 1. Strong Typing
Java enforces strict types. You cannot assign a String to an int.
*   **Primitives** (Stack allocated): `int`, `double`, `boolean`, `char`, `byte`, `short`, `long`, `float`.
*   **Reference Types** (Heap allocated): Arrays, Objects, Strings.

## 2. Memory Model (Stack vs Heap)
*   User-defined objects (new Student()) live on the **Heap**.
*   Method calls and local primitive variables live on the **Stack**.
*   A variable `Student s` is a reference (pointer) on the stack pointing to the object on the heap.

## 3. Type Casting
*   **Widening**: Automatic (int -> long). Safe.
*   **Narrowing**: Manual `(int) myDouble`. Possible data loss.
Java requires explicit confirmation for dangerous casts.
""",
    3: """# Module 3: Control Flow
## 1. Conditional Logic
Java uses familiar C-style syntax: `if`, `else if`, `else`.
Key difference from C: The condition MUST be a boolean. `if(1)` is a compile-time error; `if(true)` is required.

## 2. Switch Expressions (Modern Java)
Traditional `switch` uses `case` and `break`.
Modern Java (14+) introduces `arrow syntax`:
`case Day.MONDAY -> System.out.println("Start");`
This prevents "fall-through" bugs and allows utilizing switch as an expression (returning a value).

## 3. Loops
*   `for(init; condition; update)`: Standard loop.
*   `for(Type item : collection)`: Enhanced for-loop (for-each) for iterating Arrays or Lists.
*   `while` / `do-while`: Condition-based iteration.
""",
    4: """# Module 4: Methods & Scope
## 1. Static vs Instance Methods
*   **Static**: Belongs to the class. Called as `Math.max()`. Cannot access instance variables (`this`).
*   **Instance**: Belongs to an object. Called as `myObj.method()`. Can access object state.

## 2. Pass-by-Value (Crucial Concept)
Java *always* passes by value.
*   For **primitives**, acts like a copy. Modifying the argument inside the method does not affect the original.
*   For **objects**, it passes a copy of the *reference*. Modifying fields works (`obj.x = 5`), but reassigning the reference (`obj = new Obj()`) does not affect the original caller.

## 3. Method Overloading
Multiple methods can have the same name but different parameter lists (signature).
The compiler decides which one to call at compile-time (Static Binding).
""",
    5: """# Module 5: Arrays & Strings
## 1. Arrays (Fixed Size)
`int[] arr = new int[5];`.
Once created, size is immutable.
Arrays are objects in Java, so they have a `.length` property (not a method).

## 2. String Immutability
Strings in Java are immutable.
`String s = "Hello"; s = s + " World";` creates a *new* String object. The old one is eventually garbage collected.
This allows the **String Constant Pool** optimization, saving memory by sharing identical string literals.

## 3. StringBuilder
For loop-heavy string concatenation, use `StringBuilder`.
It modifies the internal buffer in-place, avoiding O(n^2) memory copying overhead.
""",
    6: """# Module 6: OOP Part 1 - Classes
## 1. Object Lifecycle
1.  **Declaration**: `Student s;` (Allocates reference on stack, init null).
2.  **Instantiation**: `new` keyword allocates memory on Heap.
3.  **Initialization**: Constructor runs to set initial state.

## 2. Constructors
Special methods appearing as `ClassName()`.
*   Can be overloaded.
*   If no constructor is defined, Java provides a default "no-arg" constructor.
*   `this(...)` calls another constructor in the same class.

## 3. Access Modifiers
*   `private`: Only this class.
*   `default` (package-private): Same package.
*   `protected`: Same package + subclasses.
*   `public`: Everywhere.
""",
    7: """# Module 7: OOP Part 2 - Inheritance
## 1. The `extends` Keyword
Java supports single inheritance for classes.
`class Dog extends Animal`.
The subclass inherits all public/protected members of the superclass.

## 2. The `super` Keyword
Used to access the parent class.
*   `super()`: Calls parent constructor (Must be first line in child constructor).
*   `super.method()`: Calls parent implementation.

## 3. Method Overriding
Redefining a parent method in the child.
Annotation `@Override` ensures compile-time check that you are actually overriding (and not just misspelling) a method.
""",
    8: """# Module 8: Polymorphism & Abstraction
## 1. Polymorphism (Runtime)
Treating different objects as a common type.
`Animal a = new Dog(); a.makeSound();`
At runtime, the JVM looks up the *actual* object type (Dog) and calls Dog's `makeSound`. This is Dynamic Dispatch.

## 2. Abstract Classes
`abstract class Shape`. Cannot be instantiated directly.
Can contain both abstract methods (no body) and concrete methods.
Used when creating a template for subclasses.

## 3. Interfaces
`interface Playable`. Pure contracts.
*   Methods are implicitly public abstract.
*   Classes `implement` interfaces.
*   A class can implement *multiple* interfaces, solving the multiple-inheritance diamond problem via behaviour contract only.
""",
    9: """# Module 9: Exception Handling
## 1. Checked vs Unchecked
*   **Unchecked (RuntimeException)**: Logic errors (NullPointer, IndexOutOfBounds). Compiler does not force you to catch them. Fix your code.
*   **Checked (Exception)**: External failures (IOException, SQLException). Compiler *forces* you to `try-catch` or `throws`.

## 2. Try-Catch-Finally
*   `try`: Code that might explode.
*   `catch`: Handle specific exception types.
*   `finally`: Code that runs *no matter what* (cleanup).

## 3. Try-with-Resources (Java 7+)
`try (Scanner s = new Scanner(File)) { ... }`
Automatically calls `.close()` at the end. Best practice for I/O handling.
""",
    10: """# Module 10: Collections Framework
## 1. List Interface
Ordered collection.
*   `ArrayList`: Dynamic array. Fast access O(1), slow insert O(n).
*   `LinkedList`: Node chain. Fast insert O(1), slow access O(n).

## 2. Set & Map
*   `HashSet`: Unique items only. Unordered. O(1) ops.
*   `HashMap`: Key-Value relationships. keys are unique. O(1) ops.
*   `TreeMap`: Sorted keys (Red-Black tree). O(log n).

## 3. Streams API (Java 8+)
Functional programming for collections.
`list.stream().filter(e -> e > 10).map(e -> e * 2).collect(Collectors.toList());`
Declarative data processing pipeline.
"""
}

# 3. JAVASCRIPT
js_theory = {
    1: """# Module 1: JavaScript Environment
## 1. The Language of the Web
JavaScript is the only language that runs natively in the browser. Originally for simple scripts, it now powers full-stack apps via Node.js.
*   **Engine**: Apps run on V8 (Chrome), SpiderMonkey (Firefox), or JavaScriptCore (Safari).

## 2. Variables & Scoping
*   `var`: Function-scoped, hoisted (old school, avoid).
*   `let`: Block-scoped, reassignable (modern standard).
*   `const`: Block-scoped, non-reassignable (preferred).

## 3. Dynamic Typing
JS is loosely typed. A variable can hold a Number, then a String.
`typeof x` allows you to inspect types at runtime. Be careful of implicit coercion (`"5" - 1 = 4` but `"5" + 1 = "51"`).
""",
    2: """# Module 2: Primitives & Operators
## 1. Primitive Types
JS has 7 primitives: `String`, `Number`, `BigInt`, `Boolean`, `Symbol`, `undefined`, and `null`.
*   **Null vs Undefined**: `undefined` is "initialized but no value". `null` is "explicitly nothing".

## 2. Equality Operators
*   `==` (Loose): Coerces types before comparing (`5 == "5"` is true). **Avoid.**
*   `===` (Strict): Checks value AND type (`5 === "5"` is false). **Always use.**

## 3. Arithmetic & Math
JS follows IEEE 754 floating point logic.
`0.1 + 0.2 !== 0.3` (It's `0.30000000000000004`).
Math functions: `Math.floor()`, `Math.random()`, `Math.max()`.
""",
    3: """# Module 3: Control Flow & Loops
## 1. Conditionals
Standard `if (condition) { }` logic.
*   **Truthy/Falsy**: `0`, `""`, `null`, `undefined`, `NaN` are false. Everything else (including `[]` and `{}`) is true.

## 2. Switch Statements
Useful for multiple distinct value checks.
Remember to `break`, otherwise "fall-through" occurs (executing next cases).

## 3. Loops
*   `for`: Standard counter loop.
*   `for...of`: Modern loop for arrays/iterables (`for (const item of items)`).
*   `for...in`: Loops over object *keys* (rarely used for arrays).
""",
    4: """# Module 4: Functions & Scope
## 1. Function Declarations vs Expressions
*   **Declaration**: `function add(a,b) {}`. Hoisted to top of scope.
*   **Expression**: `const add = function(a,b) {}`. Not hoisted.

## 2. Arrow Functions (ES6)
Concise syntax: `const add = (a, b) => a + b`.
*   **Lexical `this`**: Arrow functions inherit `this` from the parent scope, they don't capture their own. Critical for callbacks.

## 3. Closures
A function remembers the variables from the scope where it was *created*, even if executed elsewhere.
Basis for data privacy and factory functions in JS.
""",
    5: """# Module 5: Arrays & JSON
## 1. Array Methods
JS arrays are powerful dynamic learning lists.
*   **Mutation**: `push`, `pop`, `shift`, `splice`.
*   **Access**: `arr[0]`.

## 2. Higher-Order Methods (Functional)
*   `map()`: Transform every element.
*   `filter()`: Select elements.
*   `reduce()`: Accumulate to single value.
*   `forEach()`: Side effects.

## 3. JSON (JavaScript Object Notation)
The universal data format.
*   `JSON.stringify(obj)`: Object to String.
*   `JSON.parse(str)`: String to Object.
*   Keys must be double-quoted strings.
""",
    6: """# Module 6: Objects & Classes
## 1. Object Literal Syntax
`const car = { make: "Toyota", model: "Corolla" }`.
*   Dynamic access: `car["make"]` allows using variables as keys.

## 2. The `this` Keyword
The most confusing part of JS. It refers to the *context* of execution.
*   In a method: The object.
*   In global: Window/Global.
*   In strict mode: undefined.

## 3. ES6 Classes
Syntactic sugar over prototypal inheritance.
`class Dog extends Animal { constructor() { super(); } }`.
Makes OOP patterns cleaner and more familiar to Java/C# devs.
""",
    7: """# Module 7: Async JavaScript (Promises)
## 1. The Event Loop
JS is single-threaded but non-blocking.
It offloads I/O to the browser/OS and runs the callback queue when the stack is empty.

## 2. Promises
An object representing a future value.
*   States: Pending, Fulfilled, Rejected.
*   `.then(data => ...).catch(err => ...)` chaining avoids "Callback Hell".

## 3. Async / Await
Modern syntax makes async code look synchronous.
`const data = await fetch(url);`
Must be used inside an `async function`.
""",
    8: """# Module 8: DOM Manipulation
## 1. The DOM Tree
The browser converts HTML into a tree of Objects (Document Object Model).
*   Selection: `document.getElementById`, `querySelector`.

## 2. Modifying Elements
*   `el.textContent`: Change text.
*   `el.style.color`: Change CSS.
*   `el.classList.add()`: Change classes.

## 3. Event Listeners
`el.addEventListener('click', callback)`.
*   **Event Bubbling**: Events travel up from target to root.
*   **Event Delegation**: putting one listener on a parent to handle multiple children.
""",
    9: """# Module 9: Node.js Basics
## 1. JS on the Server
Node.js is a runtime that allows JS to run outside the browser.
*   Access to File System (`fs`).
*   Direct Network Access (`http`).

## 2. Modules (CommonJS vs ES Modules)
*   CommonJS: `require()` and `module.exports` (legacy Node).
*   ESM: `import` and `export` (modern standard).

## 3. NPM (Node Package Manager)
The largest software registry.
`package.json` tracks dependencies. `npm install` brings in libraries like Express, React, etc.
""",
    10: """# Module 10: Final Project Patterns
## 1. Clean Code Best Practices
*   Use `const` by default.
*   Descriptive variable names (`userList` vs `ul`).
*   Small, pure functions.

## 2. Error Handling
`try { ... } catch (err) { ... }`.
Always handle promise rejections to avoid "Unhandled Promise Rejection" crashes.

## 3. Debugging
*   `console.log()`: The classic.
*   `debugger`: Keyword that pauses execution in Chrome DevTools.
*   DevTools source tab: Step through code line by line.
"""
}

# 4. REACT
react_theory = {
    1: """# Module 1: React Basics & Philosophy
## 1. Component-Based Architecture
React divides UI into independent, reusable pieces called Components.
Instead of one massive HTML file, you build `Button`, `Header`, `Footer` and assemble them.
This separation of concern makes code maintainable and testable.

## 2. JSX (JavaScript XML)
JSX allows writing HTML-like syntax inside JavaScript.
`const el = <h1>Hello</h1>;`
It is syntactic sugar for `React.createElement()`.
*   Rules: Must close all tags, use `className` instead of `class`, and wrap adjacent elements in a fragment `<>...</>`.

## 3. Virtual DOM
React keeps a lightweight copy of the DOM in memory.
When state changes, React updates the Virtual DOM, diffs it with the real DOM, and only updates the specific nodes that changed.
This minimizes costly browser repaints.
""",
    2: """# Module 2: Props & Data Flow
## 1. Unidirectional Data Flow
In React, data flows strictly **downwards** from parent to child via Props.
Parents pass data; children receive it. Children cannot modify props directly (they are read-only).
To communicate up, children call callback functions passed down by parents.

## 2. Understanding Props
Props are like Function Arguments for your components.
`function Welcome(props) { return <h1>Hi, {props.name}</h1>; }`
They promote reusability. The same `Button` component can be green or red based on props.

## 3. Prop Destructuring
Modern React favors destructuring for cleaner code:
`function Card({ title, content }) { ... }`
Using `defaultProps` or default parameters handle missing values gracefully.
""",
    3: """# Module 3: State Management (useState)
## 1. Local State
State is the "memory" of a component. Unlike props (external), state is internal and controlled by the component.
When state changes, React re-renders the component to reflect the new UI.

## 2. The `useState` Hook
`const [count, setCount] = useState(0);`
*   `count`: The current value.
*   `setCount`: The function to update it.
*   `0`: The initial value.
**Never** modify state directly (`count = 5`). Always use the setter.

## 3. State Updates are Asynchronous
React batches updates for performance.
If updating based on previous state, use the functional form:
`setCount(prev => prev + 1)`
This ensures you work with the latest value during rapid updates.
""",
    4: """# Module 4: Effects & Lifecycle (useEffect)
## 1. Side Effects
A side effect is anything affecting the world outside the function scope: fetching data, changing document title, subscriptions.
Components should be pure functions; effects handle the "impure" parts.

## 2. The `useEffect` Hook
`useEffect(() => { ... }, [dependencies]);`
*   No deps array: Runs on *every* render.
*   Empty array `[]`: Runs *only on mount* (like componentDidMount).
*   `[prop]`: Runs when `prop` changes.

## 3. Cleanup Function
If an effect subscribes to something (like a WebSocket or Timer), it must return a cleanup function.
`return () => clearInterval(id);`
React runs this before the component unmounts or before re-running the effect.
""",
    5: """# Module 5: Conditional Rendering
## 1. The Ternary Operator
Inline condition checking inside JSX:
`{isLoggedIn ? <UserDashboard /> : <LoginBtn />}`
Concise and readable for binary states.

## 2. The Logical AND (&&)
Useful when you want to render something *only if* true, otherwise nothing.
`{hasError && <ErrorMessage />}`
*   **Warning**: If the condition is `0`, React might render the number "0" instead of nothing. Boolean cast `!!count` is safer.

## 3. Early Returns
If data is loading, return early to prevent the rest of the component from running with null data.
`if (loading) return <Spinner />;`
""",
    6: """# Module 6: Forms & Events
## 1. Controlled Components
In HTML, inputs have their own state. In React, we override this.
We set `value={state}` and update state on `onChange`.
This makes the React State the "Single Source of Truth".

## 2. Handling Events
Events in React are Synthetic Events (wrappers around browser native events).
`onSubmit={(e) => { e.preventDefault(); ... }}`
Prevents the browser from reloading the page, behaving like a Single Page App (SPA).

## 3. Complex Forms
For large forms, managing individual state variables is tedious.
Libraries like `React Hook Form` or `Formik` manage validation and state efficiently.
""",
    7: """# Module 7: React Router (Client-Side Routing)
## 1. SPA Navigation
Traditional web apps reload the page on link click.
React Router intercepts the URL change and renders a different Component *without* reloading.
Faster transitions and preserved state.

## 2. Key Components
*   `<BrowserRouter>`: Wraps the app.
*   `<Routes>` / `<Route>`: Maps paths to components.
*   `<Link>`: Replaces `<a>`. Updates history api instead of requesting a new document.

## 3. Dynamic Routes
`/users/:id`.
Use `useParams()` hook to extract parameters (e.g., getting user ID 5 from URL to fetch profile).
""",
    8: """# Module 8: Context API (Global State)
## 1. The Prop Drilling Problem
Passing data through 5 layers of components just to reach a button is messy.
Context provides a way to share values (Theme, User Auth) like a broadcast system.

## 2. Provider & Consumer
1.  **Create**: `const UserCtx = createContext()`.
2.  **Provide**: Wrap tree in `<UserCtx.Provider value={user}>`.
3.  **Consume**: Use `useContext(UserCtx)` in any child to access data directly.

## 3. When to Use
Use sparingly. It makes components harder to reuse (coupled to context).
For complex global state, consider Redux or Zustand.
""",
    9: """# Module 9: Custom Hooks & Performance
## 1. Custom Hooks
Extract logic into functions starting with `use...`.
Example: `useFetch(url)` handles loading, error, and data state internally.
Allows sharing *logic* between components, not just UI.

## 2. Memoization (`useMemo`, `useCallback`)
*   `useMemo`: Caches a stored value. Used for expensive calculations.
*   `useCallback`: Caches a function definition. Used to prevent child re-renders when passing functions as props.

## 3. `React.memo`
Wraps a component to prevent re-render if its props haven't changed.
Optimization technique for list items or static UI parts.
""",
    10: """# Module 10: Optimizations & Ecosystem
## 1. Code Splitting (Lazy Loading)
`React.lazy` and `Suspense`.
Don't load the Administration Dashboard code for a regular user. Load it only when they visit the route.
Reduces initial bundle size.

## 2. Next.js (The Framework)
React is a library (UI). Next.js is a framework (Routing, SSR, API).
Concepts like Server-Side Rendering (SSR) and Static Site Generation (SSG) improve SEO and Performance.

## 3. Virtualization
Rendering 10,000 list rows freezes the browser.
Virtualization (React Window) renders only the 10 rows visible on screen + buffers.
Essential for Big Data apps.
"""
}

# 5. C++
cpp_theory = {
    1: """# Module 1: C++ Foundations & Compilation
## 1. System-Level Power
C++ gives you direct control over hardware. It is a superset of C with OOP features.
It is compiled, statically typed, and supports both low-level memory manipulation and high-level abstractions.

## 2. The Compilation Pipeline
1.  **Preprocessor**: Handles directives (`#include`, `#define`). Replaces text.
2.  **Compiler**: Translates C++ to Assembly.
3.  **Assembler**: Translates Assembly to Machine Code (Object files `.o`).
4.  **Linker**: Combines object files and libraries into the final executable.

## 3. Basic I/O
`iostream` provides streams: `cin` (input) and `cout` (output).
Namespaces (`using namespace std;`) manage identifier conflicts.
Best practice: Avoid `using namespace std` in headers to prevent pollution.
""",
    2: """# Module 2: Types & Memory Models
## 1. Fundamental Types
*   Integral: `int`, `long`, `short`, `char`, `bool`.
*   Floating: `float`, `double`.
*   Sizes are platform-dependent (int is usually 4 bytes, but not guaranteed). use `sizeof`.

## 2. The Stack vs The Heap
*   **Stack**: Fast, automatic storage. Local variables live here. They die when scope ends.
*   **Heap**: Large, manual storage. You request memory, you generally must free it (until Modern C++).

## 3. RAII (Resource Acquisition Is Initialization)
The Golden Rule of C++.
Bind resource life (memory, file handles) to object life.
When an object goes out of scope (stack unwinding), its Destructor releases the resource.
This eliminates most memory leaks without a Garbage Collector.
""",
    3: """# Module 3: Control Flow
## 1. Branching
`if`, `switch`.
C++ allows variable declaration inside if-conditions (C++17):
`if (int x = getValue(); x > 0) { ... }` reduces scope pollution.

## 2. Loops
`for`, `while`, `do-while`.
Range-based for loop (C++11):
`for (const auto& item : items)` iterates collections efficiently logic.

## 3. Jump Statements
*   `break`: Exit loop/switch.
*   `continue`: Skip iteration.
*   `goto`: Exists but considered harmful (spaghetti code).
""",
    4: """# Module 4: Functions & References
## 1. Function Prototypes
Separate declaration (header) from implementation (cpp file).
The Linker connects them.

## 2. Arguments: Value vs Reference
*   **By Value** (`int x`): Copies data. Safe but slow for big objects.
*   **By Reference** (`int &x`): Passes alias. Fast. Allows modification.
*   **Const Reference** (`const int &x`): Fast (no copy) + Safe (read-only). Default for objects.

## 3. Function Overloading
Same name, different parameters.
Compiler mangles names to distinguish them.
""",
    5: """# Module 5: Pointers & Arrays
## 1. Pointers
Variables that store memory addresses.
`int* p = &x;`
*   `&` (Address-of): Get the address.
*   `*` (Dereference): Access value at address.
Crucial for dynamic memory and arrays.

## 2. Pointer Arithmetic
`p + 1` moves the pointer by `sizeof(type)` bytes.
Arrays decay to pointers when passed to functions.
Buffer overflows happen here (accessing index out of bounds).

## 3. C-Style Arrays vs std::array
*   `int arr[5]` is raw memory. No size safety.
*   `std::array<int, 5>` (C++11) wraps it with size info and safety. Use this.
""",
    6: """# Module 6: Classes & Objects
## 1. Encapsulation
Bundling data and methods.
*   `public`: Interface.
*   `private`: Implementation details (Data).
*   `class` defaults to private; `struct` defaults to public.

## 2. Constructors & Destructors
*   **Ctor**: Initializes object.
*   **Dtor (`~Class`)**: Cleans up. crucial for RAII.
*   Initializer lists `: x(val)` are more efficient than assignment inside body.

## 3. Const Methods
`void print() const;`
Promises not to modify the object state.
Compiler enforces this. Essential for correctness.
""",
    7: """# Module 7: Dynamic Memory
## 1. New and Delete
`int* p = new int;` allocates on Heap.
`delete p;` frees it.
Forgot `delete`? Memory Leak.
Double `delete`? Undefined Behavior (Crash).

## 2. Dynamic Arrays
`int* arr = new int[10];` -> `delete[] arr;`
Mismatched new/delete causes issues.

## 3. Modern Approach (Avoid new!)
Use Smart Pointers or `std::vector`.
Raw `new`/`delete` is considered legacy/library-impl code in modern C++.
""",
    8: """# Module 8: Inheritance & Polymorphism
## 1. Inheritance
`class Dog : public Animal`.
"Is-a" relationship.
Method overriding allows specialized behavior.

## 2. Virtual Functions
To enable polymorphism (calling child method via parent pointer), the base method must be `virtual`.
`virtual void speak();`
This creates a V-Table (lookup table) pointer in the object.

## 3. Abstract Classes
Classes with at least one Pure Virtual Function (`= 0`).
`virtual void shape() = 0;`
Enforces interface compliance.
""",
    9: """# Module 9: The STL (Standard Template Library)
## 1. Containers
*   `std::vector`: Dynamic array. Use 90% of the time.
*   `std::map`: Balanced Tree (Key-Value). Ordered.
*   `std::unordered_map`: Hash Table. Fast.

## 2. Iterators
Pointers-on-steroids for traversing containers.
`vector<int>::iterator it = v.begin();`
Decouples algorithms from container logic.

## 3. Algorithms
`<algorithm>` header.
`std::sort`, `std::find`, `std::transform`.
Highly optimized generic code. Don't write your own bubble sort.
""",
    10: """# Module 10: Modern C++ (11/14/17/20)
## 1. Smart Pointers
*   `unique_ptr`: Sole ownership. Deletes when out of scope. No copy, only move.
*   `shared_ptr`: Reference counted. Deletes when last owner is gone.

## 2. Lambdas
Anonymous functions.
`auto func = [](int x) { return x * 2; };`
Great for passing custom logic to STL algorithms.

## 3. Move Semantics (&&)
Optimizing copying.
Instead of deep copying a temporary object, we "steal" its internal pointers.
Drastically improves performance for return-by-value.
"""
}

# 6. HTML
html_theory = {
    1: """# Module 1: Semantic HTML & Structure
## 1. The Document Object Model (DOM)
HTML is not just text; it's a tree structure.
`<!DOCTYPE html>` triggers standards mode.
The `<html>` root contains `<head>` (metadata) and `<body>` (content).

## 2. Semantic Elements
Don't use `<div>` for everything.
*   `<header>`, `<nav>`, `<main>`, `<article>`, `<footer>`.
*   Semantics give meaning to content, helping Search Engines (SEO) and Screen Readers (Accessibility).
*   Example: A screen reader can jump straight to `<main>`.

## 3. Content Categorization
*   **Block-level**: Starts on new line, takes full width (`div`, `p`, `h1`).
*   **Inline**: Takes necessary width, flows with text (`span`, `a`, `img`).
""",
    2: """# Module 2: Forms & Interactive Inputs
## 1. The `<form>` Element
The container for user input.
*   `action`: URL to send data to.
*   `method`: HTTP method (GET/POST).
*   **Best Practice**: Always perform Backend validation. HTML validation is just UI sugar.

## 2. Input Prototypes
HTML5 introduced powerful types:
*   `<input type="email">`: Mobile keyboards show '@'.
*   `<input type="date">`: Native date pickers.
*   `<input type="number">`: Numeric keypads.

## 3. Accessibility (Labels)
Every input MUST have a label.
*   Explicit: `<label for="id">Name</label><input id="id">`.
*   Implicit: `<label>Name <input></label>`.
Using `placeholder` is NOT a replacement for a label (it disappears when typing).
""",
    3: """# Module 3: Accessibility (a11y)
## 1. Why it Matters
Web is for everyone, including those with visual, motor, or cognitive impairments.
Legal requirements (ADA/WCAG) enforce this for many sites.

## 2. ARIA (Accessible Rich Internet Applications)
Attributes like `aria-label`, `aria-hidden`, `role="alert"`.
**Rule of thumb**: No ARIA is better than Bad ARIA. Use native HTML semantics first.
Only use ARIA when creating custom widgets (like a divine toggle switch).

## 3. Images & Alt Text
`<img src="..." alt="Description">`.
*   Decorative images: `alt=""` (Screen reader ignores).
*   Informative images: Describe the *meaning*, not just the visual ("Chart showing sales up 5%" vs "Blue bars").
""",
    4: """# Module 4: Media & Graphics
## 1. Audio & Video
Native tags `<audio>` and `<video>` removed reliance on Flash.
*   Attributes: `controls`, `autoplay`, `loop`, `muted`.
*   Multiple sources `<source>` for format compatibility (MP4 vs WebM).

## 2. The Canvas API
`<canvas>`: A bitmap drawing surface.
Used for games, visualizations, and photo editing.
Driven completely by JavaScript (`ctx.fillRect(...)`).

## 3. SVG (Scalable Vector Graphics)
XML-based vector images.
*   Resolution independent (sharp on Retina).
*   Stylable via CSS (`fill: red`).
*   Animatable.
""",
    5: """# Module 5: Tables & Data
## 1. Table Structure
Tables are for **tabular data**, NOT layout (don't live in 1999).
*   `<thead>`: Header rows (`<th>`).
*   `<tbody>`: Body rows (`<tr>`, `<td>`).
*   `<tfoot>`: Summary rows.

## 2. Spanning
*   `rowspan="2"`: Merge vertical cells.
*   `colspan="2"`: Merge horizontal cells.
*   Complex tables can be confusing for screen readers; use `scope="col"` or `headers` attributes.

## 3. Styling Hooks
`<caption>` provides a title for the table.
`<colgroup>` allows styling entire columns without adding classes to every cell.
""",
    6: """# Module 6: Meta Tags & SEO
## 1. Search Engine Optimization
SEO starts with code.
*   `<title>`: The most important tag. Appears in search results.
*   `<meta name="description">`: The snippet below the link.

## 2. Social Media Cards (Open Graph)
Control how your link looks on Twitter/Facebook.
*   `og:title`, `og:image`, `og:description`.
*   Essential for click-through rates.

## 3. Viewport Meta Tag
`<meta name="viewport" content="width=device-width, initial-scale=1">`.
Checking "Mobile Friendly". Without this, mobile browsers zoom out to show a desktop site (unreadable).
""",
    7: """# Module 7: Hyperlinks & Navigation
## 1. The A Tag
Hyperlink is the H in HTML.
*   `href`: The destination.
*   `target="_blank"`: Opens in new tab (Security risk! Always add `rel="noopener noreferrer"`).

## 2. Relative vs Absolute
*   Absolute: `https://google.com` (Different domain).
*   Relative: `/about` (Same domain) or `../images` (File system navigation).

## 3. Fragment Identifiers
`href="#section1"`. Jumps to the element with `id="section1"` on the same page.
Used for Table of Contents or "Skip to Content" links.
""",
    8: """# Module 8: Storage & APIs
## 1. LocalStorage vs SessionStorage
*   **LocalStorage**: Persists forever (until cleared). 5-10MB limit. Good for theme preference.
*   **SessionStorage**: Persists only for the tab session. Good for form drafts.
*   **Cookies**: Sent with every HTTP request. Used for Auth tokens.

## 2. Geolocation API
`navigator.geolocation.getCurrentPosition()`.
Requires user permission (Browser prompt).
HTTPS only.

## 3. Drag and Drop API
Native support for dragging elements.
Events: `ondragstart`, `ondragover` (must preventDefault), `ondrop`.
Often complex; libraries like specific DnD are popular wrappers.
""",
    9: """# Module 9: Responsive Images
## 1. The Problem
Desktops need 4K images; Mobiles need tiny JPEGs to save data.
Sending 4K headers to a phone is bad performance.

## 2. `srcset` Attribute
`<img src="small.jpg" srcset="large.jpg 1024w, medium.jpg 640w">`.
Tells the browser: "Here are the files and their widths, you choose the best one."

## 3. The `<picture>` Element
For "Art Direction" (Showing a wide shot on desktop but a cropped regular portrait on mobile).
Allows different file formats too (`type="image/webp"`).
""",
    10: """# Module 10: Validation & Best Practices
## 1. W3C Validation
HTML is forgiving. It tries to render broken code.
This is bad for consistency. Use the W3C Validator to catch unclosed tags or invalid nesting.

## 2. Maintainability
*   Consistent indentation (2 or 4 spaces).
*   Lowercase tags and attributes.
*   Quote all attribute values.

## 3. Progressive Enhancement
Build the core content first (plain HTML).
Then add CSS for layout.
Then add JS for interactivity.
If JS fails, the site should still be readable.
"""
}

# 7. CSS
css_theory = {
    1: """# Module 1: Selectors & The Cascade
## 1. Types of Selectors
*   **Element**: `p {}` (Low specificty, 0-0-1).
*   **Class**: `.card {}` (Medium, 0-1-0). Reusable.
*   **ID**: `#nav {}` (High, 1-0-0). Unique.
*   **Universal**: `* {}`. Resets.

## 2. The Cascade
CSS = Cascading Style Sheets.
When rules conflict (e.g., both `.blue` and `.red` set color), the winner is decided by:
1.  **Importance**: `!important`.
2.  **Specificity**: ID > Class > Tag.
3.  **Source Order**: Last defined wins.

## 3. Inheritance
Some properties (color, font-family) trigger down to children.
Some (border, padding) do not.
Use `inherit` to force inheritance.
""",
    2: """# Module 2: The Box Model
## 1. Everything is a Box
Every HTML element is a rectangular box composed of 4 layers:
1.  **Content**: The text/image.
2.  **Padding**: Space *inside* the border.
3.  **Border**: The line around the padding.
4.  **Margin**: Space *outside* the border (pushes neighbors away).

## 2. Box-Sizing
Standard behavior (`content-box`) adds padding/border to width, breaking layouts.
`box-sizing: border-box` includes padding/border IN the width.
**Best Practice**: Apply this globally `* { box-sizing: border-box; }`.

## 3. Margins
*   **Collapsing**: Vertical margins of adjacent elements merge (largest wins).
*   **Auto**: `margin: 0 auto` centers a block element horizontally.
""",
    3: """# Module 3: Typography & Fonts
## 1. Font Families
*   **Serif**: Times New Roman (Formal).
*   **Sans-Serif**: Arial, Helvetica (Clean, Screen-friendly).
*   **Monospace**: Code.
Always provide a fallback stack: `font-family: "Open Sans", Helvetica, sans-serif;`.

## 2. Units
*   `px`: Absolute. Good for borders.
*   `em`: Relative to parent font-size.
*   `rem`: Relative to Root (html) font-size. **Preferred** for accessibility (respects user browser settings).

## 3. Text Properties
*   `line-height`: Vertical spacing (readability). 1.5 is standard.
*   `letter-spacing`: Tracking.
*   `text-align`: Left, center, right, justify.
""",
    4: """# Module 4: Flexbox (1D Layout)
## 1. The Flex Container
`display: flex;`.
Turns direct children into flex items.
Default: Lay out in a row, shrinking to fit.

## 2. Axes
*   **Main Axis**: Defined by `flex-direction` (row or column).
*   **Cross Axis**: The perpendicular one.
*   `justify-content`: Aligns along Main Axis.
*   `align-items`: Aligns along Cross Axis.

## 3. Flexibility
`flex: 1;`.
Shorthand for `flex-grow`, `flex-shrink`, `flex-basis`.
Makes the item fill available space.
""",
    5: """# Module 5: CSS Grid (2D Layout)
## 1. Grid vs Flexbox
Flexbox is for lines (menus, stacks). Grid is for pages (sidebar + main content + footer).
Grid handles rows and columns simultaneously. `display: grid;`.

## 2. Defining Tracks
`grid-template-columns: 200px 1fr;`.
*   `fr`: Fraction unit. Takes up remaining space.
*   `repeat(3, 1fr)`: Three equal columns.

## 3. Grid Areas
Name your cells:
`grid-template-areas: "header header" "sidebar main";`
Then assign children: `.head { grid-area: header; }`.
Visual layout in code!
""",
    6: """# Module 6: Responsive Design
## 1. The Viewport
The infinite canvas. We view it through a "viewport" (screen).
Responsive design means adapting to viewport width.

## 2. Media Queries
Conditional CSS.
`@media (max-width: 768px) { .sidebar { display: none; } }`.
Breakpoints: Mobile (<600), Tablet (<900), Desktop (>900).

## 3. Mobile-First
Write CSS for mobile *first* (simpler, 1 column).
Then use `min-width` media queries to add complexity for larger screens.
This is more performant (mobiles don't parse desktop overrides).
""",
    7: """# Module 7: Transitions & Animations
## 1. Transitions
Smoothly changing a property from State A to State B.
`transition: background 0.3s ease;`.
Triggered by pseudo-classes (`:hover`) or class changes via JS.

## 2. Keyframes
Complex, multi-step animations.
`@keyframes slide { 0% { left: 0; } 100% { left: 100px; } }`.
Independent of user interaction (can loop infinite).

## 3. Performance
Animate `transform` (move/scale) and `opacity`.
Avoid animating `width`/`height`/`top`/`left` as they trigger layout recalculations (slow).
""",
    8: """# Module 8: Custom Properties (Variables)
## 1. Syntax
`--primary-color: #3498db;`.
access with `var(--primary-color)`.
Standard CSS, no preprocessor needed.

## 2. Scoping
Variables follow the cascade.
*   Define in `:root` for global scope.
*   Redefine in a specific class `.dark-mode` to override down the tree.

## 3. Theming / Dark Mode
The power of variables.
Switching a class on `<body>` updates all colors instantly without writing new CSS rules for every component.
""",
    9: """# Module 9: Pseudo-Elements & Classes
## 1. Pseudo-Classes (State)
Target elements based on state.
*   `:hover`, `:focus` (Accessiblity vital!).
*   `:nth-child(even)`: Striped tables.
*   `:not(.active)`: Exclusion.

## 2. Pseudo-Elements (Virtual)
Create elements via CSS without polluting HTML.
*   `::before`, `::after`.
*   Must set `content: ""`.
*   Used for icons, tooltips, decorative shapes.

## 3. Stacking Context (z-index)
`z-index` controls depth.
Only works on positioned elements (`relative`, `absolute`, `fixed`).
It creates a stacking context; a child with z=999 cannot escape a parent with z=1.
""",
    10: """# Module 10: CSS Architecture
## 1. The Maintenance Problem
CSS is global. Name collisions are inevitable in big projects (`.card` matches everything).
Specificity wars lead to `!important` hell.

## 2. BEM (Block Element Modifier)
Naming convention: `.block__element--modifier`.
*   `.btn`: Block.
*   `.btn__icon`: Element inside.
*   `.btn--large`: Variant.
Keeps specificity low (flat) and explicit.

## 3. CSS Modules / CSS-in-JS
Modern tools scale CSS.
*   CSS Modules: Auto-generates unique class names (`btn_x8f2`).
*   Styled Components: Writes CSS in JS files constrained to components.
"""
}

# 8. C
c_theory = {
    1: """# Module 1: C Fundamentals
## 1. The Mother of Languages
C is the foundation of modern computing (Linux, Windows, Python's core).
It is small, fast, and dangerous. It provides zero abstractions over the hardware.
"C assumes you know what you are doing."

## 2. Structure of a C Program
*   `#include <stdio.h>`: Preprocessor imports.
*   `int main()`: Entry point.
*   `return 0`: Exit code (0 = success).
*   Semicolons `;` are mandatory.

## 3. Compilation Process
Source (`.c`) -> Preprocessor -> Compiler -> Linker -> Executable.
`gcc main.c -o app`
Unlike Python, you manage the build process.
""",
    2: """# Module 2: Scalar Types & Variables
## 1. Data Types
*   `int`: Integer (usually 4 bytes).
*   `char`: Single character / byte (1 byte). ASCII.
*   `float`, `double`: Decimals.
*   Size varies by CPU architecture. Use `sizeof()` to be sure.

## 2. Variables
Declaration: `int x;`. Memory contains garbage until initialized.
Initialization: `int x = 5;`.
Constants: `const int MAX = 100;`.

## 3. Format Specifiers
`printf` needs to know types to format output.
*   `%d`: Integer.
*   `%f`: Float.
*   `%c`: Char.
*   `%s`: String (char array).
Mismatches cause garbage output.
""",
    3: """# Module 3: Control Flow
## 1. Logic
`if (x > 5) { ... } else { ... }`.
C uses integer logic for Booleans (pre-C99).
0 is False. Non-zero is True.
`<stdbool.h>` adds `bool`, `true`, `false`.

## 2. Loops
*   `while`: Standard.
*   `do-while`: Run at least once.
*   `for (init; cond; inc)`: The classic C loop.
Note: In old C (C89), you must declare variables at the top of the block, not inside the `for` loop.

## 3. Switch
Efficient dispatch.
Supports only integers/chars (no strings).
Fall-through is default (feature/bug).
""",
    4: """# Module 4: Functions
## 1. Decomposition
Breaking logic into small, reusable blocks.
`int add(int a, int b) { return a+b; }`
Must allow specific types. No polymorphism.

## 2. Prototypes
C passes top-down. If you call `func()` before defining it, compiler panics.
Solution: Declare prototype `int func();` at top, define at bottom.

## 3. Call Stack
Variables are local to the function (Stack frame).
When function returns, variables are popped and lost.
Passed arguments are copies (Pass by Value).
""",
    5: """# Module 5: Pointers & Memory Address
## 1. What is a Pointer?
A variable holding a memory address.
`int *p;` -> I hold the address of an int.
`&x` -> Address of x.
`*p` -> Value at that address.

## 2. Why Pointers?
*   Passing large data without copying (pass by reference).
*   Dynamic memory (Heap).
*   Arrays and Strings (which are just internal pointers).

## 3. Danger Zone
*   Segfault: Accessing memory you don't own.
*   Null Pointer: `p = NULL`. Dereferencing crashes program.
""",
    6: """# Module 6: Arrays & Strings
## 1. Arrays
Contiguous memory block. `int arr[5];`.
Access: `arr[0]`.
Internally, `arr` is just a pointer to the first element.
`arr[i]` is sugar for `*(arr + i)`.

## 2. No Bounds Checking
C will happily let you access `arr[100]` of a size 5 array.
This reads random memory or crashes. Major security vulnerability (Buffer Overflow).

## 3. Strings are Arrays
C has no String type. It has arrays of chars ending in a Null Terminator `\0`.
`char s[] = "Hi";` is `['H', 'i', '\0']`.
Functions `strcpy`, `strlen` rely on finding that `\0`.
""",
    7: """# Module 7: Structs & Unions
## 1. User-Defined Types
`struct Point { int x; int y; };`.
Grouping related data.
Access: `p.x` (Direct) or `ptr->x` (via Pointer).

## 2. Typedef
`typedef struct Point Point;`.
Removes the need to write `struct` everywhere.
`Point p1;`.

## 3. Unions
Memory efficient: Multiple members share the *same* memory space.
Only one active at a time.
Used in low-level driver code or variant types.
""",
    8: """# Module 8: Dynamic Memory (Manual)
## 1. The Heap
Stack is small. Heap is huge.
`<stdlib.h>`
`malloc(size)`: Allocate bytes. Returns `void*`.
`free(ptr)`: Release bytes.

## 2. Lifecycle
`int *arr = malloc(10 * sizeof(int));`
... use it ...
`free(arr);`
If you forget `free`: **Memory Leak**.
If you `free` twice: **Double Free Corruption**.

## 3. Valgrind
A tool to detect leaks. Essential for C development.
""",
    9: """# Module 9: File I/O
## 1. FILE Pointers
`FILE *fp = fopen("data.txt", "r");`
Modes: "r" (read), "w" (write), "a" (append), "rb" (binary).

## 2. Operations
*   `fprintf`: Write formatted text.
*   `fscanf`: Read formatted text.
*   `fgets`: Read line (safer than gets).

## 3. Buffering
I/O is expensive. C buffers specific data.
`fflush(fp)` forces write to disk.
Always `fclose(fp)` to flush and release lock.
""",
    10: """# Module 10: Advanced C & Build Systems
## 1. Preprocessor Macros
`#define MAX(a,b) ((a)>(b)?(a):(b))`
Text substitution. Powerful but dangerous (side effects in arguments).
Use `const` and `inline` functions where possible.

## 2. Modular Programming
Splitting code into `.c` (Implem) and `.h` (Header) files.
Include Guards: `#ifndef HEADER_H ...` prevents double inclusion.

## 3. Makefiles
Automating the build.
Definitions of targets and dependencies.
`make` determines what needs recompiling based on file timestamps.
"""
}

# 9. GO (GOLANG)
go_theory = {
    1: """# Module 1: The Go Philosophy
## 1. Simplicity by Design
Go (Golang) was created at Google to solve problems of scale.
It rejects complex features like inheritance, method overloading, and pointer arithmetic.
"Clear is better than clever."

## 2. Workspace & Tools
*   `go run main.go`: Compile and run in memory.
*   `go build`: Create binary.
*   `go fmt`: Standardized formatting (no arguments about whitespace!).
*   `go mod`: Dependency management.

## 3. The `main` Package
Every executable Go program starts in `package main`.
The entry point is `func main()`.
Exits when main returns (other Goroutines are killed immediately).
""",
    2: """# Module 2: Variables & Types
## 1. Static but Concise
Go is statically typed, but type inference saves typing.
*   `var x int = 10` (Verbose).
*   `x := 10` (Short declaration). Only works inside functions.

## 2. Zero Values
Go never leaves variables uninitialized (no garbage memory).
*   `int` -> 0
*   `string` -> ""
*   `bool` -> false
*   `pointer` -> nil

## 3. Basic Types
`bool`, `string`, `int`, `uint`, `byte` (alias for uint8), `rune` (alias for int32/Unicode char), `float64`.
""",
    3: """# Module 3: Control Flow
## 1. The Only Loop
Go has only one loop keyword: `for`.
*   `for i := 0; i < 10; i++` (Standard).
*   `for x < 10` (Like While).
*   `for` (Infinite).

## 2. If / Switch
*   `if`: No parentheses needed. `if x > 5 { }`.
*   `switch`: No `break` needed (automatic break). Use `fallthrough` explicitly if needed.

## 3. Defer
`defer cleanup()` schedules a function call to run immediately before the surrounding function returns.
Used for file closing, mutex unlocking.
Stack execution (Last-In, First-Out).
""",
    4: """# Module 4: Functions
## 1. Signatures
`func add(a int, b int) int { return a + b }`.
Parameters are typed. Return types come after the parenthesis.

## 2. Multiple Return Values
Go functions can return multiple values.
`func swap(a, b int) (int, int) { return b, a }`.
This avoids "out parameters" or wrapping results in objects.

## 3. Named Return Values
`func split(sum int) (x, y int)`.
You can assign to `x` and `y` inside the function and use a "naked" `return`.
Use sparingly (can reduce readability in long functions).
""",
    5: """# Module 5: Arrays & Slices
## 1. Arrays (Fixed)
`var a [5]int`. Length is part of the type.
`[5]int` is different from `[4]int`.
Passed by value (copies the whole array!).

## 2. Slices (Dynamic)
The viewport into an underlying array.
`var s []int = a[1:4]`.
Has a Length and Capacity.
Passed by reference (cheap).

## 3. Appending
`s = append(s, 10)`.
If capacity is exceeded, Go allocates a new bigger array, copies data, and points the slice to it.
""",
    6: """# Module 6: Maps & Structs
## 1. Maps
Hash tables. `m := make(map[string]int)`.
*   `delete(m, "key")`.
*   `val, ok := m["key"]`. The `ok` boolean checks existence.

## 2. Structs
Typed collections of fields.
`type Vertex struct { X int; Y int }`.
No classes in Go. Structs are the data containers.

## 3. Embedding (Composition)
Instead of inheritance, Go uses embedding.
`type Admin struct { User; Level int }`.
Admin gets access to User fields naturally.
""",
    7: """# Module 7: Methods & Interfaces
## 1. Methods
Functions attached to a type.
`func (v Vertex) Abs() float64`.
`(v Vertex)` is the Receiver.

## 2. Pointer Receivers
`func (v *Vertex) Scale(f float64)`.
Allows the method to modify the struct.
More efficient (avoids copying).

## 3. Interfaces (Implicit)
`type Abser interface { Abs() float64 }`.
A generic type.
If a struct has an `Abs()` method, it **is** an Abser.
No `implements` keyword. "Duck typing checked at compile time."
""",
    8: """# Module 8: Goroutines (Concurrency)
## 1. Lightweight Threads
`go myFunction()`.
Spawns a new thread of execution managed by the Go Runtime (not OS threads).
2KB stack size vs 1MB for OS threads. You can run thousands.

## 2. The Scheduler
Go's "M:N scheduler" multiplexes M goroutines onto N OS threads.
Automatic context switching.

## 3. Sync Package
`sync.Mutex` for locking shared data.
`sync.WaitGroup` for waiting for a group of goroutines to finish.
""",
    9: """# Module 9: Channels
## 1. CSP (Communicating Sequential Processes)
"Do not communicate by sharing memory; share memory by communicating."
Channels are pipes for passing specific data between goroutines.

## 2. Operations
`ch := make(chan int)`.
`ch <- v` (Send).
`v := <-ch` (Receive).
Refusal to send/receive blocks the goroutine until the other side is ready. Synchronization without locks.

## 3. Buffered Channels
`make(chan int, 100)`.
Sends only block when buffer is full.
""",
    10: """# Module 10: Error Handling
## 1. Errors are Values
Go has no Exceptions. It returns errors as the last return value.
`f, err := os.Open("file.txt")`.

## 2. The Check
`if err != nil { return err }`.
Forces you to handle failure cases explicitly right where they happen.

## 3. Custom Errors
Implementing the `error` interface.
`type MyError struct { Msg string }`.
`func (e *MyError) Error() string { return e.Msg }`.
"""
}

# 10. TYPESCRIPT
ts_theory = {
    1: """# Module 1: TypeScript Basics
## 1. Superset of JavaScript
TS adds static typing to JS.
It compiles (transpiles) down to plain JS.
Every valid JS program is a valid TS program (mostly).

## 2. Types
`const name: string = "Alice";`.
`const age: number = 30;`.
Compiler catches logic errors (`"5" * 5`) before you run the code.

## 3. Configuration
`tsconfig.json`.
Controls strictness (`noImplicitAny`), target version (ES5, ES6), and module system.
""",
    2: """# Module 2: Advanced Types
## 1. The `any` Type
The escape hatch. `let x: any`.
Disables type checking. Avoid using it unless migrating legacy code.

## 2. Arrays & Tuples
*   `number[]` or `Array<number>`.
*   **Tuple**: `[string, number]`. Fixed length and types at specific positions.

## 3. Enums
`enum Color { Red, Green, Blue }`.
A feature added by TS (not in JS). Maps names to numbers (0, 1, 2).
""",
    3: """# Module 3: Interfaces vs Types
## 1. Interfaces
`interface User { name: string; id: number; }`.
Extendable. Used mainly for defining object shapes and class contracts.

## 2. Type Aliases
`type ID = string | number;`.
More flexible. Can define Unions, Primitives, and Tuples.

## 3. Interface Merging
Interfaces with the same name merge automatically. Types do not.
""",
    4: """# Module 4: Functions & Classes
## 1. Function Typing
`function add(x: number, y: number): number`.
Optional parameters: `y?: number`.
Default parameters: `y: number = 10`.

## 2. Classes
Standard ES6 classes but with access modifiers.
`public` (default), `private`, `protected`.
`readonly` properties.

## 3. Abstract Classes
Classes that cannot be instantiated.
Used as base classes requiring implementation.
""",
    5: """# Module 5: Generics
## 1. Reusable Code
Writing function that work with any type but keep type safety.
`function identity<T>(arg: T): T { return arg; }`.

## 2. Constraints
`function logLength<T extends { length: number }>(arg: T)`.
Ensures the passed type T has a `.length` property.

## 3. Generic Classes
`class Box<T> { content: T; }`.
`new Box<string>()`.
""",
    6: """# Module 6: Unions & Intersections
## 1. Union Types
`let id: string | number`.
Variable can be one or the other.
Ts enforces checking type (Narrowing) before using specific methods.

## 2. Intersection Types
`type DraggableImage = Image & Draggable`.
Combines properties of both types.

## 3. Literal Types
`let direction: "left" | "right"`.
The variable can only be strictly one of those strings.
""",
    7: """# Module 7: Utility Types
## 1. Partial & Required
*   `Partial<User>`: All fields become optional.
*   `Required<User>`: All fields become required.

## 2. Pick & Omit
*   `Pick<User, "name">`: Subtype with only name.
*   `Omit<User, "id">`: Subtype without id.

## 3. Readonly
`Readonly<T>`: Makes all properties immutable.
""",
    8: """# Module 8: Decorators
## 1. Meta-programming
`@Component({...})`.
Functions that modify classes or methods at design time.
Experimental feature (needs config enabled).

## 2. Class Decorators
Receives the constructor.
Can replace or extend the class definition.

## 3. Method Decorators
Can intercept method calls, log arguments, or modify return values.
""",
    9: """# Module 9: Modules & Namespaces
## 1. ES Modules
`import { A } from "./a";`.
The standard way.

## 2. Namespaces
`namespace Validation { ... }`.
Internal TS organizational tool. Less common now that ESM is standard.

## 3. Ambient Declarations (.d.ts)
Files that describe types for JS libraries.
`declare module "lodash" { ... }`.
Allows using untyped JS libraries with type safety.
""",
    10: """# Module 10: Strict Mode
## 1. `strict: true`
Enables all strict flags. Best practice for new projects.

## 2. `strictNullChecks`
`null` and `undefined` are not in the domain of every type.
You must handle them explicitly (`string | null`).
Prevents "Cannot read property of null" runtime errors.

## 3. `noImplicitAny`
Forces you to type everything. No lazy "any" inference.
"""
}

# 11. SOLIDITY
solidity_theory = {
    1: """# Module 1: Blockchain & EVM
## 1. Ethereum Virtual Machine
The EVM is a global, decentralized state machine.
Code runs on thousands of nodes simultaneously.
"The Word Global Computer".

## 2. Smart Contracts
Immutable programs deployed to the blockchain.
Once deployed, code cannot be changed (mostly).
They hold code and state (storage).

## 3. Gas
Computational limit.
Users pay ETH (gas fees) to execute state-changing functions.
Infinite loops are impossible because gas runs out.
""",
    2: """# Module 2: Contract Structure
## 1. Pragma
`pragma solidity ^0.8.0;`.
Defines the compiler version to prevent breaking changes.

## 2. State Variables
stored on the blockchain.
`uint public count;`.
Writing to these costs significant gas (Storage).

## 3. Functions
`function inc() external { ... }`.
Logic execution.
""",
    3: """# Module 3: Data Types
## 1. Value Types
*   `uint256` (unsigned integer, standard).
*   `bool`.
*   `address` (20 byte Ethereum address). `address payable` can receive ETH.

## 2. Structs
`struct Todo { string text; bool completed; }`.
Custom complex types.

## 3. Mappings
Key-Value store. `mapping(address => uint) public balances;`.
*   Can't iterate/loop over mappings.
*   Every possible key exists (default zero value).
""",
    4: """# Module 4: Functions & Visibility
## 1. Visibility
*   `public`: Internal + External call.
*   `external`: Only from outside (Gas optimized).
*   `internal`: Inside contract + Inheritance.
*   `private`: Inside contract only.

## 2. Mutability
*   `view`: Reads state, no modification. Free (if called externally).
*   `pure`: No read, no write (math only). Free.
*   Default: Writes state. Costs Gas.

## 3. Payable
`function deposit() external payable`.
Allows the function to receive ETH along with the call.
`msg.value` holds the amount.
""",
    5: """# Module 5: Modifiers & Require
## 1. Input Validation
`require(condition, "Error Msg");`.
Reverts transaction if false, refunding remaining gas.

## 2. Modifiers
Reusable code wrappers.
`modifier onlyOwner() { require(msg.sender == owner); _; }`.
The `_;` represents the function body execution.

## 3. Custom Errors (Gas efficient)
`error InsufficientFunds();`
`revert InsufficientFunds();`.
Cheaper than storing error strings.
""",
    6: """# Module 6: Events & Logs
## 1. Logging
`event Transfer(address indexed from, address to, uint amount);`.
`emit Transfer(...)`.
Writes data to transaction logs.

## 2. Off-chain Indexing
Smart contracts cannot read events.
External apps (Frontends, subgraphs) listen to events to update UI.
Cheap alternative to storing data in Storage.

## 3. Indexed Parameters
Up to 3 parameters in an event can be `indexed`.
Allows filtering logs efficiently (e.g., "Show me all transfers FROM this address").
""",
    7: """# Module 7: Inheritance
## 1. Is-A Relationship
`contract Token is ERC20, Ownable`.
Solidity supports multiple inheritance (C3 linearization).

## 2. Virtual & Override
To modify a parent function:
Parent: `function foo() public virtual`.
Child: `function foo() public override`.

## 3. Super
`super.foo()` calls the parent implementation.
""",
    8: """# Module 8: Data Locations
## 1. Storage
Persistent. Expensive. State variables.

## 2. Memory
Temporary (function execution). Mutable. Erased after call.
Lower gas cost.
`function f(uint[] memory arr)`.

## 3. Calldata
Temporary. Read-only. External function arguments.
Cheapest location.
""",
    9: """# Module 9: Security Pitfalls
## 1. Reentrancy
Attacker contract calls back into your contract before the first call finishes.
**fix**: Checks-Effects-Interactions pattern. Update state *before* sending ETH.

## 2. Integer Overflow
Before 0.8.0, `uint8(255) + 1 == 0`.
Solidity 0.8+ has built-in safe math (reverts on overflow).

## 3. Access Control
Forgetting `onlyOwner` on critical functions like `withdraw` or `mint`.
""",
    10: """# Module 10: Tokens (ERC-20)
## 1. The Standard
Interface describing a fungible token.
`transfer`, `approve`, `transferFrom`, `balanceOf`.

## 2. Implementation
Using OpenZeppelin libraries (Audit-safe).
`import "@openzeppelin/.../ERC20.sol"`.

## 3. Mint & Burn
Creating and destroying supply.
Note: TotalSupply is just a uint variable tracking the sum.
"""
}

