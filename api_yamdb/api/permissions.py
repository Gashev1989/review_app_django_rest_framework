from rest_framework import permissions


class IsOwnerIReadOnly(permissions.BasePermission):
    """Имеет право распоряжаться своим контентом"""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
            or request.user.is_superuser
        )

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )


class IsAdmin(permissions.BasePermission):
    """Полная свобода действий"""

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_admin
            or request.user.is_superuser
        )

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and request.user.is_admin
            or request.user.is_superuser
            or request.parser_context['kwargs'].get('pk') == 'me'
            and request.user.is_authenticated
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """Администратор может все, остальные только читать."""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_admin
            or request.user.is_superuser
        )

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and (
                request.user.is_admin
                or request.user.is_superuser
            ))
        )
