
from backend.api.topic_classifier import TopicClassifier
import sys

def test(topic):
    result = TopicClassifier.classify(topic)
    print(f"Topic: '{topic}' -> {result}")

if __name__ == "__main__":
    test("React")
    test("Python")
    test("Ancient History")
    test("react")
