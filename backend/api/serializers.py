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
    
    class Meta:
        model = Module
        fields = ['id', 'name', 'description', 'content', 'difficulty', 'order', 'code_examples', 'case_scenarios', 'videos', 'quizzes']

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