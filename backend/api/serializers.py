from rest_framework import serializers
from .models import Course, Module, Video, Quiz, Progress

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
    
    class Meta:
        model = Module
        fields = ['id', 'name', 'description', 'content', 'difficulty', 'order', 'code_examples', 'case_scenarios', 'videos', 'quizzes', 'theory', 'mini_labs', 'preloaded_code']

    def get_preloaded_code(self, obj):
        # Fallback 1: check if the first mini_lab has preloaded_code
        if obj.case_scenarios and len(obj.case_scenarios) > 0:
            first_lab = obj.case_scenarios[0]
            if isinstance(first_lab, dict) and 'preloaded_code' in first_lab and first_lab['preloaded_code']:
                return first_lab['preloaded_code']
        
        # Fallback 2: check if any code_examples are available
        if obj.code_examples and len(obj.code_examples) > 0:
            first_example = obj.code_examples[0]
            if isinstance(first_example, dict) and 'code' in first_example:
                return first_example['code']
        return ""

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