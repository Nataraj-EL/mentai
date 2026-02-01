import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: NO API KEY FOUND")
    exit(1)

print(f"Using Key: ...{api_key[-4:]}")

# Configure SDK
genai.configure(api_key=api_key)

print("\n--- TEST 1: LIST MODELS ---")
try:
    count = 0
    for m in genai.list_models():
        print(f"Found: {m.name}")
        if 'generateContent' in m.supported_generation_methods:
             print(f"  -> Supports Generation")
        count += 1
    if count == 0:
        print("RESULT: No models found. (API likely disabled or restricted)")
    else:
        print(f"RESULT: Found {count} models.")
except Exception as e:
    print(f"RESULT: List Models Failed with error: {e}")

print("\n--- TEST 2: GENERATE CONTENT (gemini-1.5-flash) ---")
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    res = model.generate_content("Ping")
    print(f"RESULT: Success! Response: {res.text}")
except Exception as e:
    print(f"RESULT: Failed: {e}")
