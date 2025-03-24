from rest_framework.permissions import BasePermission

class CanManageObjectPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in ["GET", "DELETE", "PUT", "PATCH", "POST"]:
            return request.user and request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        profile = getattr(obj, "profile", None) or getattr(obj, "user", None)
        if profile is None:
            return request.user.is_staff

        if request.method in ["DELETE", "PUT", "PATCH"]:
            return profile.user == request.user or request.user.is_staff
        
        if request.method in ["GET", "POST"]:
            return (profile.user == request.user or 
                    request.user.is_staff or 
                    profile.followers.filter(id=request.user.profile.id).exists())
        
        return True