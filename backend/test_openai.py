import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.ai_orchestrator import AIOrchestrator
from dotenv import load_dotenv

load_dotenv()
print("OpenAI Key exists:", os.getenv("OPENAI_API_KEY") is not None)

orch = AIOrchestrator()
print("Has OpenAI Client:", orch.openai_client is not None)

print("Testing _call_openai directly:")
res = orch._call_openai("Hello")
print("OpenAI Result:", res)
