from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    """Разрешение, позволяющее редактировать объект только автору."""

    def has_object_permission(self, request, view, obj):
        """Проверяет, является ли пользователь автором объекта."""
        return request.method in SAFE_METHODS or obj.author == request.user
