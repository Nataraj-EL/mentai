import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load env
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("No API Key")
    exit(1)

genai.configure(api_key=api_key)

models = ['gemini-1.5-flash', 'gemini-pro', 'gemini-1.0-pro']
for m in models:
    print(f"Testing {m}...")
    try:
        model = genai.GenerativeModel(m)
        r = model.generate_content("Hello")
        print(f"Success: {r.text}")
    except Exception as e:
        print(f"Failed: {e}")
