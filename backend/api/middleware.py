import logging

logger = logging.getLogger('api')

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info(f"Incoming request: {request.method} {request.path}")
        response = self.get_response(request)
        if response.status_code >= 400:
            logger.error(f"Error on {request.path} (Status {response.status_code})")
        return response
