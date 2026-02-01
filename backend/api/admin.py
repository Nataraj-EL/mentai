from django.contrib import admin
from .models import Course, Video, Quiz, Progress

admin.site.register(Course)
admin.site.register(Video)
admin.site.register(Quiz)
admin.site.register(Progress)
