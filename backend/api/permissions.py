from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrReadOnlyPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.author == request.user
    
# from rest_framework import permissions


# class IsAuthorOrReadOnlyPermission(permissions.BasePermission):
#     """Автор может изменять, остальные только читать."""

#     def has_permission(self, request, view):
#         """Проверка прав доступа к представлению."""
#         return request.user and request.user.is_authenticated

#     def has_object_permission(self, request, view, obj):
#         """Проверка прав доступа к объекту."""
#         return (
#             request.method in permissions.SAFE_METHODS
#             or obj.author == request.user
#         )