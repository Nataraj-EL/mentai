from rest_framework.views import APIView
from rest_framework.response import Response

class HealthCheckView(APIView):
    def get(self, request):
        return Response({
            "status": "ok",
            "service": "MentAI Backend",
            "environment": "production"
        }, status=200)

def root_status(request):
    from django.http import JsonResponse
    return JsonResponse({"status": "MentAI backend is running"}, status=200)
