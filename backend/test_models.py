import os
import sys
import logging
from dotenv import load_dotenv
from google import genai

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load env
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("No API Key")
    sys.exit(1)

# Try v1beta
print("Testing with v1beta...")
client = genai.Client(api_key=api_key, http_options={'api_version': 'v1beta'})

models_to_test = ['gemini-1.5-flash', 'gemini-1.5-flash-001', 'gemini-1.5-pro']

for m in models_to_test:
    print(f"Testing {m}...")
    try:
        response = client.models.generate_content(
            model=m,
            contents='Hello'
        )
        print(f"SUCCESS with {m}: {response.text}")
    except Exception as e:
        print(f"FAIL with {m}: {e}")

print("-" * 20)
# Try v1 default (no http_options)
print("Testing with v1 (default)...")
client_v1 = genai.Client(api_key=api_key)
for m in models_to_test:
    print(f"Testing {m}...")
    try:
        response = client_v1.models.generate_content(
            model=m,
            contents='Hello'
        )
        print(f"SUCCESS with {m}: {response.text}")
    except Exception as e:
        print(f"FAIL with {m}: {e}")
