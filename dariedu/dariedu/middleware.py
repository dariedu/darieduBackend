# middleware.py
import logging
import traceback
import time
import json

from django.db import connection


class ErrorHandlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.logger = logging.getLogger('api.requests')
        start_time = time.time()

        self.logger.info(f"Request: {request.method} {request.get_full_path()}")

        response = self.get_response(request)

        duration = time.time() - start_time
        self.logger.info(f"Response: {response.status_code} - Duration: {duration:.2f}s")

        if response.status_code >= 400:
            self.logger.warning(
                f'Error {response.status_code}: '
                f'Path: {request.path}, '
                f'Method: {request.method}'
                f'User-Agent: {request.META.get("HTTP_USER_AGENT")}'
                f'Referer: {request.META.get("HTTP_REFERER")}'
                f'User IP: {request.META.get("REMOTE_ADDR")}'
                f'Exception: {traceback.format_exc()}'
                f'User: {request.user.is_authenticated} tg_id: {request.user.tg_id}'
            )

        return response


class RequestResponseLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger = logging.getLogger('django.server')

        try:
            if request.body:
                body = request.body.decode('utf-8')
                logger.warning(f"Request Body: {body}")

                if request.method == 'POST':
                    if request.content_type == 'application/json':
                        try:
                            post_data = json.loads(body)
                            logger.warning(f"POST JSON Data: {json.dumps(post_data, ensure_ascii=False)}")
                        except json.JSONDecodeError:
                            logger.error("Invalid JSON data received.")
                    else:
                        logger.warning(f"POST Data: {request.POST.dict()}")
            else:
                logger.warning("Request Body is empty.")
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


class SecurityLoggingMiddleware:
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        self.log_request(request)
        self.logger = logging.getLogger('middleware.security')

        response = self.get_response(request)

        self.log_response(request, response)

        return response

    def log_request(self, request):
        if request.user.is_authenticated:
            self.logger.info(f"User  {request.user.username} accessed {request.path}")
        else:
            self.logger.info(f"Anonymous user accessed {request.path}")

    def log_response(self, request, response):
        self.logger.info(f"Response status: {response.status_code} for {request.path}")

        if response.status_code == 403:
            self.logger.warning(f"Access denied for {request.path} - "
                                f"User: {request.user.username if request.user.is_authenticated else 'Anonymous'}")
        elif response.status_code == 401:
            self.logger.warning(f"Unauthorized access attempt for {request.path} -"
                                f" User: {request.user.username if request.user.is_authenticated else 'Anonymous'}")


class SchemaLoggingMiddleware:
    def __init__(self, get_response=None):
        self.get_response = get_response
        self.logger = logging.getLogger('django.db.backends.schema')

    def __call__(self, request):
        response = self.get_response(request)

        self.log_schema_changes()

        return response

    def log_schema_changes(self):
        for query in connection.queries:
            if "CREATE" in query['sql'] or "ALTER" in query['sql'] or "DROP" in query['sql']:
                self.logger.info(f"Schema Change: {query['sql']} - Time: {query['time']}s")
