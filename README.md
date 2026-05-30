# MentAI — AI-Powered Interactive Learning Buddy

MentAI is a modern, high-fidelity interactive educational platform designed to generate university-grade courses, interactive laboratories, and assessment quizzes dynamically. The platform features an ultra-minimalistic and elegant visual design system, a custom local database caching system, full Monaco Editor code compiling integrations, and comprehensive PDF report generation.

---

## 🚀 Key Features

### 1. Dynamic Course & Lesson Builder
- **AI Course Orchestration**: Dynamically generates full 10-module university-grade curricula on any search topic (from Java to MongoDB, SQL database design, or complex software architectures).
- **Intelligent Local Cache**: Utilizes a highly optimized local database caching system. Generating an existing course retrieves records instantly in `< 15ms`, protecting the platform from sequential LLM rate-limiting.

### 2. University-Grade Theory Lessons
- **Rich Content Layout**: Modules feature detailed markdown tutorials, architectural schemas, CRUD guides, and syntax walkthroughs.
- **Clean Aesthetic**: All course headers and cards are built on an elegant, minimalistic solid white surface with a signature vertical Electric Cyan (`#06B6D4`) indicator and subtle shadows.

### 3. Integrated Monaco Code Sandbox
- **Full Dev Environment**: Implements a dedicated in-browser Monaco editor code container in module labs.
- **Judge0 Compiler Execution**: Connects to the Judge0 compiler engine to run code in real-time across multiple environments, including:
  - **Python**, **Java**, **JavaScript**, **Rust**, **C++**, **SQL**, and **MongoDB**.
- **Accents**: The sandbox wrapper utilizes standard monospaced metadata and Electric Cyan action controls with the play icon removed for clean, minimalist typography.

### 4. Interactive "Fix the Syntax Bug" Loading Game
- **Topic-Aware Challenges**: Mounts a beautiful, high-contrast syntax debugging speed-run card during backend course polling.
- **Core Mechanics**: Serves language-specific debugging tasks (e.g. colons in Python, tags in React, aggregate queries in SQL) matching the user's search topic, complete with score counters, choice validations, and auto-advancing timelines.

### 5. Premium Interactive Quiz Assessment
- **satisfying Choice UI**: Choice cards feature circular letter-indicator badges (`A`, `B`, `C`, `D`) that dynamically highlight to Electric Cyan when selected.
- **Tactile Feedback**: Implements subtle scale lifts and translation animations (`x: 4`) when choice items are hovered.
- **Sticky Desktop Navigation**: The sidebar navigation container dynamically stick-scrolls alongside all 10 questions on laptops and wide desktop windows.

### 6. High-Fidelity PDF Export Engine
- **Professional Reports**: Generates premium syllabus books and quiz performance sheets.
- **Branded Design**: Includes full-width cover pages with elegant slate headers, dynamic category tags, automatic running headers and footers with page-number stamping, and page-break coordinate calculations.

---

## 🛠️ Technology Stack

### Frontend
- **Framework**: Next.js, React (TypeScript)
- **Styling**: Tailwind CSS, CSS Variables
- **Animations**: Framer Motion
- **Code Editor**: `@monaco-editor/react`
- **PDF Generation**: `jspdf`

### Backend
- **Framework**: Django, Django REST Framework
- **Database**: SQLite3
- **External APIs**: Judge0 (Compiler), Gemini/OpenAI (LLM Orchestration)

---

## 📦 Installation & Setup

### 1. Prerequisites
- **Python** (version 3.10 or higher)
- **Node.js** (version 18 or higher)
- **NPM**

### 2. Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the database migrations:
   ```bash
   python manage.py migrate
   ```
5. Start the Django development server:
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

### 3. Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```
2. Install the Node modules:
   ```bash
   npm install
   ```
3. Start the Next.js development server:
   ```bash
   npm run dev
   ```
4. Open your browser and navigate to `http://localhost:3000`.

---

## 🧪 Automated Testing
Run the backend tests to verify database classifies and Judge0 compiler services:
- **Compiler checks**: `python backend/test_compiler.py`
- **Cache validations**: `python backend/test_sql_cache.py`
