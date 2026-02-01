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
            
            # 3. Retry Logic: 2 retries (total 3 attempts) with small delay
            max_retries = 2
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    response = model.generate_content(query)
                    
                    if response and response.text:
                        return Response({
                            "answer": response.text,
                            "timestamp": timezone.now().isoformat()
                        }, status=status.HTTP_200_OK)
                    else:
                        raise ValueError("Empty response from AI service")

                except Exception as e:
                    last_exception = e
                    logger.warning(
                        f"Attempt {attempt + 1} failed for /api/v1/ask. "
                        f"Exception: {str(e)} | Timestamp: {timezone.now().isoformat()}"
                    )
                    if attempt < max_retries:
                        import time
                        time.sleep(0.5) # 0.5s delay between retries
            
            # If all retries fail
            logger.error(
                f"Gemini API failure after {max_retries + 1} attempts. "
                f"Status: {getattr(last_exception, 'status_code', 'N/A')} | "
                f"Error: {str(last_exception)} | Timestamp: {timezone.now().isoformat()}"
            )
            return Response({
                "answer": "I'm sorry, I'm having trouble processing your request right now. Please try again later.",
                "timestamp": timezone.now().isoformat()
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Unexpected error in /api/v1/ask: {str(e)}")
            return Response({
                "answer": "An unexpected error occurred. Please try again later.",
                "timestamp": timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
