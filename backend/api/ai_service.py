from google import genai
import os
import json
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables.")
            self.client = None
        else:
            self.client = genai.Client(api_key=self.api_key, http_options={'api_version': 'v1'})
            self.model_name = 'gemini-1.5-flash'
            import importlib.metadata
            try:
                ver = importlib.metadata.version("google-genai")
                logger.info(f"Initialized GeminiService with google-genai version: {ver}")
            except:
                logger.info("Initialized GeminiService with unknown google-genai version")

    def generate_course_structure(self, topic, language, level="Beginner"):
        """
        Generates a structured course outline with 10 modules using Gemini.
        Returns a JSON object with the course structure.
        """
        if not self.client:
            return None

        prompt = f"""
        Create a comprehensive 10-module course on "{topic}" using {language}.
        Target Audience: {level}
        
        The output must be a valid JSON object with the following structure:
        {{
            "course_title": "Title of the course",
            "course_description": "Brief description",
            "modules": [
                {{
                    "module_number": 1,
                    "title": "Module Title",
                    "description": "Module Description",
                    "learning_objectives": ["Objective 1", "Objective 2"],
                    "difficulty": "Beginner/Intermediate/Advanced"
                }}
            ]
        }}
        Ensure there are exactly 10 modules.
        IMPORTANT: Do not include the phrase 'Master this concept.' in any descriptions or content.
        IMPORTANT: Return ONLY the JSON object. Do not wrap it in markdown block quotes.
        """
        
        return self._generate_json(prompt)

    def generate_module_content(self, topic, language, module_title, module_number):
        """
        Generates detailed content for a specific module using Gemini.
        Returns a JSON object with the module content.
        """
        if not self.client:
            return None

        # SAFETY CHECK: If topic is unknown/general, do NOT generate python code.
        if language == "general":
            return {
                "content": f"We are currently building structured content for '{topic}'. Full interactive modules, labs, and quizzes will be available soon.",
                "code_examples": [],
                "mini_labs": [],
                "quizzes": [],
                "real_world_examples": [],
                "learning_outcome": "Stay tuned for updates."
            }

        prompt = f"""
        Generate detailed course content for Module {module_number}: "{module_title}" of the course "{topic}" ({language}).
        
        The output must be a valid JSON object with the following structure:
        {{
            "content": "Detailed explanatory text for the module...",
            "code_examples": [
                {{
                    "title": "Example Title",
                    "code": "code snippet...",
                    "explanation": "Explanation of the code code...",
                    "language": "{language}"
                }}
            ],
            "mini_labs": [
                 {{
                    "title": "Lab Title",
                    "description": "Lab instructions...",
                    "tasks": ["Task 1", "Task 2"],
                    "expected_outcome": "Outcome description"
                 }}
            ],
            "quizzes": [
                {{
                    "question": "Question text?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "Option A",
                    "explanation": "Why this is correct...",
                    "difficulty": "easy/medium/hard",
                    "type": "code_prediction/reasoning/debugging/syntax/real_world"
                }}
            ],
             "real_world_examples": [
                {{
                    "title": "Real World Use Case",
                    "description": "Description...",
                    "solution": "How it solves a problem...",
                    "learning_outcome": "What is learned..."
                }}
             ]
        }}
        
        CRITICAL QUIZ GENERATION RULES:
        1. Generate EXACTLY 10 quiz questions.
        2. Follow this STRICT distribution:
           - 3 Output prediction (code-based)
           - 2 Conceptual reasoning (with code)
           - 2 Debugging / error identification
           - 2 Syntax & best-practice evaluation
           - 1 Real-world scenario / use-case
        3. Difficulty Distribution: 3 Easy, 4 Medium, 3 Hard.
        4. Ensure all code snippets are valid {language} and relevant to the module.
        5. Provide AT LEAST 2 code examples and 1 mini lab.
        IMPORTANT: Do not include the phrase 'Master this concept.' in any descriptions or content.
        IMPORTANT: Return ONLY the JSON object. Do not wrap it in markdown block quotes.
        IMPORTANT: Return ONLY the JSON object. Do not wrap it in markdown block quotes.
        """
        
        return self._generate_json(prompt)

    def ask_mentai(self, query):
        """
        Custom chat assistant method for MentAI.
        """
        if not self.client:
            return None

        prompt = f"""
        You are MentAI, an expert AI learning assistant.
        The user is asking: "{query}"
        
        Provide a concise, helpful, and encouraging response.
        If the user asks for code, provide clean, well-commented code snippets.
        Focus on being a 'learning buddy' rather than just a search engine.
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text if response and hasattr(response, 'text') else None
        except Exception as e:
            logger.error(f"MentAI chat error: {str(e)}")
            return None

    def _generate_json(self, prompt):
        """
        Helper method to generate content and parse JSON.
        """
        if not self.client:
            return None

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            # Simple validation to ensure it didn't return Markdown code blocks wrapping the JSON
            # New SDK usually returns cleaned text if MIME type is set, but extra safety:
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            elif text.startswith("```"):
                 text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
                
            return json.loads(text)
        except Exception as e:
            logger.error(f"Gemini generation error: {str(e)}")
            return None
