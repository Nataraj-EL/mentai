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
            self.gemini_model = genai.GenerativeModel('gemini-flash-latest')
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

    def generate_all_theory(self, topic, language, modules_list):
        module_titles = [f"Module {m['module_number']}: {m['title']}" for m in modules_list]
        prompt = f"""
        Generate detailed theoretical content for the following modules of the course "{topic}" ({language}):
        {module_titles}
        
        Return ONLY a complete JSON object mapping module numbers (as strings) to their theory content:
        {{
            "1": {{
                "content": "Detailed markdown formatted explanatory text...",
                "real_world_examples": [
                    {{"title": "...", "description": "...", "solution": "...", "learning_outcome": "..."}}
                ]
            }},
            "2": {{ ... }}
        }}
        """
        raw_output = self._call_gemini(prompt, retries=3)
        return self._safe_parse_json(raw_output, {})

    def generate_all_quizzes(self, topic, language, modules_list):
        module_titles = [f"Module {m['module_number']}: {m['title']}" for m in modules_list]
        prompt = f"""
        Generate exactly 5 rigorous quiz questions for EVERY module in the course "{topic}" ({language}). 
        Modules: {module_titles}
        
        Return ONLY a JSON object mapping module numbers (as strings) to their quizzes:
        {{
            "1": {{
                "quizzes": [
                    {{"question": "?", "options": ["A", "B", "C", "D"], "answer": "A", "explanation": "...", "difficulty": "hard", "type": "multiple_choice"}}
                ]
            }},
            "2": {{ ... }}
        }}
        """
        # Prioritize Groq for speed and rate limits, fallback to Gemini
        raw_output = None
        if self.groq_client:
            raw_output = self._call_groq(prompt, retries=2)
        if not raw_output:
            raw_output = self._call_gemini(prompt, retries=2)
        return self._safe_parse_json(raw_output, {})

    def generate_all_labs(self, topic, language, modules_list):
        module_titles = [f"Module {m['module_number']}: {m['title']}" for m in modules_list]
        prompt = f"""
        Generate practical coding labs and real-world script examples for EVERY module in "{topic}" ({language}).
        Modules: {module_titles}
        
        Return ONLY a JSON object mapping module numbers (as strings) to their labs:
        {{
            "1": {{
                "code_examples": [
                    {{"title": "...", "code": "...", "explanation": "...", "language": "{language}"}}
                ],
                "mini_labs": [
                    {{"title": "...", "description": "...", "tasks": ["..."], "expected_outcome": "..."}}
                ]
            }},
            "2": {{ ... }}
        }}
        Output raw JSON only. Do not wrap in markdown blocks.
        """
        # Groq Llama-3 is excellent for code generation
        raw_output = None
        if self.groq_client:
            raw_output = self._call_groq(prompt, retries=2)
        if not raw_output:
            raw_output = self._call_gemini(prompt, retries=2)
        return self._safe_parse_json(raw_output, {})

    def generate_course_content_batched(self, topic, language, course_outline):
        """Orchestrates parallel provider calls for ALL modules at once."""
        modules_list = course_outline.get("modules", [])
        if not modules_list:
            return {}

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_theory = executor.submit(self.generate_all_theory, topic, language, modules_list)
            future_quizzes = executor.submit(self.generate_all_quizzes, topic, language, modules_list)
            future_labs = executor.submit(self.generate_all_labs, topic, language, modules_list)

            theory_data = future_theory.result() or {}
            quizzes_data = future_quizzes.result() or {}
            labs_data = future_labs.result() or {}

        # Merge results into a unified module mapping
        combined_modules = {}
        for mod in modules_list:
            mod_id = str(mod.get("module_number"))
            combined_modules[mod_id] = {}
            combined_modules[mod_id].update(theory_data.get(mod_id, {}))
            combined_modules[mod_id].update(quizzes_data.get(mod_id, {}))
            combined_modules[mod_id].update(labs_data.get(mod_id, {}))
            
        return combined_modules

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
