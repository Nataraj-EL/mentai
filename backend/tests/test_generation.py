from google import genai
import os

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found.")
    exit(1)

client_v1beta = genai.Client(api_key=api_key, http_options={'api_version': 'v1beta'})
client_v1 = genai.Client(api_key=api_key, http_options={'api_version': 'v1'})
client_v1alpha = genai.Client(api_key=api_key, http_options={'api_version': 'v1alpha'})

versions = {'v1beta': client_v1beta, 'v1': client_v1, 'v1alpha': client_v1alpha}

for ver, cli in versions.items():
    print(f"Testing version: {ver}")
    try:
        response = cli.models.generate_content(
            model='gemini-1.5-flash',
            contents="Hello, world!",
            config={
                'response_mime_type': 'application/json'
            }
        )
        print(f"Success with {ver}: {response.text}")
        break
    except Exception as e:
        print(f"Failed with {ver}: {e}")
        
print("Test script finished.")
