from rest_framework.permissions import BasePermission
from django.http import HttpRequest
from rest_framework.views import APIView

class CanManageObjectPermission(BasePermission):
    """Permission class that allows access if the user is the object owner,
    a follower of the owner, or an admin, depending on the request method."""
    
    def has_permission(self, request: HttpRequest, view: APIView) -> bool:
        """
        Checks general permission.
        - Grants access if the user is authenticated.
        """
        
        if request.method in ["GET", "DELETE", "PUT", "PATCH", "POST"]:
            return request.user and request.user.is_authenticated
        return True
    

    def has_object_permission(self, request: HttpRequest, view: APIView, obj) -> bool:
        """
        Checks object-level permissions.
        
        - `profile.user == request.user` -> Grants access if the user owns the object.
        - `request.user.is_staff` -> Grants access if the user is an admin.
        - `profile.followers.filter(id=request.user.profile.id).exists()` -> Grants GET access if the user follows the owner.
        """
        
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