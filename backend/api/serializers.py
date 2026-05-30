from rest_framework import serializers
from .models import Course, Module, Video, Quiz, Progress
from .course_content import get_practice_problems, get_mini_project
from .topic_classifier import TopicClassifier


def _module_title_from_name(name: str) -> str:
    if ": " in name:
        return name.split(": ", 1)[1]
    return name


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'title', 'url', 'is_one_shot']

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'question', 'options', 'correct_answer', 'question_type', 'explanation']

class ModuleSerializer(serializers.ModelSerializer):
    videos = VideoSerializer(many=True, read_only=True)
    quizzes = QuizSerializer(many=True, read_only=True)
    theory = serializers.CharField(source='content', read_only=True)
    mini_labs = serializers.JSONField(source='case_scenarios', read_only=True)
    preloaded_code = serializers.SerializerMethodField()
    practice_problems = serializers.SerializerMethodField()
    mini_project = serializers.SerializerMethodField()
    
    class Meta:
        model = Module
        fields = [
            'id', 'name', 'description', 'content', 'difficulty', 'order',
            'code_examples', 'case_scenarios', 'videos', 'quizzes',
            'theory', 'mini_labs', 'preloaded_code', 'practice_problems', 'mini_project',
        ]

    def _topic_context(self, obj):
        topic_label = obj.course.topic or obj.course.title or "general"
        classification = TopicClassifier.classify(topic_label)
        return classification["language"], topic_label

    def get_preloaded_code(self, obj):
        if obj.case_scenarios and len(obj.case_scenarios) > 0:
            first_lab = obj.case_scenarios[0]
            if isinstance(first_lab, dict) and first_lab.get('preloaded_code'):
                return first_lab['preloaded_code']
        
        if obj.code_examples and len(obj.code_examples) > 0:
            first_example = obj.code_examples[0]
            if isinstance(first_example, dict) and 'code' in first_example:
                return first_example['code']
        return ""

    def get_practice_problems(self, obj):
        language, topic_label = self._topic_context(obj)
        return get_practice_problems(topic_label or language, _module_title_from_name(obj.name))

    def get_mini_project(self, obj):
        language, _ = self._topic_context(obj)
        return get_mini_project(language, _module_title_from_name(obj.name), obj.order or 1)

class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    videos = VideoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'content', 'topic', 'created_at', 'modules', 'videos']

class ProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Progress
        fields = '__all__'
