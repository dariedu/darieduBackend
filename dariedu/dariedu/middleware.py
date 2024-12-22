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


class RequestResponseLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            body = request.body.decode('utf-8')
            logger.warning(f"Request Body: {body}")

            if request.method == 'POST':
                logger.warning(f"POST Data: {request.POST}")
        except Exception as e:
            logger.error(f"Error logging request body: {e}")

        response = self.get_response(request)

        try:
            if 'application/json' in response.get('Content-Type', ''):
                body = response.content.decode('utf-8')
                logger.warning(f"Response Body: {body}")
        except Exception as e:
            logger.error(f"Error logging response body: {e}")

        return response
