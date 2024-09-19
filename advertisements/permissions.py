from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Разрешение, позволяющее доступ только владельцу объекта для изменения или удаления.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        else:
            return obj.creator == request.user 

