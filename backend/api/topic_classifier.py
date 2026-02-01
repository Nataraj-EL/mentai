import re
import difflib

class TopicClassifier:
    """
    Classifies a user topic using exact and fuzzy matching.
    Standardizes output for platform consistency.
    """

    # 1. Aliases: Map variations to canonical keys
    # These are handled before fuzzy matching to catch common abbreviations
    ALIASES = {
        "py": "python", "python3": "python",
        "js": "javascript", "node": "javascript", "nodejs": "javascript",
        "ts": "typescript",
        "cpp": "c++",
        "rs": "rust",
        "sol": "solidity",
        "reactjs": "react", "nextjs": "next.js", "next": "next.js",
        "csharp": "c#",
        "golang": "go"
    }

    # 2. Canonical Registry
    # Key = Canonical Slug (lowercase)
    # Value = (Type, Language for Code, Execution Enabled, Display Title)
    # Types: EXECUTABLE, FRAMEWORK, THEORY, MARKUP
    
    REGISTRY = {
        # Executable
        "python":     ("EXECUTABLE", "python", True, "Python Programming"),
        "java":       ("EXECUTABLE", "java", True, "Java Programming"),
        "c++":        ("EXECUTABLE", "cpp", True, "C++ Programming"),
        "javascript": ("EXECUTABLE", "javascript", True, "Modern JavaScript"),
        "rust":       ("EXECUTABLE", "rust", True, "Rust Systems Programming"),
        "go":         ("EXECUTABLE", "go", True, "Go (Golang)"),
        "c":          ("EXECUTABLE", "c", True, "C Programming"),
        # Frameworks (Non-Exec for now)
        "react":      ("FRAMEWORK", "javascript", False, "React Development"), # Syntax: JS
        "next.js":    ("FRAMEWORK", "javascript", False, "Next.js Framework"),
        "vue":        ("FRAMEWORK", "javascript", False, "Vue.js"),
        "angular":    ("FRAMEWORK", "javascript", False, "Angular"),
        "django":     ("FRAMEWORK", "python", False, "Django Web Framework"),
        "flask":      ("FRAMEWORK", "python", False, "Flask Web Development"),
        "spring":     ("FRAMEWORK", "java", False, "Spring Boot"),
        "express":    ("FRAMEWORK", "javascript", False, "Express.js"),
        # Non-Executable / Theory / Markup
        "html":       ("MARKUP", "html", False, "HTML5"),
        "css":        ("MARKUP", "css", False, "CSS3"),
        "sql":        ("THEORY", "general", False, "SQL Database Design"),
        "mongodb":    ("THEORY", "general", False, "MongoDB Fundamentals"),
        "solidity":   ("THEORY", "general", False, "Solidity & Smart Contracts"),
        
        # Newly Enabled Executables
        "ruby":       ("EXECUTABLE", "ruby", True, "Ruby Programming"),
        "c#":         ("EXECUTABLE", "csharp", True, "C# Development"),
        "swift":      ("EXECUTABLE", "swift", True, "Swift iOS Development"),
        "kotlin":     ("EXECUTABLE", "kotlin", True, "Kotlin Android Development"),
        "php":        ("EXECUTABLE", "php", True, "PHP Web Development"),
        "dart":       ("THEORY", "general", False, "Dart & Flutter")
    }

    @staticmethod
    def classify(topic_input):
        cleaned = topic_input.lower().strip()
        
        # 1. Alias Resolution
        if cleaned in TopicClassifier.ALIASES:
            cleaned = TopicClassifier.ALIASES[cleaned]
            
        # 2. Exact Match
        if cleaned in TopicClassifier.REGISTRY:
            return TopicClassifier._format_result(cleaned)
            
        # 3. Fuzzy Match
        # Get close matches with cutoff=0.6 (allows for 'pythin', 'javascrip', etc)
        matches = difflib.get_close_matches(cleaned, TopicClassifier.REGISTRY.keys(), n=1, cutoff=0.6)
        
        if matches:
            best_match = matches[0]
            # Log correction? (In a real app, yes)
            return TopicClassifier._format_result(best_match, was_corrected=True)
            
        # 4. Fallback (Unknown)
        return {
            "type": "THEORY",
            "language": "general", 
            "execution_enabled": False,
            "display_title": f"Introduction to {topic_input.title()}", # Fallback title
            "canonical_slug": "general",
            "is_correction": False
        }

    @staticmethod
    def _format_result(key, was_corrected=False):
        data = TopicClassifier.REGISTRY[key]
        return {
            "type": data[0],
            "language": data[1],
            "execution_enabled": data[2],
            "display_title": data[3],
            "canonical_slug": key,
            "is_correction": was_corrected
        }
