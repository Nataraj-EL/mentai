class LanguageRegistry:
    """
    Centralized registry for supported programming languages and their metadata.
    """
    SUPPORTED_LANGUAGES = {
        "python": {
            "name": "Python",
            "judge0_id": 71,  # Python 3.8.1 (Judge0 CE)
            "monaco_id": "python",
            "aliases": ["py", "python3"],
            "extension": "py"
        },
        "rust": {
            "name": "Rust",
            "judge0_id": 73,  # Rust 1.40.0 (Judge0 CE)
            "monaco_id": "rust",
            "aliases": ["rs"],
            "extension": "rs"
        },
        "javascript": {
            "name": "JavaScript",
            "judge0_id": 63,  # JavaScript (Node.js 12.14.0)
            "monaco_id": "javascript",
            "aliases": ["js", "node", "nodejs"],
            "extension": "js"
        },
        "java": {
            "name": "Java",
            "judge0_id": 62,  # Java (OpenJDK 13.0.1)
            "monaco_id": "java",
            "aliases": [],
            "extension": "java"
        },
        "cpp": {
            "name": "C++",
            "judge0_id": 54,  # C++ (GCC 9.2.0)
            "monaco_id": "cpp",
            "aliases": ["cplusplus", "c++"],
            "extension": "cpp"
        },
        "c": {
            "name": "C",
            "judge0_id": 50,  # C (GCC 9.2.0)
            "monaco_id": "c",
            "aliases": ["clang"],
            "extension": "c"
        },
        "go": {
            "name": "Go",
            "judge0_id": 60,  # Go (1.13.5)
            "monaco_id": "go",
            "aliases": ["golang"],
            "extension": "go"
        },
        "typescript": {
            "name": "TypeScript",
            "judge0_id": 74,  # TypeScript (3.7.4)
            "monaco_id": "typescript",
            "aliases": ["ts"],
            "extension": "ts"
        },
        "solidity": {
            "name": "Solidity",
            "judge0_id": None,  # Not supported natively by Judge0 CE usually, mostly FE only or specialized
            "monaco_id": "sol",
            "aliases": ["sol"],
            "extension": "sol"
        }
    }

    @classmethod
    def get_language_id(cls, language_name):
        """Get Judge0 ID for a given language."""
        lang_data = cls.get_language_metadata(language_name)
        return lang_data.get("judge0_id") if lang_data else None

    @classmethod
    def get_monaco_id(cls, language_name):
        """Get Monaco Editor ID for a given language."""
        lang_data = cls.get_language_metadata(language_name)
        return lang_data.get("monaco_id") if lang_data else "plaintext"

    @classmethod
    def get_language_metadata(cls, language_name):
        """
        Normalize language name and return metadata.
        Handles case-insensitivity and aliases.
        """
        if not language_name:
            return None
            
        normalized = language_name.lower().strip()
        
        # Direct match
        if normalized in cls.SUPPORTED_LANGUAGES:
            return cls.SUPPORTED_LANGUAGES[normalized]
            
        # Alias match
        for key, data in cls.SUPPORTED_LANGUAGES.items():
            if normalized in data["aliases"]:
                return data
                
        return None
        
    @classmethod
    def is_supported(cls, language_name):
        return cls.get_language_metadata(language_name) is not None
