from rest_framework.permissions import BasePermission

class CanManageObjectPermission(BasePermission):
    """
    Custom permission class to manage access and modification permissions for objects.

    - **GET, POST requests**:
      - Access is granted if the user is the object owner or an admin.
      - If the user is not the owner but follows the object owner, they can perform a GET request.

    - **PUT, PATCH, DELETE requests**:
      - Access is granted only if the user is the object owner or an admin.

    - If the object has no `profile` or `user` attribute, only staff members can access it.
    """
    
    def has_permission(self, request, view):
        """
        Checks general permission.
        - Grants access if the user is authenticated.
        """
        
        if request.method in ["GET", "DELETE", "PUT", "PATCH", "POST"]:
            return request.user and request.user.is_authenticated
        return True
    

    def has_object_permission(self, request, view, obj):
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