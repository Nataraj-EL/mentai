import os
import django
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from rest_framework.test import APIRequestFactory
from api.views import CodeExecutionView

def test_compiler_languages():
    print("=== Testing Compiler Execution for All Major Languages ===")
    factory = APIRequestFactory()
    view = CodeExecutionView.as_view()

    # Define test cases for each executable programming language
    test_cases = [
        {
            "name": "Python",
            "topic": "Python Programming",
            "code": "print('Hello from Python!')",
            "expected_stdout": "Hello from Python!\n"
        },
        {
            "name": "Java",
            "topic": "Java Programming",
            "code": 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello from Java!");\n    }\n}',
            "expected_stdout": "Hello from Java!\n"
        },
        {
            "name": "JavaScript",
            "topic": "Modern JavaScript",
            "code": "console.log('Hello from JavaScript!');",
            "expected_stdout": "Hello from JavaScript!\n"
        },
        {
            "name": "Rust",
            "topic": "Rust Systems Programming",
            "code": 'fn main() {\n    println!("Hello from Rust!");\n}',
            "expected_stdout": "Hello from Rust!\n"
        },
        {
            "name": "C++",
            "topic": "C++ Programming",
            "code": '#include <iostream>\nusing namespace std;\nint main() {\n    cout << "Hello from C++!" << endl;\n    return 0;\n}',
            "expected_stdout": "Hello from C++!\n"
        }
    ]

    for tc in test_cases:
        print(f"\n[Testing {tc['name']}] Sending code to Judge0 via execute-code endpoint...")
        request = factory.post('/api/execute-code/', {
            'code': tc['code'],
            'topic': tc['topic']
        }, format='json')
        
        response = view(request)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.data
            stdout = data.get("stdout", "")
            stderr = data.get("stderr", "")
            compile_output = data.get("compile_output", "")
            status_desc = data.get("status", {}).get("description", "Unknown")
            
            print(f"Status: {status_desc}")
            print(f"Stdout: {repr(stdout)}")
            if stderr:
                print(f"Stderr: {repr(stderr)}")
            if compile_output:
                print(f"Compile Output: {repr(compile_output)}")
                
            if status_desc == "Accepted":
                print(f"✓ {tc['name']} compiler is working perfectly!")
            else:
                print(f"⚠ {tc['name']} returned status: {status_desc}")
        else:
            print(f"✗ Failed with error: {response.data}")

if __name__ == '__main__':
    test_compiler_languages()
