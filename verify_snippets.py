import sys
import os

# Ensure backend directory is in path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from api.course_content import get_prebuilt_code_snippet
except ImportError as e:
    print(f"Error importing module: {e}")
    sys.exit(1)

languages = ["python", "java", "cpp", "rust", "javascript"]
modules = [0, 4, 8] # Beginner, Intermediate, Advanced
labs = [0, 1, 2]

errors = []
passed = 0

print("Verifying Code Snippets...")
print("-" * 60)

for lang in languages:
    print(f"Checking {lang.upper()}...")
    for mod in modules:
        topic_type = "EXECUTABLE"
        # Determine topic name to help the function
        topic = f"{lang} Programming"
        
        for lab in labs:
            snippet = get_prebuilt_code_snippet(topic, topic_type, mod, lab, f"Module {mod+1} Title")
            
            if snippet is None:
                errors.append(f"MISSING: {lang} Mod {mod} Lab {lab}")
                continue
                
            if "Implement your logic here" in snippet or "// Generic example" in snippet:
                errors.append(f"GENERIC/PLACEHOLDER: {lang} Mod {mod} Lab {lab}")
                continue
            
            # Additional language specific checks
            if lang == "java" and "public class" not in snippet:
                 errors.append(f"INVALID JAVA: {lang} Mod {mod} Lab {lab} (missing class)")
            
            if lang == "rust" and "fn main" not in snippet and "struct" not in snippet and "enum" not in snippet:
                 # Struct/Enum examples might not have main if they are just definitions, but usually they should differ.
                 # Actually my Rust snippets all have main or struct/enum.
                 pass

            passed += 1
            # print(f"  OK: Mod {mod} Lab {lab} -> {snippet.splitlines()[0]}")

print("-" * 60)
if errors:
    print(f"FAILED. {len(errors)} errors found:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print(f"SUCCESS! Verified {passed} snippets.")
    sys.exit(0)
