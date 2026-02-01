
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'api'))

from api.topic_classifier import TopicClassifier
from api.ai_service import GeminiService
from api.course_content import get_module_titles

def test_safety():
    print(">>> Testing Safety Hardening <<<")
    
    # 1. Topic Classification
    topic = "QuantumBanana"
    classification = TopicClassifier.classify(topic)
    print(f"Topic: {topic}")
    print(f"Classification: {classification}")
    
    if classification['language'] != 'general':
        print("FAIL: Classification language should be 'general'")
        sys.exit(1)
        
    if classification['execution_enabled'] is not False:
        print("FAIL: Execution should be disabled")
        sys.exit(1)
        
    print("PASS: Classification Correct")
    
    # 2. AI Service Safety
    ai = GeminiService()
    # Mock client presence if needed for the test to reach the check
    ai.client = True 
    
    content = ai.generate_module_content(topic, "general", "Intro", 1)
    print(f"Content: {content}")
    
    if "structured content" not in content['content']:
        print("FAIL: Content should be placeholder message")
        sys.exit(1)
        
    if len(content['code_examples']) > 0:
         print("FAIL: Should have no code examples")
         sys.exit(1)
         
    print("PASS: AI Service Safety Correct")

    # 3. Fallback Titles
    titles = get_module_titles("general")
    print(f"Titles: {titles}")
    if "Overview of general" not in titles[0]:
         print("FAIL: Titles should use generic fallback")
         sys.exit(1)
         
    print("PASS: Fallback Titles Correct")
    print("\nALL SAFETY CHECKS PASSED")

if __name__ == "__main__":
    test_safety()
