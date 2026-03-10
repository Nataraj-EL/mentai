import os
import json
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.ai_orchestrator import AIOrchestrator
from dotenv import load_dotenv

load_dotenv()

orchestrator = AIOrchestrator()
module_content = orchestrator.generate_complete_module("HTML5", "html", "Introduction to HTML", 1)

print("--- THEORY ---")
print("Length:", len(module_content.get("theory", "")))

print("\n--- MINI LABS ---")
print(json.dumps(module_content.get("mini_labs", []), indent=2))

print("\n--- QUIZZES ---")
print(json.dumps(module_content.get("quizzes", []), indent=2))

# Also test generate_quizzes specifically
print("\n--- GENERATE QUIZZES SPECIFICALLY ---")
quiz_output = orchestrator.generate_quizzes("HTML5", "html", "Introduction to HTML", 1)
print(json.dumps(quiz_output, indent=2))
