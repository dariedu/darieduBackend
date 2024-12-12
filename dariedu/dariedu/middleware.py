# middleware.py
import logging
import traceback

logger = logging.getLogger('django.request')


class ErrorHandlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if response.status_code >= 400:
            logger.warning(
                f'Error {response.status_code}: '
                f'Path: {request.path}, '
                f'Method: {request.method}'
            )

        return response