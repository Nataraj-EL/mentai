import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.ai_orchestrator import AIOrchestrator
import json

orch = AIOrchestrator()
prompt = """
Generate exactly 10 quiz questions for Module 1: "Introduction to HTML" of "HTML5" (html).
Return ONLY a JSON object containing an array field "quizzes":
{
    "quizzes": [
        {
            "question": "Question text?",
            "options": ["Op A", "Op B", "Op C", "Op D"],
            "answer": "Op A",
            "explanation": "Why this is correct...",
            "difficulty": "easy/medium/hard",
            "type": "code_prediction"
        }
    ]
}
Focus on deep reasoning.
"""
print("Testing _call_groq directly for Quizzes:")
res = orch._call_groq(prompt)
print("Groq Raw Result:\n", res)
parsed = orch._safe_parse_json(res, {"quizzes": []})
print("\nParsed Result:\n", json.dumps(parsed, indent=2))
