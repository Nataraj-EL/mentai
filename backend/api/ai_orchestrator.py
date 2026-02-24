import os
import json
import logging
import concurrent.futures
from json_repair import repair_json
import google.generativeai as genai
from groq import Groq

logger = logging.getLogger(__name__)

class AIOrchestrator:
    """
    Hybrid Multi-LLM Orchestrator
    - Structure generation -> Gemini (fast, free)
    - Quiz generation -> OpenAI (or Gemini Flash fallback)
    - Lab generation -> Groq (Llama-3 fast code generation, or Gemini Fallback)
    - Theory generation -> Gemini
    """
    def __init__(self):
        # Gemini Init
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest')
        else:
            self.gemini_model = None

        # Groq Init
        self.groq_key = os.getenv("GROQ_API_KEY")
        if self.groq_key:
            self.groq_client = Groq(api_key=self.groq_key)
        else:
            self.groq_client = None

        # OpenAI Init (Optional)
        self.openai_key = os.getenv("OPENAI_API_KEY")
        if self.openai_key:
            from openai import OpenAI
            self.openai_client = OpenAI(api_key=self.openai_key)
        else:
            self.openai_client = None

    def _safe_parse_json(self, raw_text, default_val=None):
        if not raw_text:
            return default_val
        try:
            # json_repair robustly handles markdown wrapper, trailing commas, missing quotes, etc.
            repaired = repair_json(raw_text, return_objects=True)
            return repaired if repaired else default_val
        except Exception as e:
            logger.error(f"Failed to parse repaired JSON: {str(e)}\nRaw: {raw_text}")
            return default_val

    def generate_course_structure(self, topic, language, level="Beginner"):
        """Structure Phase matches Gemini."""
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
        Ensure there are exactly 10 modules. Do not include the phrase 'Master this concept.' Return ONLY raw JSON.
        """
        raw_output = self._call_gemini(prompt)
        return self._safe_parse_json(raw_output, {})

    def generate_theory(self, topic, language, module_title, module_number):
        prompt = f"""
        Generate detailed theoretical content for Module {module_number}: "{module_title}" of the course "{topic}" ({language}).
        Return ONLY a JSON object:
        {{
            "content": "Detailed markdown formatted explanatory text...",
            "real_world_examples": [
                {{
                    "title": "Use Case",
                    "description": "...",
                    "solution": "...",
                    "learning_outcome": "..."
                }}
            ]
        }}
        """
        raw_output = self._call_gemini(prompt)
        return self._safe_parse_json(raw_output, {"content": f"Theory for {module_title}", "real_world_examples": []})

    def generate_quizzes(self, topic, language, module_title, module_number):
        prompt = f"""
        Generate exactly 10 quiz questions for Module {module_number}: "{module_title}" of "{topic}" ({language}).
        Return ONLY a JSON object containing an array field "quizzes":
        {{
            "quizzes": [
                {{
                    "question": "Question text?",
                    "options": ["Op A", "Op B", "Op C", "Op D"],
                    "answer": "Op A",
                    "explanation": "Why this is correct...",
                    "difficulty": "easy/medium/hard",
                    "type": "code_prediction"
                }}
            ]
        }}
        Focus on deep reasoning.
        """
        raw_output = None
        if self.openai_client:
            raw_output = self._call_openai(prompt)
        if not raw_output:
            raw_output = self._call_gemini(prompt)
            
        return self._safe_parse_json(raw_output, {"quizzes": []})

    def generate_labs(self, topic, language, module_title, module_number):
        prompt = f"""
        Generate coding labs and examples for Module {module_number}: "{module_title}" of "{topic}" ({language}).
        Return ONLY a JSON object:
        {{
            "code_examples": [
                {{
                    "title": "Example Title",
                    "code": "code snippet...",
                    "explanation": "Explanation...",
                    "language": "{language}"
                }}
            ],
            "mini_labs": [
                 {{
                    "title": "Lab Title",
                    "description": "Instructions...",
                    "tasks": ["Task 1", "Task 2"],
                    "expected_outcome": "Outcome"
                 }}
            ]
        }}
        Ensure high quality compilable {language} code.
        """
        raw_output = None
        if self.groq_client:
            raw_output = self._call_groq(prompt)
        if not raw_output:
            raw_output = self._call_gemini(prompt)
        
        return self._safe_parse_json(raw_output, {"code_examples": [], "mini_labs": []})

    def generate_complete_module(self, topic, language, module_title, module_number):
        """Orchestrates parallel provider calls."""
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_theory = executor.submit(self.generate_theory, topic, language, module_title, module_number)
            future_quizzes = executor.submit(self.generate_quizzes, topic, language, module_title, module_number)
            future_labs = executor.submit(self.generate_labs, topic, language, module_title, module_number)

            theory_data = future_theory.result()
            quizzes_data = future_quizzes.result()
            labs_data = future_labs.result()

        # Merge results into a unified module dict
        combined = {}
        combined.update(theory_data if theory_data else {})
        combined.update(quizzes_data if quizzes_data else {})
        combined.update(labs_data if labs_data else {})
        return combined

    # -- Internal Callers with Retry/Failover --

    def _call_gemini(self, prompt, retries=2):
        if not self.gemini_model:
            return None
        import time
        for attempt in range(retries):
            try:
                response = self.gemini_model.generate_content(prompt)
                return response.text
            except Exception as e:
                logger.warning(f"Gemini attempt {attempt+1} failed: {e}")
                time.sleep(1)
        return None

    def _call_groq(self, prompt, retries=2):
        if not self.groq_client:
            return None
        import time
        for attempt in range(retries):
            try:
                chat_completion = self.groq_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You output only valid raw JSON. No markdown wrappers. No chat preamble."},
                        {"role": "user", "content": prompt}
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0.2,
                )
                return chat_completion.choices[0].message.content
            except Exception as e:
                logger.warning(f"Groq attempt {attempt+1} failed: {e}")
                time.sleep(1)
        return None
        
    def _call_openai(self, prompt, retries=2):
        if not self.openai_client:
            return None
        import time
        for attempt in range(retries):
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    response_format={ "type": "json_object" },
                    messages=[
                        {"role": "system", "content": "You are a JSON generating system. Output JSON only."},
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.warning(f"OpenAI attempt {attempt+1} failed: {e}")
                time.sleep(1)
        return None
