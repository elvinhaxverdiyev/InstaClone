from rest_framework.permissions import BasePermission

class CanManageObjectPermission(BasePermission):
    
    def has_permission(self, request, view):
        if request.method in ["GET", "DELETE", "PUT", "PATCH", "POST"]:
            return request.user and request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in ["DELETE", "PUT", "PATCH"]:
            profile = getattr(obj, "profile", None) or getattr(obj, "user", None)
            if profile is None:
                return request.user.is_staff
            return profile.user == request.user or request.user.is_staff
        
        if request.method == "GET":
            profile = getattr(obj, "profile", None) or getattr(obj, "user", None)
            if profile is None:
                return False  
            return (profile.user == request.user or 
                   request.user.is_staff or 
                   profile.followers.filter(id=request.user.id).exists())
        
        return True