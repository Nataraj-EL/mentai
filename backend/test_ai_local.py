import os
import sys
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load local env
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
    logger.info(f"Loaded environment from {env_path}")
else:
    logger.warning(f".env not found at {env_path}")

# Add backend to path so we can import api module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.ai_service import GeminiService

def test_ask():
    print("Testing GeminiService...")
    service = GeminiService()
    if not service.client:
        print("Failed to initialize client (Check API Key)")
        if not os.getenv("GEMINI_API_KEY"):
             print("GEMINI_API_KEY is missing from env")
        else:
             print(f"GEMINI_API_KEY found (len={len(os.getenv('GEMINI_API_KEY'))})")
        return

    print("Client initialized. Sending query...")
    try:
        response = service.ask_mentai("Explain what you can do.")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error during ask_mentai: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ask()
