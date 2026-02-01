import os
import sys
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.ai_service import GeminiService

s = GeminiService()
if s.client:
    try:
        print("Listing available models...")
        pager = s.client.models.list()
        count = 0
        for m in pager:
            print(f" - {m.name}")
            count += 1
            if count > 20: break
    except Exception as e:
        print(f"Error listing models: {e}")
