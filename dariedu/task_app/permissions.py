# from rest_framework import permissions

# Вернуть по необходимости!
# Для метода завершения задачи куратором
# class IsAbleCompleteTask(permissions.BasePermission):
#     """
#     Object-level permission to allow only curator of the task to complete it.
#     """
#     def has_object_permission(self, request, view, obj):
#        return request.user.is_staff and request.user == obj.curator  # TODO swap to comment
