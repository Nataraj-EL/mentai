import os
import requests
import json
import re
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO
from datetime import datetime
from django.contrib.auth.models import User
from .models import Course, Module, Video, Quiz
from .serializers import CourseSerializer

from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import threading
from django.core.cache import cache


# Module-level fallback cache for dev/local
_course_cache = {}
_cache_lock = threading.Lock()

from .languages import LanguageRegistry
from .course_content import get_module_titles, get_prebuilt_code_examples, get_practice_problems, get_mini_labs, get_module_quiz, get_prebuilt_code_snippet, get_module_theory, get_mini_project, get_module_objectives
from .topic_classifier import TopicClassifier

class GenerateCourseView(APIView):
    def post(self, request):
        try:
            # Validate request data
            topic = request.data.get("topic")
            if not topic:
                return Response({
                    "error": "Topic is required", 
                    "details": "Please provide a 'topic' field in the request body",
                    "example": {"topic": "Java Programming"}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not isinstance(topic, str) or len(topic.strip()) == 0:
                return Response({
                    "error": "Invalid topic format",
                    "details": "Topic must be a non-empty string",
                    "example": {"topic": "Java Programming"}
                }, status=status.HTTP_400_BAD_REQUEST)

            
            # 1. Input Intelligence & Standardization
            # Classify first to get canonical data and correct typos (e.g. "pythin" -> "python")
            classification = TopicClassifier.classify(topic)
            
            # Use the intelligent Display Title for the course (e.g. "Python Programming")
            display_title = classification.get("display_title", topic.title())
            canonical_slug = classification["language"]
            execution_enabled = classification["execution_enabled"]
            topic_type = classification["type"]
            
            # Standardize title for consistent caching and UI
            topic = display_title
            
            print(f"Generating for: {topic} (Lang: {canonical_slug}, Exec: {execution_enabled})")
            
            # Check in-memory cache with standardized key
            if topic.lower() in _course_cache:
                return Response(_course_cache[topic.lower()], status=status.HTTP_200_OK)

            # Generate Course Structure (Fast Mode)
            # Pass canonical_language explicitly so we don't re-detect
            course_data = self.create_course_structure_fast(
                topic, 
                language=canonical_slug, 
                execution_enabled=execution_enabled,
                topic_type=topic_type
            )
            
            # Cache results
            _course_cache[topic.lower()] = course_data
            
            return Response(course_data, status=status.HTTP_201_CREATED)

        except ValueError as ve:
            return Response({
                "error": "Validation error", 
                "details": str(ve)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            print("[Backend Error] Exception in GenerateCourseView:", tb)
            return Response({
                "error": "Internal server error", 
                "details": "An unexpected error occurred while generating the course"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create_course_structure_fast(self, topic, language=None, execution_enabled=True, topic_type="EXECUTABLE"):
        """Dynamic course generation using Gemini AI with static fallback"""
        if not language:
            language = self.detect_programming_language(topic)
            
        # Try Gemini Generation First
        try:
            from .ai_service import GeminiService
            ai_service = GeminiService()
            
            if ai_service.client:
                print(f"Attempting valid Gemini generation for: {topic}")
                course_outline = ai_service.generate_course_structure(topic, language)
                
                if course_outline and "modules" in course_outline:
                    # Transform structure to match frontend expectations
                    modules = []
                    for mod in course_outline["modules"]:
                        mod_num = mod.get("module_number", len(modules) + 1)
                        # Generate detailed content for each module using Gemini
                        module_content = ai_service.generate_module_content(topic, language, mod["title"], mod_num)
                        
                        if not module_content:
                            # Fallback to static content for this module if AI fails
                            difficulty = "beginner" if mod_num <= 3 else "intermediate" if mod_num <= 7 else "advanced"
                            module_content = self.generate_unique_module_content(language, mod["title"], mod_num, difficulty, mod_num-1, topic=topic, topic_type=topic_type)
                        
                        module_data = {
                            "id": mod_num,
                            "name": f"Module {mod_num}: {mod['title']}",
                            "description": mod.get("description", ""),
                            "difficulty": mod.get("difficulty", "Intermediate"),
                            "order": mod_num,
                            "content": module_content.get("content", mod.get("description")),
                            "subsections": [
                                {"title": obj, "content": obj} for obj in mod.get("learning_objectives", [])
                            ],
                            # New Fields
                            "theory": module_content.get("theory", get_module_theory(language, mod["title"], mod_num)),
                            "mini_project": module_content.get("mini_project", get_mini_project(language, mod["title"], mod_num)),
                            
                            # Legacy
                            "code_examples": module_content.get("code_examples", []),
                            "real_world_examples": module_content.get("real_world_examples", []),
                            "mini_labs": module_content.get("mini_labs", []),
                            "quizzes": module_content.get("quizzes", []),
                            "learning_outcome": module_content.get("learning_outcome", "Master this module."),
                            "practice_problems": get_practice_problems(topic, mod["title"]),
                            "preloaded_code": get_prebuilt_code_snippet(topic, topic_type, mod_num-1, mod["title"])
                        }
                    modules.append(module_data)

                    return {
                        "course_title": course_outline.get("course_title", f"Complete {topic} Mastery Course"),
                        "course_content": course_outline.get("course_description", f"A comprehensive course covering {topic}."),
                        "topic": topic,
                        "modules": modules,
                        "metadata": {
                            "language": language,
                            "execution_enabled": execution_enabled,
                            "topic_type": topic_type
                        }
                    }
        except Exception as e:
            print(f"Gemini generation failed: {e}. Falling back to static content.")
            import traceback
            traceback.print_exc()

        # FALLBACK: Existing Static Logic
        print("Using static generation fallback...")
        module_titles = get_module_titles(language)
        
        # STRICT CONTENT INTEGRITY CHECK
        # If no syllabus exists (None), return "Under Construction".
        if not module_titles:
             return {
                "course_title": f"{topic} (Pending Content)",
                "course_content": f"We are actively building structured content for {topic}. Interactive modules are coming soon.",
                "topic": topic,
                "modules": [], # No modules generated
                "metadata": {
                    "language": language,
                    "execution_enabled": False,
                    "topic_type": "THEORY",
                    "is_pending": True
                }
            }

        modules = []
        for i, title in enumerate(module_titles):
            module_number = i + 1
            difficulty = "beginner" if module_number <= 3 else "intermediate" if module_number <= 7 else "advanced"
            
            module_content = self.generate_unique_module_content(language, title, module_number, difficulty, i, topic=topic, topic_type=topic_type)
            
            module_data = {
                "id": module_number,
                "name": f"Module {module_number}: {title}",
                "description": "", # Duration removed
                "difficulty": difficulty,
                "order": module_number,
                "content": module_content.get("content", f"Learn about {title}."),
                "subsections": [
                    {"title": obj, "content": obj} for obj in get_module_objectives(language, title, module_number)
                ],
                # New fields
                "theory": module_content.get("theory", get_module_theory(language, title, module_number)),
                "mini_project": module_content.get("mini_project", get_mini_project(language, title, module_number)),
                # Legacy
                "code_examples": module_content.get("code_examples", []),
                "real_world_examples": module_content.get("real_world_examples", []),
                "mini_labs": module_content.get("mini_labs", []),
                "quizzes": module_content.get("quizzes", []),
                "learning_outcome": module_content.get("learning_outcome", "Master this module."),
                "practice_problems": get_practice_problems(topic, title),
                "preloaded_code": get_prebuilt_code_snippet(topic, topic_type, i, module_title=title)
            }
            modules.append(module_data)
        
        return {
            "course_title": f"Complete {topic} Mastery Course",
            "course_content": f"A comprehensive course covering {topic}.",
            "topic": topic,
            "modules": modules,
            "metadata": {
                "language": language,
                "execution_enabled": execution_enabled,
                "topic_type": topic_type
            }
        }

    def generate_unique_module_content(self, language, module_title, module_number, difficulty, module_index, topic="", topic_type="EXECUTABLE"):
        """Generate unique, context-specific content for each module"""
        objectives = self.generate_module_specific_objectives(language, module_title, module_number)
        
        # New Refactored Content
        theory_content = get_module_theory(language, module_title, module_number)
        mini_project = get_mini_project(language, module_title, module_number)
        
        # Legacy items (kept if needed for compatibility, but intended to be replaced in UI)
        real_world_examples = [{
            "title": f"{module_title} in Industry",
            "description": f"Discover how {module_title.lower()} is applied in real-world {language} projects, such as {self.get_real_world_example(language, module_title, module_index)}.",
            "solution": f"Implement {module_title.lower()} to address challenges in {language} development.",
            "learning_outcome": f"Gain insight into the professional application of {module_title.lower()} in {language}."
        }]
        
        mini_labs = get_mini_labs(language, module_title, module_number, topic_type=topic_type)
        quizzes = get_module_quiz(topic, topic_type, module_title, module_number)
        preloaded_code = get_prebuilt_code_snippet(topic, topic_type, module_index, 0, module_title)
        
        learning_outcome = f"After completing this module, you will be able to apply {module_title.lower()} in {language} to solve real-world problems and build advanced applications."
        
        return {
            "content": f"Module {module_number}: {module_title}",
            "subsections": [
                {"title": obj, "content": obj} for obj in objectives
            ],
            # Pass new fields
            "theory": theory_content,
            "mini_project": mini_project,
            
            # Legacy/Frontend compatibility (can be empty lists if we update frontend strictly)
            "code_examples": [], # Removed as per directive
            "real_world_examples": real_world_examples,
            "mini_labs": mini_labs,
            "quizzes": quizzes,
            "learning_outcome": learning_outcome,
            "preloaded_code": preloaded_code
        }


    def generate_unique_code_examples(self, language, module_title, module_number, difficulty, module_index):
        """Generate 2-3 unique, language-specific code examples per module for Python and Rust"""
        examples = []
        
        if language == "Python":
            # Python-specific code examples based on module content
            if "introduction" in module_title.lower() or "environment" in module_title.lower():
                examples = [
                    {
                        "title": "Hello World in Python",
                        "code": "#!/usr/bin/env python3\n\n# Your first Python program\nprint(\"Hello, World!\")\n\n# Check Python version\nimport sys\nprint(f\"Python version: {sys.version}\")\n\n# Simple variable assignment\nname = \"Python Learner\"\nprint(f\"Welcome to {name}!\")",
                        "explanation": "Basic Python program demonstrating print statements, imports, and variable assignment.",
                        "language": "python"
                    },
                    {
                        "title": "Python Interactive Session",
                        "code": "# Start Python interactive session\n# python3\n\n# Basic arithmetic\nx = 10\ny = 5\nprint(f\"Addition: {x + y}\")\nprint(f\"Subtraction: {x - y}\")\nprint(f\"Multiplication: {x * y}\")\nprint(f\"Division: {x / y}\")\nprint(f\"Integer division: {x // y}\")\nprint(f\"Modulo: {x % y}\")\nprint(f\"Power: {x ** y}\")",
                        "explanation": "Demonstrates basic arithmetic operations and f-string formatting in Python.",
                        "language": "python"
                    }
                ]
            elif "variables" in module_title.lower() or "data types" in module_title.lower():
                examples = [
                    {
                        "title": "Python Data Types",
                        "code": "# Python data types demonstration\n\n# Numbers\ninteger_num = 42\nfloat_num = 3.14\ncomplex_num = 1 + 2j\n\n# Strings\nname = \"Python\"\nmessage = 'Hello, World!'\nmulti_line = \"\"\"\nThis is a\nmulti-line string\n\"\"\"\n\n# Boolean\nis_python = True\nis_java = False\n\n# Collections\nmy_list = [1, 2, 3, \"python\"]\nmy_tuple = (1, 2, 3)\nmy_dict = {\"name\": \"Python\", \"version\": 3.9}\nmy_set = {1, 2, 3, 4}\n\n# Type checking\nprint(f\"Type of integer_num: {type(integer_num)}\")\nprint(f\"Type of name: {type(name)}\")\nprint(f\"Type of my_list: {type(my_list)}\")",
                        "explanation": "Shows all major Python data types and type checking.",
                        "language": "python"
                    },
                    {
                        "title": "Variable Operations",
                        "code": "# Variable operations and type conversion\n\n# Dynamic typing\nx = 10\nprint(f\"x is {x}, type: {type(x)}\")\n\nx = \"ten\"\nprint(f\"x is now {x}, type: {type(x)}\")\n\n# Type conversion\nnumber_str = \"42\"\nnumber_int = int(number_str)\nnumber_float = float(number_str)\n\nprint(f\"String: {number_str}, type: {type(number_str)}\")\nprint(f\"Integer: {number_int}, type: {type(number_int)}\")\nprint(f\"Float: {number_float}, type: {type(number_float)}\")\n\n# Multiple assignment\na, b, c = 1, 2, 3\nprint(f\"a={a}, b={b}, c={c}\")",
                        "explanation": "Demonstrates dynamic typing and type conversion in Python.",
                        "language": "python"
                    }
                ]
            elif "control flow" in module_title.lower() or "conditionals" in module_title.lower():
                examples = [
                    {
                        "title": "Conditional Statements",
                        "code": "# Conditional statements in Python\n\nage = 18\n\n# Simple if statement\nif age >= 18:\n    print(\"You are an adult\")\nelse:\n    print(\"You are a minor\")\n\n# if-elif-else chain\ntemperature = 25\n\nif temperature < 0:\n    print(\"It's freezing!\")\nelif temperature < 10:\n    print(\"It's cold\")\nelif temperature < 20:\n    print(\"It's cool\")\nelif temperature < 30:\n    print(\"It's warm\")\nelse:\n    print(\"It's hot!\")\n\n# Conditional expressions (ternary operator)\nstatus = \"adult\" if age >= 18 else \"minor\"\nprint(f\"Status: {status}\")",
                        "explanation": "Shows if-elif-else statements and conditional expressions.",
                        "language": "python"
                    },
                    {
                        "title": "Loops in Python",
                        "code": "# Loops demonstration\n\n# For loop with range\nprint(\"Counting from 1 to 5:\")\nfor i in range(1, 6):\n    print(f\"  {i}\")\n\n# For loop with list\nfruits = [\"apple\", \"banana\", \"cherry\"]\nprint(\"\\nFruits:\")\nfor fruit in fruits:\n    print(f\"  {fruit}\")\n\n# While loop\nprint(\"\\nCountdown:\")\ncount = 5\nwhile count > 0:\n    print(f\"  {count}\")\n    count -= 1\nprint(\"  Blast off!\")\n\n# Loop with enumerate\nprint(\"\\nFruits with index:\")\nfor index, fruit in enumerate(fruits):\n    print(f\"  {index}: {fruit}\")",
                        "explanation": "Demonstrates for loops, while loops, and enumerate function.",
                        "language": "python"
                    }
                ]
            else:
                # Generic Python examples for other modules
                for i in range(2, 5):
                    examples.append({
                        "title": f"{module_title} Example {i-1}",
                        "code": f"# {module_title} in Python\ndef example_{module_number}_{i}():\n    # Implementation for {module_title.lower()} (Module {module_number}, Example {i})\n    print(f\"{module_title} - Example {i} in Python\")\n    \n    # Add specific logic based on module\n    if \"function\" in \"{module_title.lower()}\":\n        return f\"Function example {i}\"\n    elif \"data structure\" in \"{module_title.lower()}\":\n        return [1, 2, 3, i]\n    else:\n        return \"Example completed\"\n\nexample_{module_number}_{i}()",
                        "explanation": f"Demonstrates {module_title.lower()} in Python (Module {module_number}, Example {i}).",
                        "language": "python"
                    })
                    
        elif language == "Rust":
            # Rust-specific code examples based on module content
            if "introduction" in module_title.lower() or "environment" in module_title.lower():
                examples = [
                    {
                        "title": "Hello World in Rust",
                        "code": "// Your first Rust program\nfn main() {\n    println!(\"Hello, World!\");\n    \n    // Check Rust version (compile-time)\n    println!(\"Rust program compiled successfully!\");\n    \n    // Simple variable\n    let name = \"Rust Learner\";\n    println!(\"Welcome to {}!\", name);\n}",
                        "explanation": "Basic Rust program demonstrating println! macro and variable declaration.",
                        "language": "rust"
                    },
                    {
                        "title": "Rust Cargo Project",
                        "code": "// Cargo.toml\n// [package]\n// name = \"hello_rust\"\n// version = \"0.1.0\"\n// edition = \"2021\"\n\n// [dependencies]\n\n// src/main.rs\nfn main() {\n    println!(\"Hello from Cargo project!\");\n    \n    // Basic arithmetic\n    let x = 10;\n    let y = 5;\n    println!(\"Addition: {}\", x + y);\n    println!(\"Subtraction: {}\", x - y);\n    println!(\"Multiplication: {}\", x * y);\n    println!(\"Division: {}\", x / y);\n    println!(\"Remainder: {}\", x % y);\n}",
                        "explanation": "Shows a complete Rust project structure with Cargo and basic arithmetic.",
                        "language": "rust"
                    }
                ]
            elif "variables" in module_title.lower() or "data types" in module_title.lower() or "ownership" in module_title.lower():
                examples = [
                    {
                        "title": "Rust Data Types and Ownership",
                        "code": "fn main() {\n    // Basic data types\n    let integer: i32 = 42;\n    let float: f64 = 3.14;\n    let boolean: bool = true;\n    let character: char = 'A';\n    let string: String = String::from(\"Hello, Rust!\");\n    \n    // Ownership demonstration\n    let s1 = String::from(\"hello\");\n    let s2 = s1; // s1's value moves to s2\n    // println!(\"{}\", s1); // This would cause a compile error\n    println!(\"{}\", s2); // This works\n    \n    // Borrowing\n    let s3 = String::from(\"world\");\n    let len = calculate_length(&s3); // Borrow s3\n    println!(\"The length of '{}' is {}.\", s3, len);\n}\n\nfn calculate_length(s: &String) -> usize {\n    s.len()\n}",
                        "explanation": "Demonstrates Rust data types, ownership, and borrowing concepts.",
                        "language": "rust"
                    },
                    {
                        "title": "Mutable Variables",
                        "code": "fn main() {\n    // Immutable by default\n    let x = 5;\n    println!(\"x is: {}\", x);\n    \n    // Make it mutable\n    let mut y = 5;\n    println!(\"y is: {}\", y);\n    y = 6;\n    println!(\"y is now: {}\", y);\n    \n    // Shadowing\n    let z = 5;\n    let z = z + 1;\n    let z = z * 2;\n    println!(\"z is: {}\", z);\n    \n    // Type conversion with shadowing\n    let spaces = \"   \";\n    let spaces = spaces.len();\n    println!(\"Number of spaces: {}\", spaces);\n}",
                        "explanation": "Shows mutable variables, shadowing, and type conversion in Rust.",
                        "language": "rust"
                    }
                ]
            elif "control flow" in module_title.lower() or "functions" in module_title.lower():
                examples = [
                    {
                        "title": "Control Flow in Rust",
                        "code": "fn main() {\n    let number = 7;\n    \n    // if expression\n    if number < 5 {\n        println!(\"condition was true\");\n    } else {\n        println!(\"condition was false\");\n    }\n    \n    // if in let statement\n    let condition = true;\n    let number = if condition { 5 } else { 6 };\n    println!(\"The value of number is: {}\", number);\n    \n    // Loop\n    let mut count = 0;\n    loop {\n        count += 1;\n        if count == 5 {\n            break;\n        }\n    }\n    println!(\"Count: {}\", count);\n    \n    // While loop\n    let mut number = 3;\n    while number != 0 {\n        println!(\"{}\", number);\n        number -= 1;\n    }\n    println!(\"LIFTOFF!!!\");\n}",
                        "explanation": "Demonstrates if expressions, loops, and while loops in Rust.",
                        "language": "rust"
                    },
                    {
                        "title": "Functions in Rust",
                        "code": "fn main() {\n    // Function call\n    another_function(5, 6);\n    \n    // Function with return value\n    let x = five();\n    println!(\"The value of x is: {}\", x);\n    \n    // Function with expression\n    let y = {\n        let x = 3;\n        x + 1 // No semicolon = return value\n    };\n    println!(\"The value of y is: {}\", y);\n}\n\nfn another_function(x: i32, y: i32) {\n    println!(\"The value of x is: {} and y is: {}\", x, y);\n}\n\nfn five() -> i32 {\n    5 // Return value\n}",
                        "explanation": "Shows function definition, parameters, and return values in Rust.",
                        "language": "rust"
                    }
                ]
            else:
                # Generic Rust examples for other modules
                for i in range(2, 5):
                    examples.append({
                        "title": f"{module_title} Example {i-1}",
                        "code": f"// {module_title} in Rust\nfn example_{module_number}_{i}() -> String {{\n    // Implementation for {module_title.lower()} (Module {module_number}, Example {i})\n    println!(\"{module_title} - Example {{}} in Rust\", {i});\n    \n    // Add specific logic based on module\n    if \"{module_title.lower()}\".contains(\"function\") {{\n        return \"Function example\".to_string();\n    }} else if \"{module_title.lower()}\".contains(\"data structure\") {{\n        return format!(\"Data structure example {{}}\", {i});\n    }} else {{\n        return \"Example completed\".to_string();\n    }}\n}}\n\nfn main() {{\n    let result = example_{module_number}_{i}();\n    println!(\"{{}}\", result);\n}}",
                        "explanation": f"Demonstrates {module_title.lower()} in Rust (Module {module_number}, Example {i}).",
                        "language": "rust"
                    })
                
        else:
            # Generic fallback for other languages
            examples = []
            for i in range(1, 3):
                code_sample = f"// Sample code for {module_title} in {language}\n// Implement your logic here..."
                if language.lower() in ['python', 'ruby']:
                    code_sample = f"# Sample code for {module_title} in {language}\n# Implement your logic here..."
                
                examples.append({
                    "title": f"{module_title} Example {i}",
                    "code": code_sample,
                    "explanation": f"This is a placeholder example for {module_title} in {language}.",
                    "language": language.lower()
                })
                
        return examples

    def generate_module_specific_objectives(self, language, module_title, module_number):
        """Generate unique learning objectives based on module and language"""
        module_lower = module_title.lower()
        
        if language == "Python":
            if "introduction" in module_lower or "environment" in module_lower:
                return [
                    f"Set up a Python development environment with proper tools and IDEs (Module {module_number})",
                    f"Write and execute your first Python program using the interactive shell (Module {module_number})",
                    f"Understand Python's syntax rules, indentation, and basic program structure (Module {module_number})",
                    f"Navigate the Python ecosystem and understand version differences (Module {module_number})"
                ]
            elif "variables" in module_lower or "data types" in module_lower:
                return [
                    f"Master Python's dynamic typing system and variable declaration (Module {module_number})",
                    f"Work with all Python data types: numbers, strings, booleans, and collections (Module {module_number})",
                    f"Perform type conversion and understand Python's type system (Module {module_number})",
                    f"Use Python operators effectively for arithmetic, comparison, and logical operations (Module {module_number})"
                ]
            elif "control flow" in module_lower or "conditionals" in module_lower:
                return [
                    f"Write conditional statements using if, elif, and else constructs (Module {module_number})",
                    f"Implement loops using for and while statements with proper control (Module {module_number})",
                    f"Use loop control statements like break, continue, and else clauses (Module {module_number})",
                    f"Apply control flow to solve real-world programming problems (Module {module_number})"
                ]
            elif "functions" in module_lower or "scope" in module_lower:
                return [
                    f"Define and call functions with parameters and return values (Module {module_number})",
                    f"Understand Python's scope rules and variable lifetime (Module {module_number})",
                    f"Use default parameters, keyword arguments, and variable-length arguments (Module {module_number})",
                    f"Apply functions to organize code and promote reusability (Module {module_number})"
                ]
            elif "data structures" in module_lower or "lists" in module_lower or "dictionaries" in module_lower:
                return [
                    f"Create and manipulate lists, tuples, and dictionaries effectively (Module {module_number})",
                    f"Use list comprehensions and dictionary comprehensions for data processing (Module {module_number})",
                    f"Implement sets and understand their unique properties (Module {module_number})",
                    f"Choose appropriate data structures for different programming scenarios (Module {module_number})"
                ]
            elif "object-oriented" in module_lower or "oop" in module_lower:
                return [
                    f"Define classes and create objects in Python (Module {module_number})",
                    f"Implement inheritance, encapsulation, and polymorphism (Module {module_number})",
                    f"Use special methods and understand Python's object model (Module {module_number})",
                    f"Apply OOP principles to design maintainable and extensible code (Module {module_number})"
                ]
            elif "file" in module_lower or "i/o" in module_lower:
                return [
                    f"Read from and write to files using Python's file handling capabilities (Module {module_number})",
                    f"Work with different file formats including text, CSV, and JSON (Module {module_number})",
                    f"Use context managers for safe file operations (Module {module_number})",
                    f"Handle file-related exceptions and implement proper error handling (Module {module_number})"
                ]
            elif "exception" in module_lower or "debugging" in module_lower:
                return [
                    f"Use try-except blocks to handle exceptions gracefully (Module {module_number})",
                    f"Create custom exceptions and implement proper error handling (Module {module_number})",
                    f"Use debugging tools and techniques to troubleshoot Python code (Module {module_number})",
                    f"Write robust code that handles unexpected situations (Module {module_number})"
                ]
            elif "advanced" in module_lower or "libraries" in module_lower:
                return [
                    f"Use Python's standard library modules effectively (Module {module_number})",
                    f"Install and work with third-party packages using pip (Module {module_number})",
                    f"Implement advanced Python features like decorators and generators (Module {module_number})",
                    f"Apply best practices for Python development and code organization (Module {module_number})"
                ]
            else:
                return [
                    f"Master the key concepts of {module_title} in Python (Module {module_number})",
                    f"Apply {module_title} techniques to solve practical problems (Module {module_number})",
                    f"Build confidence through hands-on practice with Python (Module {module_number})",
                    f"Prepare for advanced Python development and real-world projects (Module {module_number})"
                ]
                
        elif language == "Rust":
            if "introduction" in module_lower or "environment" in module_lower:
                return [
                    f"Set up a Rust development environment with Cargo and rustc (Module {module_number})",
                    f"Create and build your first Rust project using Cargo (Module {module_number})",
                    f"Understand Rust's compilation process and error messages (Module {module_number})",
                    f"Navigate the Rust ecosystem and understand edition differences (Module {module_number})"
                ]
            elif "variables" in module_lower or "data types" in module_lower or "ownership" in module_lower:
                return [
                    f"Master Rust's ownership system and memory management (Module {module_number})",
                    f"Work with Rust's primitive types and understand type annotations (Module {module_number})",
                    f"Use borrowing and references to access data without taking ownership (Module {module_number})",
                    f"Apply ownership rules to write memory-safe Rust code (Module {module_number})"
                ]
            elif "control flow" in module_lower or "functions" in module_lower:
                return [
                    f"Write conditional expressions and use if statements effectively (Module {module_number})",
                    f"Implement loops using loop, while, and for constructs (Module {module_number})",
                    f"Define functions with proper signatures and return types (Module {module_number})",
                    f"Use control flow to solve problems while maintaining Rust's safety guarantees (Module {module_number})"
                ]
            elif "structs" in module_lower or "enums" in module_lower or "pattern matching" in module_lower:
                return [
                    f"Define and use structs to create custom data types (Module {module_number})",
                    f"Implement enums and understand their relationship with pattern matching (Module {module_number})",
                    f"Use match expressions and pattern matching for control flow (Module {module_number})",
                    f"Apply structs and enums to model real-world data effectively (Module {module_number})"
                ]
            elif "collections" in module_lower or "data structures" in module_lower:
                return [
                    f"Work with Rust's standard collections: Vec, HashMap, and HashSet (Module {module_number})",
                    f"Use iterators and iterator adaptors for data processing (Module {module_number})",
                    f"Implement custom data structures while respecting ownership rules (Module {module_number})",
                    f"Choose appropriate collections for different performance requirements (Module {module_number})"
                ]
            elif "error handling" in module_lower or "result" in module_lower or "option" in module_lower:
                return [
                    f"Use Result and Option types for robust error handling (Module {module_number})",
                    f"Implement proper error propagation using the ? operator (Module {module_number})",
                    f"Create custom error types and implement the Error trait (Module {module_number})",
                    f"Write code that handles errors gracefully without panicking (Module {module_number})"
                ]
            elif "file" in module_lower or "async" in module_lower:
                return [
                    f"Read from and write to files using Rust's standard library (Module {module_number})",
                    f"Work with async/await syntax for asynchronous programming (Module {module_number})",
                    f"Use tokio or other async runtimes for concurrent operations (Module {module_number})",
                    f"Handle I/O operations safely with proper error handling (Module {module_number})"
                ]
            elif "traits" in module_lower or "generics" in module_lower:
                return [
                    f"Define and implement traits to define shared behavior (Module {module_number})",
                    f"Use generic types and functions to write reusable code (Module {module_number})",
                    f"Implement trait bounds and understand trait objects (Module {module_number})",
                    f"Apply traits and generics to create flexible, type-safe abstractions (Module {module_number})"
                ]
            elif "memory safety" in module_lower or "concurrency" in module_lower:
                return [
                    f"Understand Rust's memory safety guarantees and zero-cost abstractions (Module {module_number})",
                    f"Use smart pointers like Box, Rc, and Arc for memory management (Module {module_number})",
                    f"Implement safe concurrent programming using threads and channels (Module {module_number})",
                    f"Apply Rust's concurrency primitives to solve real-world problems (Module {module_number})"
                ]
            else:
                return [
                    f"Master the key concepts of {module_title} in Rust (Module {module_number})",
                    f"Apply {module_title} techniques while maintaining Rust's safety guarantees (Module {module_number})",
                    f"Build confidence through hands-on practice with Rust (Module {module_number})",
                    f"Prepare for advanced Rust development and systems programming (Module {module_number})"
                ]
        else:
            # Generic objectives for other languages
            return [
                f"Understand the fundamental concepts of {module_title} in {language} (Module {module_number})",
                f"Write simple programs demonstrating {module_title} (Module {module_number})",
                f"Debug common errors related to {module_title} in {language} (Module {module_number})",
                f"Apply best practices for {module_title} (Module {module_number})"
            ]

    def get_real_world_example(self, language, module_title, module_index):
        # Return a unique real-world use case per module
        use_cases = [
            f"banking transaction systems using {module_title.lower()} in {language}",
            f"e-commerce platforms leveraging {module_title.lower()} in {language}",
            f"IoT device management with {module_title.lower()} in {language}",
            f"data analytics pipelines built with {module_title.lower()} in {language}",
            f"cloud-native microservices using {module_title.lower()} in {language}",
            f"mobile app development with {module_title.lower()} in {language}",
            f"AI/ML model deployment using {module_title.lower()} in {language}",
            f"blockchain solutions with {module_title.lower()} in {language}",
            f"real-time chat applications using {module_title.lower()} in {language}",
            f"cybersecurity tools built with {module_title.lower()} in {language}"
        ]
        return use_cases[module_index % len(use_cases)]




    def generate_instant_module_content(self, language, module_title, module_number, difficulty):
        """Generate module content instantly using templates"""
        # Pre-built learning objectives
        objectives = [
            f"Master fundamental concepts of {module_title}",
            f"Apply {module_title} in practical scenarios", 
            f"Build real-world applications using {module_title}",
            f"Understand best practices for {module_title}"
        ]
        
        # Pre-built explanatory content
        # Pre-built explanatory content
        explanatory_content = (
            f"This module provides comprehensive coverage of {module_title} in {language}. "
            "You'll learn essential concepts, practical applications, and industry best practices.\\n\\n"
            f"Key topics covered include fundamental principles, real-world use cases, and hands-on exercises that will help you master {module_title}. "
            f"The content is designed to be accessible for {difficulty} level learners while providing depth and practical value.\\n\\n"
            f"By the end of this module, you'll have a solid understanding of {module_title} and be able to apply these concepts in your own projects. "
            "The hands-on exercises and real-world examples will reinforce your learning and build your confidence."
        )
        
        # Pre-built code examples based on language
        # Pass module_number (extracted or default) to get scaled difficulty
        code_examples = get_prebuilt_code_examples(language, module_title, module_number)
        
        # Pre-built real-world examples
        real_world_examples = [{
            "title": f"Real-world Application of {module_title}",
            "description": f"{module_title} is widely used in industry for building scalable applications, data processing, and system development. Companies use these concepts to create robust, maintainable software solutions.",
            "solution": f"Apply {module_title} principles to design efficient, scalable solutions.",
            "learning_outcome": f"Understand how {module_title} is applied in professional software development."
        }]
        
        # Pre-built mini labs
        mini_labs = [{
            "title": f"{module_title} Practice Lab",
            "description": f"Complete these hands-on tasks to reinforce your understanding of {module_title} concepts in {language}.",
            "tasks": [
                f"Create a {language} program demonstrating {module_title} fundamentals",
                f"Build a practical application using {module_title} concepts",
                f"Implement best practices for {module_title} in {language}"
            ],
            "expected_outcome": f"You will gain practical experience implementing {module_title} concepts and be able to apply them to real-world scenarios."
        }]
        
        # Pre-built quizzes
        quizzes = self.get_prebuilt_quizzes(language, module_title)
        
        return {
            "content": f"Module {module_number}: {module_title}",
            "subsections": [
                {"title": obj, "content": obj} for obj in objectives
            ] + [
                {"title": "Explanatory Content", "content": explanatory_content}
            ],
            "code_examples": code_examples,
            "real_world_examples": real_world_examples,
            "mini_labs": mini_labs,
            "quizzes": quizzes
        }


    def get_prebuilt_quizzes(self, language, module_title):
        """Return pre-built quiz questions"""
        return [
            {
                "question": f"Which of the following is a key concept in {module_title}?",
                "options": [
                    f"a) Core {module_title} principles",
                    f"b) Hardware components", 
                    f"c) Network protocols",
                    f"d) Database design"
                ],
                "correct_answer": "a)",
                "explanation": f"{module_title} focuses on core programming principles and concepts."
            },
            {
                "question": f"What is the primary purpose of {module_title}?",
                "options": [
                    f"a) To build robust applications",
                    f"b) To design hardware",
                    f"c) To manage networks",
                    f"d) To create databases"
                ],
                "correct_answer": "a)",
                "explanation": f"{module_title} is used to build robust and scalable applications."
            },
            {
                "question": f"Which language feature is most important in {module_title}?",
                "options": [
                    f"a) Syntax and structure",
                    f"b) Hardware compatibility",
                    f"c) Network protocols",
                    f"d) Database queries"
                ],
                "correct_answer": "a)",
                "explanation": f"Proper syntax and structure are fundamental to {module_title}."
            },
            {
                "question": f"How does {module_title} improve code quality?",
                "options": [
                    f"a) Through best practices and patterns",
                    f"b) By optimizing hardware",
                    f"c) By managing networks",
                    f"d) By designing databases"
                ],
                "correct_answer": "a)",
                "explanation": f"{module_title} improves code quality through established best practices and design patterns."
            },
            {
                "question": f"What is the main benefit of learning {module_title}?",
                "options": [
                    f"a) Building better software",
                    f"b) Hardware optimization",
                    f"c) Network management",
                    f"d) Database administration"
                ],
                "correct_answer": "a)",
                "explanation": f"Learning {module_title} helps you build better, more maintainable software."
            }
        ]

    def create_course_structure(self, topic):
        topic_lower = topic.lower()
        # Dynamically generate 10 module titles based on topic and language
        language = self.detect_programming_language(topic)
        
        # Generate specific module titles based on language and progression
        module_titles = self.generate_module_titles(language, topic)
        
        if not module_titles:
            return {
                "course_title": f"{topic} (Pending Content)",
                "course_content": f"We are actively building structured content for {topic}.",
                "topic": topic,
                "modules": [],
                "metadata": {
                   "language": language,
                   "execution_enabled": False,
                   "topic_type": "THEORY"
                }
            }
        
        modules = []
        for i in range(len(module_titles)):
            module_number = i + 1
            module_title = module_titles[i]
            difficulty = (
                "beginner" if module_number <= 3 else
                "intermediate" if module_number <= 7 else
                "advanced"
            )
            module_content = self.generate_module_content(topic, module_title, module_number, difficulty)
            if not module_content: 
                # Fallback if generation fails
                module_content = {
                    "content": f"Content for {module_title}",
                    "subsections": [],
                    "code_examples": [],
                    "real_world_examples": [],
                    "mini_labs": [],
                    "quizzes": []
                }

            module_data = {
                "id": module_number,
                "name": f"Module {module_number}: {module_title}",
                "description": "",
                "difficulty": difficulty,
                "order": module_number,
                "content": module_content.get("content", ""),
                "subsections": module_content.get("subsections", []),
                "code_examples": module_content.get("code_examples", []),
                "real_world_examples": module_content.get("real_world_examples", []),
                "mini_labs": module_content.get("mini_labs", []),
                "quizzes": module_content.get("quizzes", [])
            }
            modules.append(module_data)
        return {
            "course_title": f"Complete {topic} Mastery Course",
            "course_content": f"A comprehensive course covering {topic} from fundamentals to advanced applications with hands-on projects and real-world examples.",
            "topic": topic,
            "modules": modules
        }

    def generate_module_titles(self, language, topic):
        """Generate specific module titles based on language and progression"""
        return get_module_titles(language)

    def generate_module_content(self, topic, module_title, module_number, difficulty):
        prompt = self.create_module_specific_prompt(topic, module_title, module_number, difficulty)
        try:
            GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=60
            )
            if response.status_code == 200:
                data = response.json()
                if "candidates" in data and data["candidates"]:
                    content_text = data["candidates"][0]["content"]["parts"][0]["text"]
                    parsed_content = self.parse_module_content(content_text, topic, module_title, module_number)
                    if self.validate_module_content(parsed_content, module_title):
                        return parsed_content
            raise ValueError(f"Failed to generate valid content for module {module_number}: {module_title}")
        except Exception as e:
            raise ValueError(f"Module Generation Error for {module_title}: {e}")

    def create_module_specific_prompt(self, topic, module_title, module_number, difficulty):
        language = self.detect_programming_language(topic)
        return f"You are an expert course builder for a professional LMS. Generate content for a programming course module with the following requirements:\n\nTopic: {topic}\nProgramming Language: {language}\nModule: {module_number} - {module_title}\nDifficulty: {difficulty}\n\nSTRICT REQUIREMENTS:\n- All content must be specific to the module title and programming language.\n- No generic, placeholder, fallback, or repeated content.\n- No emojis. No repeated headings. No cross-language code. No placeholder print statements.\n- All code must be real, compile-worthy, and relevant to the module and language.\n- If you cannot generate a section, leave it empty (do not use placeholders).\n\nFORMAT:\n### Learning Objectives\n\n### Explanatory Content\n\n### Code Examples\n\n### Mini Labs\n- 3 unique, hands-on tasks for this module and language\n\n### Real-World Use Cases\n- 1–2 real-world, language- and module-specific use cases\n\n### Quiz\n- 10 unique, module- and language-specific multiple choice questions\n- Each question must have 4 real, meaningful options, a correct answer, and a short explanation\n- No placeholder or generic options\n\nReturn ONLY the content in the exact format above. Do not include any extra text, instructions, or repeated headings."

    def detect_programming_language(self, topic):
        """
        Detects the programming language from the topic string using strict classifier.
        Does NOT default to Python for unknown topics.
        """
        try:
            classification = TopicClassifier.classify(topic)
            # If classifier returns "general" or "sql" (Non-Executable), return that.
            # Do NOT fallback to "python" here.
            return classification["language"]
        except Exception:
            return "general"

    def is_generic_content(self, content_text, module_title):
        generic_phrases = [
            "This module provides comprehensive coverage",
            "Python Programming Example",
            "used in various industries",
            "This module covers",
            "basic implementation",
            "fundamental concepts",
            "Task 1, Task 2, Task 3",
            "Example 1: Python Programming",
            "This example demonstrates",
            "Apply Python Programming concepts",
            "print(\"This is a demonstration of",
            "console.log(\"This is a demonstration of"
        ]
        
        content_lower = content_text.lower()
        module_lower = module_title.lower()
        
        # Check for generic phrases
        for phrase in generic_phrases:
            if phrase.lower() in content_lower:
                return True
        
        # Check if module title is not mentioned in content
        if module_lower not in content_lower:
            return True
        
        # Check for repeated placeholder patterns
        if content_text.count("Example") > 3 and "Programming" in content_text:
            return True
        
        # Check for cross-language pollution
        if self.has_cross_language_pollution(content_text, module_title):
            return True
        
        return False

    def has_cross_language_pollution(self, content_text, module_title):
        topic = "Python"  # Default, should be passed from context
        language = self.detect_programming_language(topic)
        
        # Language-specific pollution checks for Python and Rust only
        if language == "Python":
            # Check for Rust-specific syntax in Python content
            rust_patterns = [
                "fn ", "let ", "mut ", "&mut ", "&", "-> ", "::", "Result<", "Option<",
                "match ", "Some(", "None", "Ok(", "Err(", "unwrap()", "expect(",
                "Vec<", "String::", "println!", "vec![", "struct ", "enum ",
                "impl ", "trait ", "Box<", "Rc<", "Arc<", "Mutex<", "RwLock<"
            ]
            for pattern in rust_patterns:
                if pattern in content_text:
                    return True
                    
        elif language == "Rust":
            # Check for Python-specific syntax in Rust content
            python_patterns = [
                "def ", "import ", "print(", "with open(", "f\"", "elif ", "True/False",
                "range(", "len(", "append(", "strip()", "split()", "class ",
                "self.", "if __name__", "try:", "except:", "finally:", "raise ",
                "yield ", "lambda ", "map(", "filter(", "reduce(", "list(", "dict("
            ]
            for pattern in python_patterns:
                if pattern in content_text:
                    return True
            # Check for missing Rust syntax
            if "fn " not in content_text and "function" in content_text:
                return True
            if "let " not in content_text and "variable" in content_text:
                return True
        
        return False

    def validate_module_content(self, parsed_content, module_title):
        required_sections = ["subsections", "code_examples", "real_world_examples", "mini_labs"]
        
        for section in required_sections:
            if section not in parsed_content or not parsed_content[section]:
                return False
        
        # Check if content is too generic
        content_text = str(parsed_content)
        if self.is_generic_content(content_text, module_title):
            return False
        
        # Check for cross-language pollution
        if self.has_cross_language_pollution(content_text, module_title):
            return False
        
        return True

    def create_high_quality_fallback_content(self, topic, module_title, module_number, difficulty):
        # Use the existing detailed fallback methods
        learning_objectives = self.generate_learning_objectives(module_title, topic)
        explanatory_content = self.generate_explanatory_content(module_title, topic)
        code_examples = self.generate_code_examples(module_title, topic)
        real_world_examples = self.generate_real_world_examples(module_title, topic)
        mini_labs = self.generate_mini_labs(module_title, topic)
        return {
            "content": f"Module {module_number}: {module_title}",
            "subsections": [
                {"title": obj.replace('-', '').strip(), "content": obj.replace('-', '').strip()} for obj in learning_objectives
            ] + [
                {"title": "Explanatory Content", "content": explanatory_content}
            ],
            "code_examples": code_examples,
            "real_world_examples": real_world_examples,
            "mini_labs": mini_labs,
            "quizzes": self.generate_quiz_questions(topic, module_title, module_number)
        }

    def parse_module_content(self, content_text, topic, module_title=None, module_number=None):
        import random
        topic = topic or "Course Topic"
        module_title = module_title or "Module"
        module_number = module_number or 1
        content_text = re.sub(r'### Quiz.*?(?=\n\n|$)', '', content_text, flags=re.DOTALL)
        sections = {
            "content": content_text,
            "code_examples": [],
            "real_world_examples": [],
            "mini_labs": [],
            "quizzes": []
        }
        # --- Learning Objectives ---
        objectives_match = re.search(r'### Learning Objectives\n(.*?)(?=\n\n###|$)', content_text, re.DOTALL)
        learning_objectives = []
        if objectives_match:
            objectives_content = objectives_match.group(1).strip()
            learning_objectives = [obj.strip() for obj in objectives_content.split('\n') if obj.strip().startswith('-')]
        if not learning_objectives:
            learning_objectives = self.generate_learning_objectives(module_title, topic)
        sections["subsections"] = [
            {"title": obj.replace('-', '').strip(), "content": obj.replace('-', '').strip()} for obj in learning_objectives
        ]
        # --- Explanatory Content ---
        explanatory_match = re.search(r'### Explanatory Content\n(.*?)(?=\n\n###|$)', content_text, re.DOTALL)
        explanatory_content = ""
        if explanatory_match:
            explanatory_content = explanatory_match.group(1).strip()
        if not explanatory_content:
            explanatory_content = self.generate_explanatory_content(module_title, topic)
        sections["subsections"].append({
            "title": "Explanatory Content",
            "content": explanatory_content
        })
        # --- Code Examples ---
        code_blocks = re.findall(r'```(\w+)\n(.*?)\n```', content_text, re.DOTALL)
        code_examples = []
        for i, (language, code) in enumerate(code_blocks):
            title = f"Example {i+1}: {module_title}"
            if '#' in code:
                first_line = code.split('\n')[0]
                if first_line.strip().startswith('#'):
                    title = first_line.strip('# ').strip()
            code_examples.append({
                "title": title,
                "code": code.strip(),
                "explanation": f"This example demonstrates {module_title} in action.",
                "language": language
            })
        if not code_examples:
            code_examples = self.generate_code_examples(module_title, topic)
        sections["code_examples"] = code_examples
        # --- Real-World Use Case ---
        use_case_match = re.search(r'### Real-World Use Case\n(.*?)(?=\n\n###|$)', content_text, re.DOTALL)
        real_world_examples = []
        if use_case_match:
            use_case_content = use_case_match.group(1).strip()
            if use_case_content:
                real_world_examples.append({
                    "title": f"Real-world Application of {module_title}",
                    "description": use_case_content,
                    "solution": f"Apply {module_title} concepts to real-world problems.",
                    "learning_outcome": f"Understand how {module_title} is used in practice."
                })
        if not real_world_examples:
            real_world_examples = self.generate_real_world_examples(module_title, topic)
        sections["real_world_examples"] = real_world_examples
        # --- Mini Lab ---
        lab_match = re.search(r'### Mini Lab\n(.*?)(?=\n\n###|$)', content_text, re.DOTALL)
        mini_labs = []
        if lab_match:
            lab_content = lab_match.group(1).strip()
            tasks = []
            lines = lab_content.split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('###'):
                    clean_line = re.sub(r'^\d+\.\s*', '', line)
                    clean_line = re.sub(r'^-\s*', '', clean_line)
                    if clean_line:
                        tasks.append(clean_line)
            if tasks:
                mini_labs.append({
                    "title": f"{module_title} Practice Lab",
                    "description": f"Try these hands-on tasks to reinforce your learning about {module_title}.",
                    "tasks": tasks[:3],
                    "expected_outcome": f"You will gain practical experience with {module_title}."
                })
        if not mini_labs:
            mini_labs = self.generate_mini_labs(module_title, topic)
        sections["mini_labs"] = mini_labs
        # --- Content (for display, not used by frontend) ---
        content_without_code = re.sub(r'```[\s\S]*?```', '', content_text)
        content_cleaned = re.sub(r'### Learning Objectives\n.*?(?=\n\n###|$)', '', content_without_code, flags=re.DOTALL)
        content_cleaned = re.sub(r'### Explanatory Content\n.*?(?=\n\n###|$)', '', content_cleaned, flags=re.DOTALL)
        content_cleaned = re.sub(r'### Code Examples\n.*?(?=\n\n###|$)', '', content_cleaned, flags=re.DOTALL)
        content_cleaned = re.sub(r'### Real-World Use Case\n.*?(?=\n\n###|$)', '', content_cleaned, flags=re.DOTALL)
        content_cleaned = re.sub(r'### Mini Lab\n.*?(?=\n\n###|$)', '', content_cleaned, flags=re.DOTALL)
        content_cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', content_cleaned)
        sections["content"] = content_cleaned.strip()
        # --- Quizzes (unchanged) ---
        sections["quizzes"] = self.generate_quiz_questions(topic, module_title, module_number)
        return sections

    def generate_learning_objectives(self, module_title, topic):
        module_lower = module_title.lower()
        language = self.detect_programming_language(topic)
        
        if "introduction" in module_lower or "environment" in module_lower or "setup" in module_lower:
            return [
                f"Set up a {language} development environment on your system",
                f"Understand basic {language} syntax and program structure",
                f"Write and run your first {language} program",
                f"Use an IDE or text editor for {language} development"
            ]
        elif "variable" in module_lower or "data type" in module_lower or "operator" in module_lower:
            return [
                f"Understand {language}'s basic data types and their characteristics",
                f"Learn how to declare and use variables effectively in {language}",
                f"Master arithmetic, comparison, and logical operators in {language}",
                f"Practice type conversion and data manipulation in {language}"
            ]
        elif "control flow" in module_lower or "conditionals" in module_lower or "loops" in module_lower:
            return [
                f"Understand how to use control flow statements in {language}",
                f"Learn to write conditional statements and loops in {language}",
                f"Identify and fix common mistakes in control flow logic",
                f"Apply control flow to create interactive programs in {language}"
            ]
        elif "function" in module_lower or "method" in module_lower or "scope" in module_lower:
            return [
                f"Define and call functions/methods in {language}",
                f"Understand parameters, arguments, and return values in {language}",
                f"Use functions to organize and reuse code effectively",
                f"Apply scope rules and best practices in {language}"
            ]
        elif "data structure" in module_lower or "array" in module_lower or "collection" in module_lower:
            return [
                f"Understand and use data structures in {language}",
                f"Learn how to create, access, and modify collections",
                f"Practice using data structures to solve real-world problems",
                f"Choose the right data structure for a given task in {language}"
            ]
        elif "oop" in module_lower or "object-oriented" in module_lower or "class" in module_lower:
            return [
                f"Understand the principles of Object-Oriented Programming in {language}",
                f"Create and use classes and objects in {language}",
                f"Apply inheritance, encapsulation, and polymorphism",
                f"Design reusable and maintainable code using OOP in {language}"
            ]
        elif "file" in module_lower or "input" in module_lower or "output" in module_lower or "i/o" in module_lower:
            return [
                f"Understand how to read and write files using {language}",
                f"Learn different file modes and when to use each",
                f"Use proper file handling patterns for safe operations",
                f"Handle file-related exceptions and errors properly"
            ]
        elif "exception" in module_lower or "error" in module_lower or "debugging" in module_lower:
            return [
                f"Identify common errors and exceptions in {language}",
                f"Use proper exception handling mechanisms in {language}",
                f"Create custom exceptions for specific error conditions",
                f"Write robust code that handles unexpected situations gracefully"
            ]
        elif "library" in module_lower or "module" in module_lower or "framework" in module_lower:
            return [
                f"Import and use built-in and third-party modules in {language}",
                f"Understand the {language} package ecosystem",
                f"Install and manage packages using appropriate tools",
                f"Use popular libraries for common programming tasks"
            ]
        elif "advanced" in module_lower or "decorator" in module_lower or "generator" in module_lower:
            return [
                f"Understand and use advanced {language} features",
                f"Apply advanced programming patterns and techniques",
                f"Use memory management and optimization techniques",
                f"Master advanced {language} features for professional development"
            ]
        else:
            return [
                f"Master the key concepts of {module_title} in {language}",
                f"Apply {module_title} in practical scenarios",
                f"Solve real-world problems using {module_title} techniques",
                f"Build confidence through hands-on practice with {language}"
            ]

    def generate_explanatory_content(self, module_title, topic):
        language = self.detect_programming_language(topic)
        module_titles = self.generate_module_titles(language, topic)
        try:
            module_number = module_titles.index(module_title) + 1
        except Exception:
            module_number = None
        # Only use unique content for Python and Rust
        if language in ("Python", "Rust") and module_number:
            return self.get_unique_explanatory_content(language, module_title, module_number)
        return ""

    def generate_code_examples(self, module_title, topic):
        module_lower = module_title.lower()
        language = self.detect_programming_language(topic)
        
        if "data structure" in module_lower or "lists" in module_lower or "tuples" in module_lower or "dictionaries" in module_lower or "array" in module_lower or "collection" in module_lower:
            # Dynamic code example generation enforced; fallback removed
            return []
        elif "control flow" in module_lower or "conditionals" in module_lower or "loops" in module_lower:
            if language == "Python":
                return [
                    {
                        "title": "If-elif-else Statements",
                        "code": "# Grade classification\nscore = int(input('Enter your score: '))\n\nif score >= 90:\n    print('Grade: A')\nelif score >= 80:\n    print('Grade: B')\nelif score >= 70:\n    print('Grade: C')\nelse:\n    print('Grade: F')",
                        "explanation": "Shows how to use if-elif-else for multiple conditions.",
                        "language": "python"
                    },
                    {
                        "title": "For Loop with Range",
                        "code": "# Print numbers 1 to 5\nfor i in range(1, 6):\n    print(i)\n\n# Loop through a list\nfruits = ['apple', 'banana', 'cherry']\nfor fruit in fruits:\n    print(f'I like {fruit}')",
                        "explanation": "Demonstrates for loops with range and list iteration.",
                        "language": "python"
                    },
                    {
                        "title": "While Loop with Counter",
                        "code": "# Countdown from 5\ncount = 5\nwhile count > 0:\n    print(count)\n    count -= 1\nprint('Blast off!')\n\n# Keep asking until valid input\nwhile True:\n    age = input('Enter your age: ')\n    if age.isdigit() and 0 <= int(age) <= 120:\n        break\n    print('Please enter a valid age (0-120)')",
                        "explanation": "Shows while loops for counting and input validation.",
                        "language": "python"
                    }
                ]
            elif language == "Java":
                return [
                    {
                        "title": "If-else Statements",
                        "code": "// Grade classification\nScanner scanner = new Scanner(System.in);\nSystem.out.print(\"Enter your score: \");\nint score = scanner.nextInt();\n\nif (score >= 90) {\n    System.out.println(\"Grade: A\");\n} else if (score >= 80) {\n    System.out.println(\"Grade: B\");\n} else if (score >= 70) {\n    System.out.println(\"Grade: C\");\n} else {\n    System.out.println(\"Grade: F\");\n}",
                        "explanation": "Shows how to use if-else for multiple conditions in Java.",
                        "language": "java"
                    },
                    {
                        "title": "For Loop with Arrays",
                        "code": "// Print numbers 1 to 5\nfor (int i = 1; i <= 5; i++) {\n    System.out.println(i);\n}\n\n// Loop through an array\nString[] fruits = {\"apple\", \"banana\", \"cherry\"};\nfor (String fruit : fruits) {\n    System.out.println(\"I like \" + fruit);\n}",
                        "explanation": "Demonstrates for loops with traditional syntax and enhanced for loop.",
                        "language": "java"
                    },
                    {
                        "title": "While Loop with Counter",
                        "code": "// Countdown from 5\nint count = 5;\nwhile (count > 0) {\n    System.out.println(count);\n    count--;\n}\nSystem.out.println(\"Blast off!\");\n\n// Keep asking until valid input\nScanner input = new Scanner(System.in);\nwhile (true) {\n    System.out.print(\"Enter your age: \");\n    String ageStr = input.nextLine();\n    try {\n        int age = Integer.parseInt(ageStr);\n        if (age >= 0 && age <= 120) {\n            break;\n        }\n    } catch (NumberFormatException e) {\n        // Invalid input\n    }\n    System.out.println(\"Please enter a valid age (0-120)\");\n}",
                        "explanation": "Shows while loops for counting and input validation with exception handling.",
                        "language": "java"
                    }
                ]
            elif language == "JavaScript":
                return [
                    {
                        "title": "If-else Statements",
                        "code": "// Grade classification\nconst score = parseInt(prompt('Enter your score:'));\n\nif (score >= 90) {\n    console.log('Grade: A');\n} else if (score >= 80) {\n    console.log('Grade: B');\n} else if (score >= 70) {\n    console.log('Grade: C');\n} else {\n    console.log('Grade: F');\n}",
                        "explanation": "Shows how to use if-else for multiple conditions in JavaScript.",
                        "language": "javascript"
                    },
                    {
                        "title": "For Loop with Arrays",
                        "code": "// Print numbers 1 to 5\nfor (let i = 1; i <= 5; i++) {\n    console.log(i);\n}\n\n// Loop through an array\nconst fruits = ['apple', 'banana', 'cherry'];\nfor (const fruit of fruits) {\n    console.log(`I like ${fruit}`);\n}\n\n// Using forEach method\nfruits.forEach(fruit => {\n    console.log(`I like ${fruit}`);\n});",
                        "explanation": "Demonstrates for loops with traditional syntax, for-of loop, and forEach method.",
                        "language": "javascript"
                    },
                    {
                        "title": "While Loop with Counter",
                        "code": "// Countdown from 5\nlet count = 5;\nwhile (count > 0) {\n    console.log(count);\n    count--;\n}\nconsole.log('Blast off!');\n\n// Keep asking until valid input\nwhile (true) {\n    const age = prompt('Enter your age:');\n    const ageNum = parseInt(age);\n    if (!isNaN(ageNum) && ageNum >= 0 && ageNum <= 120) {\n        break;\n    }\n    console.log('Please enter a valid age (0-120)');\n}",
                        "explanation": "Shows while loops for counting and input validation.",
                        "language": "javascript"
                    }
                ]
            else:
                # Generate language-specific control flow examples
                if language == "Python":
                    return []
                elif language == "Java":
                    return []
                elif language == "JavaScript":
                    return []
                elif language == "C++":
                    return []
                elif language == "C#":
                    return []
                else:
                    return [
                        {
                            "title": f"Control Flow in {language}",
                            "code": f"// {module_title} demonstration\n// This shows control flow in {language}",
                            "explanation": f"This code demonstrates {module_title} in {language}.",
                            "language": language.lower()
                        }
                    ]
        elif "function" in module_lower or "method" in module_lower or "scope" in module_lower:
            if language == "Python":
                return [
                    {
                        "title": "Basic Function Definition",
                        "code": "def greet(name):\n    \"\"\"Return a personalized greeting.\"\"\"\n    return f'Hello, {name}!'\n\n# Call the function\nmessage = greet('Alice')\nprint(message)",
                        "explanation": "Demonstrates function definition, docstring, and calling.",
                        "language": "python"
                    },
                    {
                        "title": "Function with Multiple Parameters",
                        "code": "def calculate_area(length, width):\n    \"\"\"Calculate the area of a rectangle.\"\"\"\n    area = length * width\n    return area\n\n# Calculate area of a 5x3 rectangle\nresult = calculate_area(5, 3)\nprint(f'Area: {result} square units')",
                        "explanation": "Shows functions with multiple parameters and return values.",
                        "language": "python"
                    },
                    {
                        "title": "Function with Default Parameters",
                        "code": "def create_profile(name, age, city='Unknown'):\n    \"\"\"Create a user profile with optional city.\"\"\"\n    return {\n        'name': name,\n        'age': age,\n        'city': city\n    }\n\n# Create profiles\nprofile1 = create_profile('Bob', 25)\nprofile2 = create_profile('Alice', 30, 'New York')\nprint(profile1)\nprint(profile2)",
                        "explanation": "Demonstrates default parameters and dictionary return.",
                        "language": "python"
                    }
                ]
            elif language == "Java":
                return [
                    {
                        "title": "Basic Method Definition",
                        "code": "public class Greeter {\n    public String greet(String name) {\n        return \"Hello, \" + name + \"!\";\n    }\n    \n    public static void main(String[] args) {\n        Greeter greeter = new Greeter();\n        String message = greeter.greet(\"Alice\");\n        System.out.println(message);\n    }\n}",
                        "explanation": "Demonstrates method definition and calling in Java.",
                        "language": "java"
                    },
                    {
                        "title": "Method with Multiple Parameters",
                        "code": "public class Calculator {\n    public int calculateArea(int length, int width) {\n        return length * width;\n    }\n    \n    public static void main(String[] args) {\n        Calculator calc = new Calculator();\n        int result = calc.calculateArea(5, 3);\n        System.out.println(\"Area: \" + result + \" square units\");\n    }\n}",
                        "explanation": "Shows methods with multiple parameters and return values.",
                        "language": "java"
                    },
                    {
                        "title": "Method Overloading",
                        "code": "public class Profile {\n    public String createProfile(String name, int age) {\n        return createProfile(name, age, \"Unknown\");\n    }\n    \n    public String createProfile(String name, int age, String city) {\n        return \"Name: \" + name + \", Age: \" + age + \", City: \" + city;\n    }\n    \n    public static void main(String[] args) {\n        Profile profile = new Profile();\n        System.out.println(profile.createProfile(\"Bob\", 25));\n        System.out.println(profile.createProfile(\"Alice\", 30, \"New York\"));\n    }\n}",
                        "explanation": "Demonstrates method overloading for default parameters.",
                        "language": "java"
                    }
                ]
            elif language == "JavaScript":
                return [
                    {
                        "title": "Basic Function Definition",
                        "code": "function greet(name) {\n    return `Hello, ${name}!`;\n}\n\n// Call the function\nconst message = greet('Alice');\nconsole.log(message);\n\n// Arrow function syntax\nconst greetArrow = (name) => `Hello, ${name}!`;\nconsole.log(greetArrow('Bob'));",
                        "explanation": "Demonstrates function definition and arrow function syntax.",
                        "language": "javascript"
                    },
                    {
                        "title": "Function with Multiple Parameters",
                        "code": "function calculateArea(length, width) {\n    return length * width;\n}\n\n// Calculate area of a 5x3 rectangle\nconst result = calculateArea(5, 3);\nconsole.log(`Area: ${result} square units`);\n\n// Using arrow function\nconst area = (l, w) => l * w;\nconsole.log(`Area: ${area(4, 6)} square units`);",
                        "explanation": "Shows functions with multiple parameters and return values.",
                        "language": "javascript"
                    },
                    {
                        "title": "Function with Default Parameters",
                        "code": "function createProfile(name, age, city = 'Unknown') {\n    return {\n        name: name,\n        age: age,\n        city: city\n    };\n}\n\n// Create profiles\nconst profile1 = createProfile('Bob', 25);\nconst profile2 = createProfile('Alice', 30, 'New York');\nconsole.log(profile1);\nconsole.log(profile2);",
                        "explanation": "Demonstrates default parameters and object return.",
                        "language": "javascript"
                    }
                ]
            else:
                # Generate language-specific function examples
                if language == "Python":
                    return []
                elif language == "Java":
                    return []
                elif language == "JavaScript":
                    return []
                elif language == "C++":
                    return []
                elif language == "C#":
                    return []
                else:
                    return [
                        {
                            "title": f"Functions in {language}",
                            "code": f"// {module_title} demonstration\n// This shows functions in {language}",
                            "explanation": f"This code demonstrates {module_title} in {language}.",
                            "language": language.lower()
                        }
                    ]
        elif "file" in module_lower or "input" in module_lower or "output" in module_lower or "i/o" in module_lower:
            # Generate language-specific file I/O examples
            if language == "Python":
                return [
                    {
                        "title": "Reading a Text File",
                        "code": "# Read a text file line by line\nwith open('data.txt', 'r') as file:\n    for line in file:\n        print(line.strip())\n\n# Read entire file content\nwith open('data.txt', 'r') as file:\n    content = file.read()\n    print(content)",
                        "explanation": "Shows how to read files using the 'with' statement safely.",
                        "language": "python"
                    },
                    {
                        "title": "Writing to a Log File",
                        "code": "# Write user input to a log file\nuser_input = input('Enter your message: ')\nwith open('log.txt', 'a') as file:\n    file.write(f'{user_input}\\n')\nprint('Message logged successfully!')",
                        "explanation": "Demonstrates appending data to a file.",
                        "language": "python"
                    },
                    {
                        "title": "Reading CSV File",
                        "code": "import csv\n\n# Read CSV file\nwith open('students.csv', 'r') as file:\n    reader = csv.reader(file)\n    for row in reader:\n        print(f'Name: {row[0]}, Grade: {row[1]}')",
                        "explanation": "Shows how to work with CSV files using the csv module.",
                        "language": "python"
                    }
                ]
            elif language == "Java":
                return [
                    {
                        "title": "Reading a Text File",
                        "code": "import java.io.*;\nimport java.nio.file.*;\n\npublic class FileReader {\n    public static void main(String[] args) {\n        try {\n            // Read file line by line\n            Path path = Paths.get(\"data.txt\");\n            Files.lines(path).forEach(System.out::println);\n            \n            // Read entire file content\n            String content = Files.readString(path);\n            System.out.println(content);\n        } catch (IOException e) {\n            System.err.println(\"Error reading file: \" + e.getMessage());\n        }\n    }\n}",
                        "explanation": "Shows how to read files using Java NIO.2 API safely.",
                        "language": "java"
                    },
                    {
                        "title": "Writing to a Log File",
                        "code": "import java.io.*;\nimport java.time.LocalDateTime;\n\npublic class LogWriter {\n    public static void main(String[] args) {\n        try (FileWriter writer = new FileWriter(\"log.txt\", true)) {\n            String message = \"User activity logged\";\n            String timestamp = LocalDateTime.now().toString();\n            writer.write(timestamp + \": \" + message + \"\\n\");\n            System.out.println(\"Message logged successfully!\");\n        } catch (IOException e) {\n            System.err.println(\"Error writing to file: \" + e.getMessage());\n        }\n    }\n}",
                        "explanation": "Demonstrates writing to files with timestamps in Java.",
                        "language": "java"
                    },
                    {
                        "title": "Reading CSV File",
                        "code": "import java.io.*;\nimport java.util.*;\n\npublic class CSVReader {\n    public static void main(String[] args) {\n        try (BufferedReader reader = new BufferedReader(new FileReader(\"students.csv\"))) {\n            String line;\n            while ((line = reader.readLine()) != null) {\n                String[] parts = line.split(\",\");\n                if (parts.length >= 2) {\n                    System.out.println(\"Name: \" + parts[0] + \", Grade: \" + parts[1]);\n                }\n            }\n        } catch (IOException e) {\n            System.err.println(\"Error reading CSV: \" + e.getMessage());\n        }\n    }\n}",
                        "explanation": "Shows how to parse CSV files manually in Java.",
                        "language": "java"
                    }
                ]
            elif language == "JavaScript":
                return [
                    {
                        "title": "Reading a Text File (Node.js)",
                        "code": "const fs = require('fs');\n\n// Read file asynchronously\nfs.readFile('data.txt', 'utf8', (err, data) => {\n    if (err) {\n        console.error('Error reading file:', err);\n        return;\n    }\n    console.log(data);\n});\n\n// Read file synchronously\nconst content = fs.readFileSync('data.txt', 'utf8');\nconsole.log(content);",
                        "explanation": "Shows how to read files using Node.js fs module.",
                        "language": "javascript"
                    },
                    {
                        "title": "Writing to a Log File",
                        "code": "const fs = require('fs');\n\n// Write to log file\nconst message = 'User activity logged';\nconst timestamp = new Date().toISOString();\nconst logEntry = `${timestamp}: ${message}\\n`;\n\nfs.appendFile('log.txt', logEntry, (err) => {\n    if (err) {\n        console.error('Error writing to file:', err);\n        return;\n    }\n    console.log('Message logged successfully!');\n});",
                        "explanation": "Demonstrates appending data to files with timestamps.",
                        "language": "javascript"
                    },
                    {
                        "title": "Reading CSV File",
                        "code": "const fs = require('fs');\n\n// Read and parse CSV file\nfs.readFile('students.csv', 'utf8', (err, data) => {\n    if (err) {\n        console.error('Error reading file:', err);\n        return;\n    }\n    \n    const lines = data.split('\\n');\n    lines.forEach(line => {\n        const parts = line.split(',');\n        if (parts.length >= 2) {\n            console.log(`Name: ${parts[0]}, Grade: ${parts[1]}`);\n        }\n    });\n});",
                        "explanation": "Shows how to parse CSV files manually in Node.js.",
                        "language": "javascript"
                    }
                ]
            else:
                # Generate language-specific file I/O examples
                if language == "Python":
                    return []
                elif language == "Java":
                    return []
                elif language == "JavaScript":
                    return []
                elif language == "C++":
                    return []
                elif language == "C#":
                    return []
                elif language == "C":
                    return []
                else:
                    return [
                        {
                            "title": f"File I/O in {language}",
                            "code": f"// {module_title} demonstration\n// This shows file I/O operations in {language}",
                            "explanation": f"This code demonstrates {module_title} in {language}.",
                            "language": language.lower()
                        }
                    ]
        elif "exception" in module_lower or "error" in module_lower or "debugging" in module_lower:
            # Generate language-specific exception handling examples
            if language == "Python":
                return [
                    {
                        "title": "Basic Exception Handling",
                        "code": "try:\n    number = int(input('Enter a number: '))\n    result = 10 / number\n    print(f'Result: {result}')\nexcept ValueError:\n    print('Please enter a valid number')\nexcept ZeroDivisionError:\n    print('Cannot divide by zero')",
                        "explanation": "Shows how to handle different types of exceptions.",
                        "language": "python"
                    },
                    {
                        "title": "Custom Exception",
                        "code": "class InvalidAgeError(Exception):\n    pass\n\ndef validate_age(age):\n    if age < 0 or age > 120:\n        raise InvalidAgeError('Age must be between 0 and 120')\n    return age\n\ntry:\n    age = validate_age(150)\nexcept InvalidAgeError as e:\n    print(f'Error: {e}')",
                        "explanation": "Demonstrates creating and raising custom exceptions.",
                        "language": "python"
                    },
                    {
                        "title": "File Exception Handling",
                        "code": "try:\n    with open('nonexistent.txt', 'r') as file:\n        content = file.read()\nexcept FileNotFoundError:\n    print('File not found. Creating new file...')\n    with open('nonexistent.txt', 'w') as file:\n        file.write('This is a new file')",
                        "explanation": "Shows how to handle file-related exceptions.",
                        "language": "python"
                    }
                ]
            elif language == "Java":
                return [
                    {
                        "title": "Basic Exception Handling",
                        "code": "import java.util.Scanner;\n\npublic class ExceptionHandling {\n    public static void main(String[] args) {\n        Scanner scanner = new Scanner(System.in);\n        \n        try {\n            System.out.print(\"Enter a number: \");\n            int number = Integer.parseInt(scanner.nextLine());\n            int result = 10 / number;\n            System.out.println(\"Result: \" + result);\n            \n        } catch (NumberFormatException e) {\n            System.out.println(\"Please enter a valid number\");\n        } catch (ArithmeticException e) {\n            System.out.println(\"Cannot divide by zero\");\n        } finally {\n            scanner.close();\n        }\n    }\n}",
                        "explanation": "Shows how to handle different types of exceptions in Java.",
                        "language": "java"
                    },
                    {
                        "title": "Custom Exception",
                        "code": "class InvalidAgeException extends Exception {\n    public InvalidAgeException(String message) {\n        super(message);\n    }\n}\n\npublic class CustomException {\n    public static void validateAge(int age) throws InvalidAgeException {\n        if (age < 0 || age > 120) {\n            throw new InvalidAgeException(\"Age must be between 0 and 120\");\n        }\n    }\n    \n    public static void main(String[] args) {\n        try {\n            validateAge(150);\n        } catch (InvalidAgeException e) {\n            System.out.println(\"Error: \" + e.getMessage());\n        }\n    }\n}",
                        "explanation": "Demonstrates creating and using custom exceptions.",
                        "language": "java"
                    },
                    {
                        "title": "File Exception Handling",
                        "code": "import java.io.*;\n\npublic class FileExceptionHandling {\n    public static void main(String[] args) {\n        try {\n            File file = new File(\"nonexistent.txt\");\n            BufferedReader reader = new BufferedReader(new FileReader(file));\n            String line = reader.readLine();\n            reader.close();\n        } catch (FileNotFoundException e) {\n            System.out.println(\"File not found. Creating new file...\");\n            try {\n                FileWriter writer = new FileWriter(\"nonexistent.txt\");\n                writer.write(\"This is a new file\");\n                writer.close();\n            } catch (IOException ex) {\n                System.err.println(\"Error creating file: \" + ex.getMessage());\n            }\n        } catch (IOException e) {\n            System.err.println(\"Error reading file: \" + e.getMessage());\n        }\n    }\n}",
                        "explanation": "Shows how to handle file-related exceptions in Java.",
                        "language": "java"
                    }
                ]
            elif language == "JavaScript":
                return [
                    {
                        "title": "Basic Exception Handling",
                        "code": "// Basic exception handling in JavaScript\ntry {\n    const number = parseInt(prompt('Enter a number:'));\n    if (isNaN(number)) {\n        throw new Error('Invalid number entered');\n    }\n    const result = 10 / number;\n    console.log(`Result: ${result}`);\n} catch (error) {\n    if (error.message === 'Invalid number entered') {\n        console.log('Please enter a valid number');\n    } else if (error instanceof TypeError) {\n        console.log('Cannot divide by zero');\n    } else {\n        console.log('An error occurred:', error.message);\n    }\n}",
                        "explanation": "Shows how to handle different types of exceptions in JavaScript.",
                        "language": "javascript"
                    },
                    {
                        "title": "Custom Exception",
                        "code": "// Custom exception class\nclass InvalidAgeError extends Error {\n    constructor(message) {\n        super(message);\n        this.name = 'InvalidAgeError';\n    }\n}\n\nfunction validateAge(age) {\n    if (age < 0 || age > 120) {\n        throw new InvalidAgeError('Age must be between 0 and 120');\n    }\n    return age;\n}\n\ntry {\n    validateAge(150);\n} catch (error) {\n    if (error instanceof InvalidAgeError) {\n        console.log('Error:', error.message);\n    }\n}",
                        "explanation": "Demonstrates creating and using custom exceptions in JavaScript.",
                        "language": "javascript"
                    },
                    {
                        "title": "File Exception Handling (Node.js)",
                        "code": "const fs = require('fs');\n\n// File exception handling in Node.js\ntry {\n    const data = fs.readFileSync('nonexistent.txt', 'utf8');\n    console.log(data);\n} catch (error) {\n    if (error.code === 'ENOENT') {\n        console.log('File not found. Creating new file...');\n        try {\n            fs.writeFileSync('nonexistent.txt', 'This is a new file');\n            console.log('File created successfully');\n        } catch (writeError) {\n            console.error('Error creating file:', writeError.message);\n        }\n    } else {\n        console.error('Error reading file:', error.message);\n    }\n}",
                        "explanation": "Shows how to handle file-related exceptions in Node.js.",
                        "language": "javascript"
                    }
                ]
            elif language == "C++":
                return [
                    {
                        "title": "Basic Exception Handling",
                        "code": "#include <iostream>\n#include <stdexcept>\nusing namespace std;\n\nint main() {\n    try {\n        int number;\n        cout << \"Enter a number: \";\n        cin >> number;\n        \n        if (cin.fail()) {\n            throw invalid_argument(\"Invalid number entered\");\n        }\n        \n        if (number == 0) {\n            throw runtime_error(\"Cannot divide by zero\");\n        }\n        \n        int result = 10 / number;\n        cout << \"Result: \" << result << endl;\n        \n    } catch (const invalid_argument& e) {\n        cout << \"Please enter a valid number\" << endl;\n    } catch (const runtime_error& e) {\n        cout << e.what() << endl;\n    } catch (...) {\n        cout << \"An unexpected error occurred\" << endl;\n    }\n    \n    return 0;\n}",
                        "explanation": "Shows how to handle different types of exceptions in C++.",
                        "language": "cpp"
                    },
                    {
                        "title": "Custom Exception",
                        "code": "#include <iostream>\n#include <stdexcept>\n#include <string>\nusing namespace std;\n\nclass InvalidAgeException : public exception {\nprivate:\n    string message;\npublic:\n    InvalidAgeException(const string& msg) : message(msg) {}\n    \n    const char* what() const noexcept override {\n        return message.c_str();\n    }\n};\n\nvoid validateAge(int age) {\n    if (age < 0 || age > 120) {\n        throw InvalidAgeException(\"Age must be between 0 and 120\");\n    }\n}\n\nint main() {\n    try {\n        validateAge(150);\n    } catch (const InvalidAgeException& e) {\n        cout << \"Error: \" << e.what() << endl;\n    }\n    \n    return 0;\n}",
                        "explanation": "Demonstrates creating and using custom exceptions in C++.",
                        "language": "cpp"
                    }
                ]
            elif language == "C#":
                return [
                    {
                        "title": "Basic Exception Handling",
                        "code": "using System;\n\nclass ExceptionHandling {\n    static void Main(string[] args) {\n        try {\n            Console.Write(\"Enter a number: \");\n            int number = Convert.ToInt32(Console.ReadLine());\n            \n            if (number == 0) {\n                throw new DivideByZeroException(\"Cannot divide by zero\");\n            }\n            \n            int result = 10 / number;\n            Console.WriteLine($\"Result: {result}\");\n            \n        } catch (FormatException) {\n            Console.WriteLine(\"Please enter a valid number\");\n        } catch (DivideByZeroException e) {\n            Console.WriteLine(e.Message);\n        } catch (Exception e) {\n            Console.WriteLine($\"An error occurred: {e.Message}\");\n        }\n    }\n}",
                        "explanation": "Shows how to handle different types of exceptions in C#.",
                        "language": "csharp"
                    },
                    {
                        "title": "Custom Exception",
                        "code": "using System;\n\npublic class InvalidAgeException : Exception {\n    public InvalidAgeException(string message) : base(message) { }\n}\n\nclass CustomException {\n    static void ValidateAge(int age) {\n        if (age < 0 || age > 120) {\n            throw new InvalidAgeException(\"Age must be between 0 and 120\");\n        }\n    }\n    \n    static void Main(string[] args) {\n        try {\n            ValidateAge(150);\n        } catch (InvalidAgeException e) {\n            Console.WriteLine($\"Error: {e.Message}\");\n        }\n    }\n}",
                        "explanation": "Demonstrates creating and using custom exceptions in C#.",
                        "language": "csharp"
                    }
                ]
            else:
                # Generate language-specific exception handling examples
                if language == "Python":
                    return []
                elif language == "Java":
                    return []
                elif language == "JavaScript":
                    return []
                elif language == "C++":
                    return []
                elif language == "C#":
                    return []
                elif language == "C":
                    return []
                else:
                    return [
                        {
                            "title": f"Exception Handling in {language}",
                            "code": f"// {module_title} demonstration\n// This shows exception handling in {language}",
                            "explanation": f"This code demonstrates {module_title} in {language}.",
                            "language": language.lower()
                        }
                    ]
        else:
            # Generate language-specific code examples based on module topic
            if language == "Python":
                return []
            elif language == "Java":
                return []
            elif language == "JavaScript":
                return []
            elif language == "C++":
                return []
            elif language == "C#":
                return []
            elif language == "C":
                return []
            else:
                return [
                    {
                        "title": f"Basic {module_title} Example",
                        "code": f"// {module_title} demonstration\nconsole.log('Learning {module_title}');",
                        "explanation": f"This demonstrates basic concepts of {module_title}.",
                        "language": language.lower()
                    }
                ]

    def generate_real_world_examples(self, module_title, topic):
        module_lower = module_title.lower()
        
        if "data structure" in module_lower or "lists" in module_lower or "tuples" in module_lower or "dictionaries" in module_lower:
            use_case = (
                "Data structures are fundamental to almost every application. In web development, lists store user comments or product catalogs, tuples represent database records, and dictionaries map user IDs to user profiles. E-commerce sites use dictionaries to store shopping cart items with product IDs as keys and quantities as values.\n\n"
                "In data science, lists store datasets, tuples represent immutable data points, and dictionaries organize metadata. APIs use dictionaries to send JSON data between services. Game development uses lists for player inventories, tuples for coordinates, and dictionaries for character attributes."
            )
        elif "control flow" in module_lower or "conditionals" in module_lower or "loops" in module_lower:
            use_case = (
                "Control flow is essential in web applications for form validation, user authentication, and dynamic content generation. E-commerce sites use conditionals to check inventory levels and loops to display product lists. Automation scripts use loops to process files and conditionals to handle different file types.\n\n"
                "In data processing, loops iterate through datasets while conditionals filter and transform data. Game development relies heavily on control flow for game logic, user input handling, and AI behavior. Control flow enables programs to respond intelligently to different situations and user inputs."
            )
        elif "function" in module_lower or "scope" in module_lower:
            use_case = (
                "Functions are the building blocks of modular software. Web frameworks use functions to handle HTTP requests, process forms, and generate responses. Data processing pipelines use functions to transform, filter, and analyze data. API development relies on functions to validate input, process business logic, and format responses.\n\n"
                "Functions enable code reuse across projects and teams. They make testing easier by isolating specific behaviors. Functions also improve code readability by giving meaningful names to code blocks and hiding implementation details."
            )
        elif "file" in module_lower or "input" in module_lower or "output" in module_lower or "i/o" in module_lower:
            use_case = (
                "File handling is crucial for data persistence and processing. Logging systems write application events to log files for debugging and monitoring. Configuration management systems read settings from files to configure applications. Data processing applications read input files, process the data, and write results to output files.\n\n"
                "Web applications use file handling for user uploads, report generation, and data export. Backup systems read files from one location and write them to another. File handling is also essential for working with different data formats like CSV, JSON, XML, and binary files."
            )
        elif "exception" in module_lower or "error" in module_lower or "debugging" in module_lower:
            use_case = (
                "Exception handling is critical in production software. Web applications use try-except blocks to handle network errors, invalid user input, and database connection issues. File processing applications handle file not found errors and permission issues gracefully.\n\n"
                "APIs use exception handling to return appropriate error responses instead of crashing. Financial applications require robust error handling to prevent data corruption and ensure transaction integrity. Exception handling is also essential for logging and monitoring systems."
            )
        else:
            use_case = (
                f"{module_title} is used in many real-world scenarios. This module gives you the skills to apply it in practice."
            )
        
        return [{
            "title": f"Real-world Application of {module_title}",
            "description": use_case,
            "solution": f"Use the techniques from this module to design and implement a solution.",
            "learning_outcome": f"You will see how {module_title} is valuable in real projects."
        }]

    def generate_mini_labs(self, module_title, topic):
        module_lower = module_title.lower()
        language = self.detect_programming_language(topic)
        
        if "introduction" in module_lower or "environment" in module_lower or "setup" in module_lower:
            if language == "Python":
                tasks = [
                    "Create a Python script that displays your name, age, and favorite programming language. Use variables to store the information and print them with formatted strings.",
                    "Write a program that calculates and displays the area of a circle given its radius. Use the formula: area = π × radius². Import the math module for π.",
                    "Build a simple calculator that takes two numbers from user input and performs addition, subtraction, multiplication, and division operations."
                ]
            elif language == "Java":
                tasks = [
                    "Create a Java program that displays your personal information (name, age, city) using variables and System.out.println statements.",
                    "Write a Java application that calculates the perimeter of a rectangle given length and width. Use Scanner class for user input.",
                    "Build a simple temperature converter that converts Celsius to Fahrenheit using the formula: F = C × 9/5 + 32."
                ]
            elif language == "JavaScript":
                tasks = [
                    "Create a JavaScript program that displays your profile information using template literals and console.log statements.",
                    "Write a script that calculates the volume of a cube given its side length. Use prompt() for input and alert() for output.",
                    "Build a simple interest calculator that computes simple interest given principal, rate, and time."
                ]
            else:
                tasks = [
                    f"Create a {language} program that displays your name and current date using proper {language} syntax.",
                    f"Write a {language} application that performs basic arithmetic operations on two user-provided numbers.",
                    f"Build a simple {language} program that demonstrates variable declaration and output formatting."
                ]
        
        elif "variable" in module_lower or "data type" in module_lower or "operator" in module_lower:
            if language == "Python":
                tasks = [
                    "Create a program that demonstrates all Python data types: string, integer, float, boolean, list, tuple, and dictionary. Print each variable with its type.",
                    "Write a calculator that uses all arithmetic operators (+, -, *, /, //, %, **) and displays the results in a formatted table.",
                    "Build a type converter that takes user input and converts it between different data types (string to int, float to string, etc.)."
                ]
            elif language == "Java":
                tasks = [
                    "Create a Java program that demonstrates primitive data types (int, double, char, boolean) and String. Display each variable with its type information.",
                    "Write a Java application that performs all arithmetic operations and displays the results. Include increment and decrement operators.",
                    "Build a type conversion utility that demonstrates casting between different numeric types and handles potential data loss."
                ]
            elif language == "JavaScript":
                tasks = [
                    "Create a JavaScript program that demonstrates all data types: string, number, boolean, object, array, null, and undefined. Use typeof operator.",
                    "Write a script that performs all arithmetic and comparison operations, displaying results in a structured format.",
                    "Build a data type checker that identifies and converts user input to appropriate JavaScript types."
                ]
            else:
                tasks = [
                    f"Create a {language} program that demonstrates all basic data types and their characteristics.",
                    f"Write a {language} application that performs arithmetic operations and displays results with proper formatting.",
                    f"Build a type demonstration program that shows variable declaration and type checking in {language}."
                ]
        
        elif "control flow" in module_lower or "conditionals" in module_lower or "loops" in module_lower:
            if language == "Python":
                tasks = [
                    "Create a grade calculator that takes a score and returns the letter grade (A: 90+, B: 80-89, C: 70-79, D: 60-69, F: <60). Use if-elif-else statements.",
                    "Write a program that prints the first 20 Fibonacci numbers using a for loop. Store the sequence in a list.",
                    "Build a password validator that checks if a password meets criteria: at least 8 characters, contains uppercase, lowercase, and digit."
                ]
            elif language == "Java":
                tasks = [
                    "Create a Java program that determines the day of the week based on a number (1-7) using switch statement. Handle invalid inputs.",
                    "Write a Java application that generates a multiplication table for numbers 1-10 using nested for loops.",
                    "Build a number guessing game where the computer generates a random number and the user tries to guess it with hints."
                ]
            elif language == "JavaScript":
                tasks = [
                    "Create a JavaScript program that determines the season based on month number using switch statement and displays appropriate message.",
                    "Write a script that generates a pattern of asterisks using nested loops (e.g., triangle, square, diamond patterns).",
                    "Build a simple quiz game that asks multiple-choice questions and tracks the user's score."
                ]
            else:
                tasks = [
                    f"Create a {language} program that uses conditional statements to solve a real-world problem.",
                    f"Write a {language} application that demonstrates different types of loops with practical examples.",
                    f"Build a {language} program that combines conditionals and loops to create an interactive application."
                ]
        
        elif "function" in module_lower or "method" in module_lower or "scope" in module_lower:
            if language == "Python":
                tasks = [
                    "Create a function that calculates the factorial of a number using recursion. Include input validation and error handling.",
                    "Write a function that takes a list of numbers and returns statistics (sum, average, min, max). Use multiple return values.",
                    "Build a function that validates email addresses using regular expressions and returns True/False."
                ]
            elif language == "Java":
                tasks = [
                    "Create a Java class with methods to calculate area and perimeter of different shapes (circle, rectangle, triangle). Use method overloading.",
                    "Write a Java application with a recursive method to calculate the nth Fibonacci number. Include input validation.",
                    "Build a utility class with static methods for common string operations (reverse, palindrome check, word count)."
                ]
            elif language == "JavaScript":
                tasks = [
                    "Create a JavaScript function that implements a simple calculator with operations as parameters. Use arrow functions and default parameters.",
                    "Write a function that processes an array of objects and returns filtered/sorted results based on criteria.",
                    "Build a function that generates random passwords with specified length and character types."
                ]
            else:
                tasks = [
                    f"Create {language} functions that demonstrate parameter passing and return values.",
                    f"Write {language} methods that solve practical problems using proper scope and naming conventions.",
                    f"Build {language} functions that demonstrate different programming patterns and best practices."
                ]
        
        elif "data structure" in module_lower or "array" in module_lower or "collection" in module_lower:
            if language == "Python":
                tasks = [
                    "Create a contact management system using dictionaries. Implement add, search, update, and delete operations for contacts.",
                    "Write a program that processes a list of student grades and calculates statistics (mean, median, mode) using list operations.",
                    "Build a simple inventory system using nested dictionaries to track products with categories, prices, and stock levels."
                ]
            elif language == "Java":
                tasks = [
                    "Create a Java program that manages a list of books using ArrayList. Implement add, remove, search, and sort operations.",
                    "Write a Java application that uses HashMap to create a simple dictionary with word definitions and synonyms.",
                    "Build a student grade tracker using arrays and ArrayLists to store and calculate GPA for multiple students."
                ]
            elif language == "JavaScript":
                tasks = [
                    "Create a JavaScript program that manages a todo list using arrays and objects. Implement add, complete, delete, and filter operations.",
                    "Write a script that processes user data using Map and Set to create a unique user registry with contact information.",
                    "Build a shopping cart system using arrays of objects to manage products, quantities, and total calculations."
                ]
            else:
                tasks = [
                    f"Create a {language} program that demonstrates array/list operations with practical examples.",
                    f"Write a {language} application that uses collections to solve a real-world data management problem.",
                    f"Build a {language} program that combines different data structures to create a useful application."
                ]
        
        elif "oop" in module_lower or "object-oriented" in module_lower or "class" in module_lower:
            if language == "Python":
                tasks = [
                    "Create a BankAccount class with methods for deposit, withdraw, and balance check. Include proper validation and error handling.",
                    "Write a Student class that manages student information and grades. Implement methods to add courses, calculate GPA, and generate reports.",
                    "Build a Shape hierarchy with base class Shape and derived classes Circle, Rectangle, Triangle. Implement area and perimeter calculations."
                ]
            elif language == "Java":
                tasks = [
                    "Create a Java class hierarchy for vehicles (Vehicle, Car, Motorcycle, Truck) with inheritance and polymorphism. Include common methods and unique features.",
                    "Write a Java application with Employee class hierarchy (Employee, Manager, Developer) using inheritance and interface implementation.",
                    "Build a banking system with Account abstract class and concrete classes (Savings, Checking) with different interest calculations."
                ]
            elif language == "JavaScript":
                tasks = [
                    "Create JavaScript classes for a library management system (Book, Library, Member) with proper encapsulation and methods.",
                    "Write a class hierarchy for geometric shapes using ES6 classes and inheritance. Implement area and perimeter calculations.",
                    "Build a simple game system with classes for Player, Game, and ScoreBoard using object-oriented principles."
                ]
            else:
                tasks = [
                    f"Create {language} classes that demonstrate inheritance and polymorphism with practical examples.",
                    f"Write {language} classes that implement encapsulation and abstraction for real-world entities.",
                    f"Build a {language} class hierarchy that solves a complex problem using object-oriented design principles."
                ]
        
        elif "file" in module_lower or "input" in module_lower or "output" in module_lower or "i/o" in module_lower:
            if language == "Python":
                tasks = [
                    "Create a Python program that reads employee data from a CSV file and displays it in a formatted table. Handle missing data gracefully.",
                    "Write a log file system that records user activities with timestamps. Implement log rotation and different log levels (INFO, WARNING, ERROR).",
                    "Build a configuration file reader that reads settings from a JSON file and applies them to program behavior."
                ]
            elif language == "Java":
                tasks = [
                    "Create a Java program that reads employee data from a text file and displays it in a formatted table. Use BufferedReader and proper exception handling.",
                    "Write a Java application that creates a log file with timestamps and different log levels. Implement log rotation based on file size.",
                    "Build a configuration manager that reads properties from a .properties file and applies them to application settings."
                ]
            elif language == "JavaScript":
                tasks = [
                    "Create a JavaScript program that reads and writes JSON data to files. Implement a simple database-like system for storing user profiles.",
                    "Write a script that processes CSV data and converts it to different formats (JSON, XML). Handle various data types and edge cases.",
                    "Build a configuration system that reads settings from a JSON file and provides a simple API for accessing configuration values."
                ]
            elif language == "C":
                tasks = [
                    "Create a C program that reads employee data from a text file and displays it in a formatted table. Use fopen(), fgets(), and proper error handling.",
                    "Write a C application that creates a log file with timestamps using time.h functions. Implement log rotation based on file size.",
                    "Build a configuration file reader that reads settings from a simple text file and applies them to program behavior using C file I/O functions."
                ]
            else:
                tasks = [
                    f"Create a {language} program that reads data from files and processes it according to specific requirements.",
                    f"Write a {language} application that writes structured data to files with proper formatting and error handling.",
                    f"Build a {language} file processing system that handles different file formats and data types."
                ]
        
        elif "exception" in module_lower or "error" in module_lower or "debugging" in module_lower:
            if language == "Python":
                tasks = [
                    "Create a Python program that handles various exceptions (ValueError, FileNotFoundError, ZeroDivisionError) with specific error messages and recovery actions.",
                    "Write a custom exception hierarchy for a banking application (InsufficientFundsError, InvalidAccountError, TransactionError).",
                    "Build a robust input validation system that handles different types of user input errors and provides helpful error messages."
                ]
            elif language == "Java":
                tasks = [
                    "Create a Java application with comprehensive exception handling for file operations, network connections, and user input validation.",
                    "Write a custom exception hierarchy for a student management system (InvalidGradeException, StudentNotFoundException, DuplicateStudentException).",
                    "Build a robust calculator that handles arithmetic exceptions, input validation errors, and provides detailed error reporting."
                ]
            elif language == "JavaScript":
                tasks = [
                    "Create a JavaScript application with try-catch blocks for handling API calls, file operations, and user input validation.",
                    "Write a custom error handling system for a web form validation with specific error types and user-friendly messages.",
                    "Build a robust data processing system that handles various types of errors and provides fallback mechanisms."
                ]
            elif language == "C":
                tasks = [
                    "Create a C program that handles various error conditions using return values and errno. Implement proper error checking for file operations and user input.",
                    "Write a robust C application that uses error codes and error handling functions like perror() and strerror() for comprehensive error reporting.",
                    "Build a C program that demonstrates defensive programming techniques with proper null pointer checks and boundary validation."
                ]
            else:
                tasks = [
                    f"Create a {language} program that demonstrates comprehensive exception handling for common error scenarios.",
                    f"Write a {language} application with custom exception classes for domain-specific error conditions.",
                    f"Build a {language} error handling system that provides robust error recovery and user feedback."
                ]
        
        else:
            tasks = [
                f"Create a {language} program that demonstrates key concepts from {module_title} with practical implementation.",
                f"Write a {language} application that solves a real-world problem using {module_title} techniques and best practices.",
                f"Build a {language} project that showcases advanced features and patterns related to {module_title}."
            ]
        
        return [{
            "title": f"{module_title} Practice Lab",
            "description": f"Complete these hands-on tasks to reinforce your understanding of {module_title} concepts in {language}.",
            "tasks": tasks,
            "expected_outcome": f"You will gain practical experience implementing {module_title} concepts and be able to apply them to real-world scenarios."
        }]

    def generate_quiz_questions(self, topic, module_title=None, module_number=None):
        import random
        language = self.detect_programming_language(topic)
        if not module_title:
            raise ValueError("Module title is required for quiz generation.")
        module_lower = module_title.lower()

        # Define key concepts for common module types (expandable)
        concept_map = {
            'python': {
                'control flow': [
                    ("Which keyword is used for a conditional statement in Python?", ["if", "when", "cond", "switch"], "if", "'if' is used for conditionals in Python."),
                    ("Which statement is used to exit a loop early?", ["break", "stop", "exit", "return"], "break", "'break' exits a loop early in Python."),
                    ("What is the output of: for i in range(3): print(i)?", ["0 1 2", "1 2 3", "0 1 2 3", "1 2"], "0 1 2", "range(3) produces 0, 1, 2."),
                    ("Which loop is best for iterating over a list?", ["for", "while", "do-while", "loop"], "for", "'for' is used to iterate over lists in Python."),
                    ("Which keyword is used for an else-if condition in Python?", ["elif", "elseif", "else if", "elseif()"], "elif", "'elif' is the correct syntax for else-if in Python."),
                    ("What does the 'continue' statement do in a loop?", ["Skip to next iteration", "Exit the loop", "Skip the entire loop", "Restart the loop"], "Skip to next iteration", "'continue' skips the current iteration and continues with the next."),
                    ("Which operator is used for exponentiation in Python?", ["**", "^", "pow", "exp"], "**", "** is the exponentiation operator in Python."),
                    ("What is the result of 5 // 2 in Python?", ["2", "2.5", "2.0", "3"], "2", "// performs integer division in Python."),
                    ("Which function is used to get the length of a list?", ["len()", "length()", "size()", "count()"], "len()", "len() returns the number of items in a list."),
                    ("What is the correct way to check if a key exists in a dictionary?", ["if key in dict", "if dict.has_key(key)", "if dict.contains(key)", "if dict[key]"], "if key in dict", "Use 'in' operator to check if a key exists in a dictionary.")
                ],
                'oop': [
                    ("Which keyword is used to define a class in Python?", ["class", "object", "struct", "type"], "class", "'class' is used to define classes in Python."),
                    ("What is the first parameter of instance methods in Python?", ["self", "this", "cls", "obj"], "self", "'self' refers to the instance in Python methods."),
                    ("How do you create an object from a class?", ["obj = MyClass()", "obj = new MyClass()", "obj = MyClass.create()", "obj = class MyClass()"], "obj = MyClass()", "Use MyClass() to instantiate an object."),
                    ("Which method is called when an object is created?", ["__init__", "__new__", "__create__", "__start__"], "__init__", "__init__ is the constructor method."),
                    ("Which decorator is used for static methods?", ["@staticmethod", "@classmethod", "@property", "@static"], "@staticmethod", "@staticmethod defines a static method in a class."),
                    ("What is inheritance in Python?", ["A class can inherit from another class", "A function can inherit from another function", "A variable can inherit from another variable", "A module can inherit from another module"], "A class can inherit from another class", "Inheritance allows a class to inherit attributes and methods from another class."),
                    ("Which method is used to represent an object as a string?", ["__str__", "__repr__", "__string__", "__format__"], "__str__", "__str__ returns a string representation of the object."),
                    ("What is encapsulation in OOP?", ["Bundling data and methods that operate on that data", "Creating multiple objects", "Inheriting from multiple classes", "Creating abstract classes"], "Bundling data and methods that operate on that data", "Encapsulation bundles data and methods together in a class."),
                    ("Which keyword is used for method overriding?", ["No special keyword needed", "override", "overwrite", "redefine"], "No special keyword needed", "Python automatically overrides methods when you define them in a subclass."),
                    ("What is polymorphism in Python?", ["The ability to use different classes through a common interface", "Creating multiple objects", "Inheriting from multiple classes", "Creating abstract classes"], "The ability to use different classes through a common interface", "Polymorphism allows different classes to be used through a common interface.")
                ],
                # Add more mappings for other module types as needed
            },
            'java': {
                'control flow': [
                    ("Which keyword is used for a conditional statement in Java?", ["if", "when", "cond", "switch"], "if", "'if' is used for conditionals in Java."),
                    ("Which statement is used to exit a loop early in Java?", ["break", "stop", "exit", "return"], "break", "'break' exits a loop early in Java."),
                    ("What is the output of: for(int i=0;i<3;i++) System.out.print(i);?", ["012", "123", "0123", "01 2"], "012", "The loop prints 0, 1, 2."),
                    ("Which loop is best for iterating over an array?", ["for", "while", "do-while", "loop"], "for", "'for' is used to iterate over arrays in Java."),
                    ("Which keyword is used for an else-if condition in Java?", ["else if", "elif", "elseif", "elseif()"], "else if", "'else if' is the correct syntax in Java."),
                    ("What does the 'continue' statement do in a Java loop?", ["Skip to next iteration", "Exit the loop", "Skip the entire loop", "Restart the loop"], "Skip to next iteration", "'continue' skips the current iteration and continues with the next."),
                    ("Which loop executes at least once?", ["do-while", "while", "for", "foreach"], "do-while", "do-while loop executes the body at least once before checking the condition."),
                    ("What is the result of 5 / 2 in Java?", ["2", "2.5", "2.0", "3"], "2", "Integer division in Java truncates the decimal part."),
                    ("Which operator is used for logical AND in Java?", ["&&", "&", "and", "AND"], "&&", "&& is the logical AND operator in Java."),
                    ("What is the purpose of the 'switch' statement?", ["Execute different code based on a value", "Create a loop", "Define a method", "Create an object"], "Execute different code based on a value", "Switch statement executes different code blocks based on a variable's value.")
                ],
                'oop': [
                    ("Which keyword is used to define a class in Java?", ["class", "object", "struct", "type"], "class", "'class' is used to define classes in Java."),
                    ("What is the first parameter of instance methods in Java?", ["this", "self", "cls", "obj"], "this", "'this' refers to the instance in Java methods."),
                    ("How do you create an object from a class?", ["MyClass obj = new MyClass();", "obj = MyClass()", "MyClass.create()", "class MyClass()"], "MyClass obj = new MyClass();", "Use new MyClass() to instantiate an object in Java."),
                    ("Which method is called when an object is created?", ["constructor", "__init__", "init", "start"], "constructor", "The constructor is called when an object is created in Java."),
                    ("Which annotation is used for overriding methods?", ["@Override", "@Overload", "@Overriding", "@Method"], "@Override", "@Override is used to indicate a method override in Java."),
                    ("What is inheritance in Java?", ["A class can inherit from another class", "A method can inherit from another method", "A variable can inherit from another variable", "A package can inherit from another package"], "A class can inherit from another class", "Inheritance allows a class to inherit attributes and methods from another class."),
                    ("Which keyword is used to prevent inheritance?", ["final", "static", "private", "protected"], "final", "final keyword prevents a class from being inherited."),
                    ("What is encapsulation in Java?", ["Bundling data and methods that operate on that data", "Creating multiple objects", "Inheriting from multiple classes", "Creating abstract classes"], "Bundling data and methods that operate on that data", "Encapsulation bundles data and methods together in a class."),
                    ("Which access modifier allows access within the same package?", ["default", "public", "private", "protected"], "default", "Default access modifier allows access within the same package."),
                    ("What is polymorphism in Java?", ["The ability to use different classes through a common interface", "Creating multiple objects", "Inheriting from multiple classes", "Creating abstract classes"], "The ability to use different classes through a common interface", "Polymorphism allows different classes to be used through a common interface.")
                ],
                # Add more mappings for other module types as needed
            }
            # Add more languages as needed
        }

        lang_key = language.lower()
        # Try to match module type from title
        module_type = None
        for key in concept_map.get(lang_key, {}):
            if key in module_lower:
                module_type = key
                break
        # If no mapping, generate generic but language-specific questions
        questions = []
        if module_type:
            for q, opts, correct, expl in concept_map[lang_key][module_type]:
                opts_shuffled = opts[:]
                random.shuffle(opts_shuffled)
                correct_label = ['a)', 'b)', 'c)', 'd)'][opts_shuffled.index(correct)]
                labeled_options = [f"{label} {opt}" for label, opt in zip(['a)', 'b)', 'c)', 'd)'], opts_shuffled)]
                questions.append({
                    "question": q,
                    "options": labeled_options,
                    "correct_answer": correct_label,
                    "explanation": expl
                })
        else:
            # Fallback: generate language- and module-specific MCQs
            for i in range(10):
                q = f"In {language}, what is a key concept of {module_title}?"
                opts = [
                    f"A core concept in {module_title} for {language}",
                    f"A feature unrelated to {module_title}",
                    f"A hardware component",
                    f"A concept from another language"
                ]
                correct = opts[0]
                random.shuffle(opts)
                correct_label = ['a)', 'b)', 'c)', 'd)'][opts.index(correct)]
                labeled_options = [f"{label} {opt}" for label, opt in zip(['a)', 'b)', 'c)', 'd)'], opts)]
                questions.append({
                    "question": q,
                    "options": labeled_options,
                    "correct_answer": correct_label,
                    "explanation": f"{module_title} is a key concept in {language}."
                })
        return questions[:10]

    def extract_subsections(self, content_text):
        subsections = []
        # Look for learning objectives
        objectives_match = re.search(r'### Learning Objectives\n(.*?)(?=\n\n###|$)', content_text, re.DOTALL)
        if objectives_match:
            objectives_content = objectives_match.group(1).strip()
            objectives = [obj.strip() for obj in objectives_content.split('\n') if obj.strip().startswith('-')]
            for obj in objectives[:4]:  # Limit to 4 objectives
                subsections.append({
                    "title": obj.replace('-', '').strip(),
                    "content": f"Learning objective: {obj.replace('-', '').strip()}"
                })
        # Look for explanatory content sections
        explanatory_match = re.search(r'### Explanatory Content\n(.*?)(?=\n\n###|$)', content_text, re.DOTALL)
        if explanatory_match:
            explanatory_content = explanatory_match.group(1).strip()
            # Split by ** headings or treat as a single section
            if '**' in explanatory_content:
                sections = re.split(r'\*\*(.*?)\*\*', explanatory_content)
                for i in range(1, len(sections), 2):  # Skip first empty section, get every other section
                    if i + 1 < len(sections):
                        title = sections[i].strip()
                        content = sections[i + 1].strip()
                        if title and content:
                            subsections.append({
                                "title": title,
                                "content": content
                            })
            else:
                # If no bold headings, treat the entire content as one section
                subsections.append({
                    "title": "Explanatory Content",
                    "content": explanatory_content
                })
        # If no subsections found, create default ones
        if not subsections:
            subsections = [
                {
                    "title": "Concept Overview",
                    "content": "This module provides comprehensive coverage of the topic with practical examples and hands-on exercises."
                },
                {
                    "title": "Key Principles",
                    "content": "Learn the fundamental principles and best practices that will help you master this subject."
                }
            ]
        return subsections

    def get_unique_explanatory_content(self, language, module_title, module_number):
        """Return unique, module-specific explanatory content for Python and Rust modules 1-10."""
        if language == "Python":
            content_map = {
                1: (
                    "Python is renowned for its simplicity and readability, making it an ideal first language. Setting up your Python environment involves installing Python from the official website or using a package manager, and choosing an editor like VS Code or PyCharm. The interactive shell (REPL) allows for immediate feedback, which is invaluable for learning. Understanding the difference between Python 2 and 3, managing virtual environments, and using pip for package management are foundational skills. A well-configured environment accelerates learning and productivity, and is the first step toward professional development in Python."
                ),
                2: (
                    "Variables in Python are dynamically typed, meaning you don't declare their type explicitly. Python supports a rich set of data types: integers, floats, strings, booleans, lists, tuples, dictionaries, and sets. Operators allow you to manipulate these types—arithmetic for numbers, concatenation for strings, and logical operators for control flow. Understanding mutability, type conversion, and Python's approach to variable scope is crucial. These fundamentals underpin all Python programming, from simple scripts to complex systems."
                ),
                3: (
                    "Control flow in Python is managed with if, elif, and else statements for decision-making, and for and while loops for iteration. Indentation is syntactically significant, enforcing code clarity. Python's for loop is versatile, often used with range() or to iterate over collections. Loop control statements like break, continue, and else provide fine-grained control. Mastery of control flow enables you to write programs that respond dynamically to input and conditions, a core skill in all software development."
                ),
                4: (
                    "Functions in Python are defined with the def keyword and support default arguments, variable-length arguments, and keyword arguments. Functions promote code reuse and modularity. Scope rules (local, enclosing, global, built-in) determine variable visibility, and the nonlocal and global keywords allow you to modify variables outside the current scope. Understanding how to write, call, and organize functions is essential for building maintainable Python code and for collaborating in larger projects."
                ),
                5: (
                    "Python's built-in data structures—lists, tuples, and dictionaries—are powerful tools for organizing and manipulating data. Lists are mutable and ordered, tuples are immutable, and dictionaries store key-value pairs for fast lookups. List comprehensions and dictionary comprehensions provide concise ways to generate and transform collections. Choosing the right data structure for a task impacts performance and code clarity, and is a hallmark of effective Python programming."
                ),
                6: (
                    "Object-Oriented Programming (OOP) in Python enables you to model real-world entities using classes and objects. Python supports inheritance, polymorphism, and encapsulation. Special methods (like __init__, __str__, and __repr__) allow you to customize object behavior. Understanding how to design and use classes, manage instance and class variables, and leverage inheritance hierarchies is key to building scalable, reusable Python applications."
                ),
                7: (
                    "File I/O in Python is handled with the open() function and context managers (with statement) to ensure files are properly closed. You can read and write text and binary files, process CSV and JSON data, and handle file paths with the os and pathlib modules. Robust file handling includes error checking and exception management. Mastery of file I/O is essential for data processing, automation, and many real-world applications."
                ),
                8: (
                    "Exception handling in Python uses try, except, else, and finally blocks to manage errors gracefully. You can catch specific exceptions, raise custom exceptions, and use assertions for debugging. The built-in logging module aids in diagnosing issues. Effective debugging involves reading tracebacks, using breakpoints, and understanding common error types. These skills are vital for developing reliable, maintainable Python software."
                ),
                9: (
                    "Advanced Python features include decorators for modifying function behavior, generators for efficient iteration, and context managers for resource management. The standard library offers modules for everything from regular expressions to networking. Mastering these features allows you to write more efficient, elegant, and Pythonic code, and to leverage the full power of the language in professional settings."
                ),
                10: (
                    "Best practices in Python development include writing clean, readable code following PEP 8, using version control (git), testing with unittest or pytest, and documenting your code. Building projects—such as web apps with Flask or data analysis scripts with pandas—solidifies your skills. Understanding packaging, virtual environments, and deployment prepares you for real-world software engineering and collaboration."
                ),
            }
            return content_map.get(module_number, "This module covers advanced Python concepts relevant to modern development.")
        elif language == "Rust":
            content_map = {
                1: (
                    "Rust is a systems programming language focused on safety and performance. Setting up Rust involves installing rustup, the Rust toolchain, and using Cargo for project management. The compiler provides detailed error messages, which are a core part of the learning experience. The Rust community values clear, idiomatic code, and the official documentation is a key resource. A solid environment setup is the foundation for productive Rust development."
                ),
                2: (
                    "Rust's ownership model is its defining feature, ensuring memory safety without a garbage collector. Variables are immutable by default, but can be made mutable. Data types include integers, floats, booleans, characters, and compound types like tuples and arrays. Ownership, borrowing, and lifetimes prevent common bugs like dangling pointers. Mastering these concepts is essential for writing safe, efficient Rust code."
                ),
                3: (
                    "Control flow in Rust uses if, else, and match for branching, and loop, while, and for for iteration. Functions are defined with fn, and can return values using the -> syntax. Rust enforces explicitness, so all branches must return compatible types. Pattern matching with match is powerful for handling complex logic. Understanding control flow and function signatures is crucial for robust, predictable Rust programs."
                ),
                4: (
                    "Structs and enums are Rust's primary tools for creating custom data types. Structs group related data, while enums represent choices or variants. Pattern matching with match allows for expressive, safe handling of different cases. Methods are implemented with impl blocks. These features enable you to model complex domains and write code that is both safe and expressive."
                ),
                5: (
                    "Rust collections include vectors (Vec), strings, hash maps, and more. These types are designed for safety and performance, with ownership and borrowing rules enforced. Iterators and the Option and Result types provide powerful ways to process and handle data. Choosing the right collection and understanding its API is key to writing efficient, idiomatic Rust code."
                ),
                6: (
                    "Error handling in Rust is explicit and enforced by the type system. The Result and Option types are used instead of exceptions, making error cases impossible to ignore. Pattern matching and the ? operator simplify error propagation. This approach leads to more reliable code, as all possible outcomes must be considered. Mastery of error handling is essential for building robust Rust applications."
                ),
                7: (
                    "File I/O in Rust is performed using the std::fs and std::io modules. Reading and writing files requires handling Result types for error management. Async programming, enabled by the async/await syntax and crates like tokio, allows for scalable, non-blocking I/O. Understanding file permissions, buffering, and error handling is crucial for building efficient, reliable Rust applications that interact with the filesystem."
                ),
                8: (
                    "Traits and generics are Rust's tools for abstraction and code reuse. Traits define shared behavior, while generics allow for type-agnostic code. Implementing traits enables polymorphism, and lifetimes ensure references are valid. These features are central to Rust's type system, enabling powerful, flexible APIs without sacrificing safety or performance."
                ),
                9: (
                    "Rust guarantees memory safety through strict compile-time checks. Concurrency is achieved with threads, channels, and the Send and Sync traits, allowing safe parallelism. Smart pointers (Box, Rc, Arc) manage heap allocation and shared ownership. Understanding these concepts is vital for writing high-performance, concurrent Rust programs that avoid data races and undefined behavior."
                ),
                10: (
                    "Best practices in Rust include writing idiomatic code, using cargo for project management, and leveraging the rich ecosystem of crates. Testing is built-in with cargo test, and documentation is generated with cargo doc. Building real projects—such as command-line tools or web servers—solidifies your understanding and prepares you for professional Rust development."
                ),
            }
            return content_map.get(module_number, f"This module covers advanced {language} concepts.")
        else:
            return f"This module explores {module_title} in {language}, covering key syntax, common patterns, and best practices. You will learn how to effectively use this feature in your {language} projects."


class ValidateVideoView(APIView):
    def post(self, request):
        video_url = request.data.get('url')
        if not video_url:
            return Response({"error": "Video URL is required"}, status=400)
        
        try:
            # Extract video ID from YouTube URL
            video_id_match = re.search(r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)', video_url)
            if not video_id_match:
                return Response({"valid": False, "error": "Invalid YouTube URL format"}, status=200)
            
            video_id = video_id_match.group(1)
            
            # Check if video exists using YouTube Data API (optional)
            # For now, we'll just validate the URL format
            return Response({
                "valid": True,
                "video_id": video_id,
                "embed_url": f"https://www.youtube.com/embed/{video_id}"
            }, status=200)
            
        except Exception as e:
            return Response({"valid": False, "error": str(e)}, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class CodeExecutionView(APIView):
    def post(self, request):
        code = request.data.get('code')
        topic = request.data.get('topic') # New: Get topic from request
        
        print(f"[CodeExecutionView] Incoming request: code={code}, topic={topic}")
        
        if not code:
            print("[CodeExecutionView] Error: Code is required")
            return Response({"error": "Code is required"}, status=400)
        
        if not topic:
            print("[CodeExecutionView] Error: Topic is required for language classification")
            return Response({"error": "Topic is required"}, status=400)

        # Classify the topic to determine the language for execution
        try:
            classification = TopicClassifier.classify(topic)
            language = classification["language"] # This is the "syntax highlighting" language
            execution_enabled = classification["execution_enabled"]
            topic_type = classification["type"]
            
            print(f"[CodeExecutionView] Topic Classified: {classification}")

            if not execution_enabled:
                return Response({"error": f"Code execution is not enabled for topic type: {topic_type}"}, status=400)

        except Exception as e:
            print(f"[CodeExecutionView] Error classifying topic: {str(e)}")
            return Response({"error": "Error classifying topic", "details": str(e)}, status=500)
        
        try:
            # --- Judge0 API via RapidAPI ---
            print('RAPIDAPI_KEY from env:', os.getenv('RAPIDAPI_KEY'))
            RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
            RAPIDAPI_HOST = "judge0-ce.p.rapidapi.com"
            if not RAPIDAPI_KEY:
                return Response({"error": "Judge0 RapidAPI key not configured on server"}, status=500)

            # Map language to Judge0 language_id using Registry and Topic
            # Determine effective language from registry based on the topic classification result
            # Ideally 'language' variable holds the normalized language key (e.g. 'python', 'rust')
            language_id = LanguageRegistry.get_language_id(language)
            
            if not language_id:
                # Try to fuzzy match if exact match failed
                if not language_id:
                    # Very simple fuzzy match fallback specific for this view if needed
                    # But ideally frontend sends correct key
                    pass
                
            if not language_id:
                return Response({"error": f"Unsupported language: {language}"}, status=400)

            stdin = request.data.get('stdin', '')
            judge0_payload = {
                "language_id": language_id,
                "source_code": code,
                "stdin": stdin or ""
            }

            try:
                judge0_res = requests.post(
                    f"https://{RAPIDAPI_HOST}/submissions?base64_encoded=false&wait=true",
                    headers={
                        "content-type": "application/json",
                        "X-RapidAPI-Key": RAPIDAPI_KEY,
                        "X-RapidAPI-Host": RAPIDAPI_HOST
                    },
                    json=judge0_payload
                )
                print(f"[CodeExecutionView] Judge0 status: {judge0_res.status_code}, response: {judge0_res.text}")
                if judge0_res.status_code != 200:
                    return Response({"error": "Judge0 error", "details": judge0_res.text}, status=judge0_res.status_code)
                data = judge0_res.json()
                # Compose output
                output = {
                    "stdout": data.get("stdout", ""),
                    "stderr": data.get("stderr", ""),
                    "compile_output": data.get("compile_output", ""),
                    "status": data.get("status", {}),
                    "time": data.get("time"),
                    "memory": data.get("memory")
                }
                return Response(output, status=200)
            except Exception as e:
                print(f"[CodeExecutionView] Judge0 exception: {str(e)}")
                return Response({"error": "Error connecting to Judge0", "details": str(e)}, status=500)

        except Exception as e:
            print(f"[CodeExecutionView] Exception: {str(e)}")
            return Response({"error": "Error executing code", "details": str(e)}, status=500)


class QuizView(APIView):
    def get(self, request, module_id):
        try:
            module = Module.objects.get(id=module_id)
            quizzes = module.quizzes.all()
            
            quiz_data = []
            for quiz in quizzes:
                quiz_data.append({
                    'id': quiz.id,
                    'question': quiz.question,
                    'options': quiz.options,
                    'question_type': quiz.question_type
                })
            
            return Response({
                'module_name': module.name,
                'module_description': module.description,
                'questions': quiz_data
            }, status=200)
            
        except Module.DoesNotExist:
            return Response({"error": "Module not found"}, status=404)
        except Exception as e:
            return Response({"error": "Error fetching quiz", "details": str(e)}, status=500)


class SubmitQuizView(APIView):
    def post(self, request, module_id):
        try:
            module = Module.objects.get(id=module_id)
            user_answers = request.data.get('answers', {})
            
            quizzes = module.quizzes.all()
            total_questions = len(quizzes)
            correct_answers = 0
            
            results = []
            for quiz in quizzes:
                user_answer = user_answers.get(str(quiz.id))
                is_correct = user_answer == quiz.correct_answer
                
                if is_correct:
                    correct_answers += 1
                
                results.append({
                    'question_id': quiz.id,
                    'question': quiz.question,
                    'user_answer': user_answer,
                    'correct_answer': quiz.correct_answer,
                    'is_correct': is_correct,
                    'explanation': quiz.explanation
                })
            
            score_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
            
            return Response({
                'module_id': module_id,
                'total_questions': total_questions,
                'correct_answers': correct_answers,
                'score_percentage': score_percentage,
                'results': results
            }, status=200)
            
        except Module.DoesNotExist:
            return Response({"error": "Module not found"}, status=404)
        except Exception as e:
            return Response({"error": "Error submitting quiz", "details": str(e)}, status=500)

# -------------------------------------------------------------------------
# MENTAI PLATFORM API (Auth, Dashboard, Progress)
# -------------------------------------------------------------------------

class AuthSyncView(APIView):
    """
    Syncs user from Frontend (NextAuth) to Backend Django User.
    Creates user if not exists based on email.
    """
    def post(self, request):
        email = request.data.get("email")
        name = request.data.get("name", "")
        
        if not email:
            return Response({"error": "Email required"}, status=400)
            
        # Find or Create User
        user, created = User.objects.get_or_create(username=email, defaults={"email": email, "first_name": name})
        
        return Response({
            "status": "synced",
            "user_id": user.id,
            "is_new": created
        }, status=200)

class DashboardView(APIView):
    """
    Returns the user's learning dashboard (active courses, progress).
    """
    def get(self, request):
        email = request.query_params.get("email")
        if not email:
            return Response({"error": "Email required"}, status=400)
            
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"courses": []}, status=200) # Guest or new user
            
        from .models import UserProgress
        progress_records = UserProgress.objects.filter(user=user)
        
        dashboard_data = []
        for p in progress_records:
            total_modules = 10 # Standardized now
            completed_count = len(p.completed_modules)
            percent = int((completed_count / total_modules) * 100)
            
            dashboard_data.append({
                "topic_slug": p.topic_slug,
                "display_title": p.display_title,
                "current_module": p.current_module_id,
                "completed_count": completed_count,
                "percent_complete": percent,
                "last_visited": p.last_visited_at
            })
            
        return Response({"courses": dashboard_data}, status=200)

class UpdateProgressView(APIView):
    """
    Updates progress for a specific module/topic.
    """
    def post(self, request):
        from .models import UserProgress
        
        email = request.data.get("email")
        topic_slug = request.data.get("topic_slug")
        module_id = request.data.get("module_id")
        quiz_score = request.data.get("quiz_score") # Optional
        
        if not email or not topic_slug:
            return Response({"error": "Missing data"}, status=400)
            
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
            
        # Get canonical title (optional, but good for display)
        display_title = request.data.get("display_title", topic_slug.title())
        
        progress, created = UserProgress.objects.get_or_create(
            user=user, 
            topic_slug=topic_slug,
            defaults={"display_title": display_title}
        )
        
        # Update fields
        if module_id:
            progress.current_module_id = module_id
            
        is_completed = request.data.get("is_completed", False)
        if is_completed and module_id:
            if module_id not in progress.completed_modules:
                progress.completed_modules.append(module_id)
                
        if quiz_score is not None and module_id:
            progress.quiz_scores[str(module_id)] = quiz_score
            
        progress.last_visited_at = datetime.now()
        progress.save()
        
        return Response({"status": "updated"}, status=200)
