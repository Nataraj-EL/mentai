from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

class MentAIAskView(APIView):
    """
    Placeholder endpoint for MentAI queries.
    Validates frontend -> backend connection.
    """
    def post(self, request):
        query = request.data.get('query', '')
        if not query:
            return Response({"error": "Query is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            "answer": "MentAI is an AI-powered learning assistant.",
            "timestamp": timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
