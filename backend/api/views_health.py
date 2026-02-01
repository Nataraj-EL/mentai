from rest_framework.views import APIView
from rest_framework.response import Response

class HealthCheckView(APIView):
    def get(self, request):
        import os
        return Response({
            "status": "ok",
            "service": "MentAI Backend",
            "environment": "production",
            "gemini_api_configured": bool(os.getenv("GEMINI_API_KEY"))
        }, status=200)

def root_status(request):
    from django.http import JsonResponse
    return JsonResponse({"status": "MentAI backend is running"}, status=200)
