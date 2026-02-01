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

        # Initialize Gemini once
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {str(e)}")
            return Response(
                {"error": "AI service initialization failed."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Retry Logic: Up to 2 retries (3 total attempts) with 0.5s delay
        max_retries = 2
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                response = model.generate_content(query)
                
                # Check if the response was blocked or empty
                if not response:
                    raise ValueError("Empty response object from Gemini")
                
                # Check for blocked response
                if hasattr(response, 'candidates') and not response.candidates:
                    # Check prompt feedback if available
                    feedback = ""
                    if hasattr(response, 'prompt_feedback'):
                        feedback = f" | Feedback: {str(response.prompt_feedback)}"
                    raise ValueError(f"No candidates returned by Gemini{feedback}")

                if response.text:
                    return Response({
                        "answer": response.text,
                        "timestamp": timezone.now().isoformat()
                    }, status=status.HTTP_200_OK)
                else:
                    raise ValueError("Response text is empty")

            except Exception as e:
                last_exception = e
                # Check for specific safety block errors
                error_msg = str(e)
                if "finish_reason" in error_msg or "safety" in error_msg.lower():
                    logger.warning(f"Gemini safety block for query: '{query}'")
                    return Response({
                        "answer": "I'm sorry, I cannot discuss that topic as it may violate safety guidelines. Please ask something else.",
                        "timestamp": timezone.now().isoformat()
                    }, status=status.HTTP_200_OK)

                logger.warning(
                    f"Attempt {attempt + 1} failed for query: '{query}'. "
                    f"Error: {str(e)} | Timestamp: {timezone.now().isoformat()}"
                )
                if attempt < max_retries:
                    import time
                    time.sleep(0.5)
        
        # All attempts failed
        logger.error(
            f"Gemini API failure after {max_retries + 1} attempts for query: '{query}'. "
            f"Error: {str(last_exception)} | Timestamp: {timezone.now().isoformat()}"
        )
        return Response({
            "answer": "I'm sorry, I'm having trouble processing your request right now. Please try again later.",
            "timestamp": timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
