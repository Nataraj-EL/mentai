import os
import logging
import google.generativeai as genai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .ai_service import GeminiService

logger = logging.getLogger('api')

class MentAIAskView(APIView):
    """
    Core AI endpoint for MentAI with automated retries.
    """
    def post(self, request):
        query = request.data.get('query')

        # Validation: query must exist and be a non-empty string
        if not query or not isinstance(query, str) or not query.strip():
            return Response(
                {"error": "Invalid request: 'query' must be a non-empty string."},
                status=status.HTTP_400_BAD_REQUEST
            )

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY is missing from environment.")
            return Response(
                {"error": "AI service configuration error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Use central GeminiService
        ai_service = GeminiService()
        if not ai_service.client:
            return Response(
                {"error": "AI service configuration error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        try:
            # Use a simplified prompt for the chat assistant
            answer = ai_service.ask_mentai(query)
            if answer:
                return Response({
                    "answer": answer,
                    "timestamp": timezone.now().isoformat()
                }, status=status.HTTP_200_OK)
            else:
                raise ValueError("Empty response from AI service")

        except Exception as e:
            logger.error(f"MentAI chat failure: {str(e)}")
            return Response({
                "answer": "I'm sorry, I'm having trouble processing your request right now. Please try again later.",
                "timestamp": timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
        return Response({
            "answer": "I'm sorry, I'm having trouble processing your request right now. Please try again later.",
            "timestamp": timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
