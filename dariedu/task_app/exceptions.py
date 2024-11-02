from rest_framework import status
from rest_framework.exceptions import APIException


class BadRequest(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Bad request'
    default_code = 'bad_request'


class Forbidden(APIException):
    """Исключение для пользователя если не подтверждён, поле is_confirmed
    статус кода - 403
    сообщение - User does not confirmed
    для детальной отладки сообщение - forbidden_confirmed"""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'User does not confirmed'
    default_code = 'forbidden_confirmed'
