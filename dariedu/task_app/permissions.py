import functools

from rest_framework import permissions
from rest_framework.request import Request

from .exceptions import Forbidden


# Вернуть по необходимости!
# Для метода завершения задачи куратором
class IsAbleCompleteTask(permissions.BasePermission):
    """
    Object-level permission to allow only curator of the task to complete it.
    """

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff and request.user == obj.curator


class IsCurator(permissions.BasePermission):
    """
    Allow access only to curators.
    """

    def has_permission(self, request, view):
        return request.user.is_staff


def is_confirmed(func):
    """Декоратор, на случай, если пользователь не подтверждён, см. exception.py там объяснение вывода"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                if not request.user.is_confirmed:
                    raise Forbidden()
        return func(*args, **kwargs)
    return wrapper
