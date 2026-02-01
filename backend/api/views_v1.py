import os
import logging
import google.generativeai as genai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

logger = logging.getLogger('api')

class MentAIAskView(APIView):
    """
    Core AI endpoint for MentAI.
    Uses Gemini AI to generate answers to user queries.
    """
    def post(self, request):
        query = request.data.get('query')

        # 1. Validation: query must exist and be a non-empty string
        if not query or not isinstance(query, str) or not query.strip():
            return Response(
                {"error": "Invalid request: 'query' must be a non-empty string."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Gemini Integration
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY is not set in environment variables.")
            return Response(
                {"error": "AI service configuration error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            response = model.generate_content(query)
            
            if response and response.text:
                return Response({
                    "answer": response.text,
                    "timestamp": timezone.now().isoformat()
                }, status=status.HTTP_200_OK)
            else:
                raise ValueError("Empty response from AI")

        except Exception as e:
            logger.error(f"Gemini API failure: {str(e)}")
            return Response({
                "answer": "I'm sorry, I'm having trouble processing your request right now. Please try again later.",
                "timestamp": timezone.now().isoformat()
            }, status=status.HTTP_200_OK) # Returning 200 with fallback message as per "graceful fallback" requirement
