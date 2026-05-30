import os
import time
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import Course, Module, Quiz
from rest_framework.test import APIRequestFactory
from api.views import GenerateCourseView

def test_sql_caching():
    print("=== Testing SQL Course Caching and Content Fallbacks ===")
    
    # 1. Clean up existing SQL courses to ensure clean run
    Course.objects.filter(topic__iexact="sql").delete()
    print("Deleted any existing SQL courses from DB.")

    factory = APIRequestFactory()
    view = GenerateCourseView.as_view()

    # 2. First Run - Should generate from fallbacks and save
    print("\n[Run 1] Requesting SQL Course (Generating fresh)...")
    start_time = time.time()
    request1 = factory.post('/api/generate-course/', {'topic': 'SQL', 'force': False}, format='json')
    response1 = view(request1)
    duration1 = time.time() - start_time
    
    print(f"Status Code: {response1.status_code}")
    print(f"Duration: {duration1:.4f} seconds")
    
    assert response1.status_code == 201, f"Expected 201, got {response1.status_code}"
    data1 = response1.data
    print(f"Course Title: {data1.get('title')}")
    print(f"Modules Generated: {len(data1.get('modules', []))}")
    
    # Verify module content fields
    first_module = data1['modules'][0]
    print(f"\nFirst Module Details:")
    print(f"Name: {first_module.get('name')}")
    print(f"Theory length: {len(first_module.get('theory', ''))} characters")
    print(f"Mini Labs count: {len(first_module.get('mini_labs', []))}")
    print(f"Preloaded code: {repr(first_module.get('preloaded_code'))}")
    print(f"Quizzes count: {len(first_module.get('quizzes', []))}")
    
    assert len(first_module.get('theory', '')) > 200, "Theory content is too short or missing!"
    assert len(first_module.get('mini_labs', [])) > 0, "Mini labs are missing!"
    assert len(first_module.get('quizzes', [])) == 10, f"Expected 10 quizzes, got {len(first_module.get('quizzes', []))}"
    assert first_module.get('preloaded_code') != "", "Preloaded starter code is missing!"

    # 3. Second Run - Should serve instantly from local database cache
    print("\n[Run 2] Requesting SQL Course again (Should hit Cache)...")
    start_time = time.time()
    request2 = factory.post('/api/generate-course/', {'topic': 'SQL', 'force': False}, format='json')
    response2 = view(request2)
    duration2 = time.time() - start_time
    
    print(f"Status Code: {response2.status_code}")
    print(f"Duration: {duration2:.4f} seconds")
    
    assert response2.status_code == 200, f"Expected 200 (OK from cache), got {response2.status_code}"
    print("Cache verification SUCCESSFUL. Served instantly from cache!")
    print(f"Speedup: {duration1 / duration2:.1f}x faster!")

if __name__ == '__main__':
    test_sql_caching()
