from django.urls import path
from .views_v1 import MentAIAskView

urlpatterns = [
    path('ask', MentAIAskView.as_view(), name='ask-v1'),
]
