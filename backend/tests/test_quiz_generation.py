from api.course_content import get_module_quiz

def test_language(topic, type, title):
    print(f"\n>>> Testing {topic} ({type}) <<<")
    failed = False
    for mod in [1, 2, 5, 10]:
        quiz = get_module_quiz(topic, type, title, mod)
        count = len(quiz.get('questions', []))
        status = "PASS" if count >= 10 else "FAIL"
        print(f"  Module {mod}: {count} questions -> {status}")
        if count < 10: failed = True
    
    if failed:
        print(f"!!! {topic} FAILED verification !!!")
    else:
        print(f"*** {topic} PASSED all modules ***")

if __name__ == "__main__":
    test_language("Python", "EXECUTABLE", "Python Basics")
    test_language("JavaScript", "EXECUTABLE", "JS Intro")
    test_language("Java", "EXECUTABLE", "Java Basics")
    test_language("Go", "EXECUTABLE", "Go Basics")
    test_language("React", "FRAMEWORK", "Components")
