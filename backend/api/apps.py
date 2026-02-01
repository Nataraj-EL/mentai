from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        import os
        import logging
        logger = logging.getLogger('api')
        if os.getenv("GEMINI_API_KEY"):
            logger.info("MentAI Startup: GEMINI_API_KEY is loaded and configured.")
        else:
            logger.warning("MentAI Startup: GEMINI_API_KEY is MISSING from environment variables.")
