from django.urls import path
from . import views
from .views_health import HealthCheckView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health'),
    path('generate-course/', views.GenerateCourseView.as_view(), name='generate-course'),
    path('quiz/<int:module_id>/', views.QuizView.as_view(), name='quiz'),
    path('quiz/<int:module_id>/submit/', views.SubmitQuizView.as_view(), name='submit-quiz'),
    path('validate-video/', views.ValidateVideoView.as_view(), name='validate-video'),
    path('execute-code/', views.CodeExecutionView.as_view(), name='execute-code'),
    # Platform API
    path('auth/sync/', views.AuthSyncView.as_view(), name='auth-sync'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('progress/update/', views.UpdateProgressView.as_view(), name='progress-update'),
] 
