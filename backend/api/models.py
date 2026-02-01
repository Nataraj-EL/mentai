from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Course(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    topic = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.user.username if self.user else 'Anonymous'})"

class Module(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    name = models.CharField(max_length=255)
    description = models.TextField()
    content = models.TextField(default="", blank=True)  # Detailed tutorial content
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    order = models.IntegerField(default=0)
    code_examples = models.JSONField(default=list, blank=True)  # For technical topics
    case_scenarios = models.JSONField(default=list, blank=True)  # For non-technical topics
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.title} - {self.name}"

class Video(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='videos', null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='videos', null=True, blank=True)
    title = models.CharField(max_length=255)
    url = models.URLField()
    is_one_shot = models.BooleanField(default=False)  # For the impressive one-shot video

    def __str__(self):
        return self.title

class Quiz(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='quizzes', null=True, blank=True)
    question = models.TextField()
    options = models.JSONField()
    correct_answer = models.CharField(max_length=255)
    question_type = models.CharField(max_length=20, default='mcq')  # mcq, code, logic
    explanation = models.TextField(default="", blank=True)  # Explanation for the correct answer

    def __str__(self):
        return self.question

class Progress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, null=True, blank=True)
    completed = models.BooleanField(default=False)
    quiz_score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.course.title} - {'Completed' if self.completed else 'Incomplete'}"

class UserProgress(models.Model):
    """
    Flexible progress tracking for dynamic/transient courses.
    Stores progress against a canonical topic slug rather than a database Course ID.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_progress')
    topic_slug = models.CharField(max_length=255) # e.g. "python", "react"
    display_title = models.CharField(max_length=255) # e.g. "Python Programming"
    
    current_module_id = models.IntegerField(default=1) # The module user is currently on
    completed_modules = models.JSONField(default=list, blank=True) # List of IDs [1, 2, 3]
    quiz_scores = models.JSONField(default=dict, blank=True) # {"1": 80, "2": 100}
    
    last_visited_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # One progress record per user per topic
        unique_together = ('user', 'topic_slug')
        ordering = ['-last_visited_at']

    def __str__(self):
        return f"{self.user.username} - {self.display_title}"
