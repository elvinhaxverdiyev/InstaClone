from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import HttpRequest

from .posts_controls import Pagination
from profiles.models import Profile
from profiles.serializers import ProfileSerializer, UserSerializer
from .permissions_cotrols import CanManageObjectPermission


class ProfileListAPIView(APIView):
    """API View to list all profiles with pagination support."""
    permission_classes = [IsAuthenticated]
    pagination_class = Pagination 
    
    def get(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Handles GET request to list all profiles with pagination."""
        profiles = Profile.objects.all()  
        paginator = self.pagination_class() 
        result_page = paginator.paginate_queryset(profiles, request)
        
        serializer = ProfileSerializer(result_page, many=True)  
        return Response(serializer.data, status=status.HTTP_200_OK) 
    

class ProfileSearchAPIView(APIView):
    """API View to search profiles by username."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Handles GET request to search profiles by username."""
        query = request.query_params.get('q', None)
        if query:
            profiles = Profile.objects.filter(user__username__icontains=query)
        else:
            profiles = Profile.objects.all()
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RegisterAPIView(APIView):
    """API View to register a new profile."""

    def post(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Handles POST request to create a new profile."""
        serializer = ProfileSerializer(data=request.data)

        if serializer.is_valid():
            profile = serializer.save()
            refresh = RefreshToken.for_user(profile.user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            return Response({
                "user": ProfileSerializer(profile).data,
                "access": access_token,
                "refresh": refresh_token
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LoginAPIView(APIView):
    """API View to authenticate users and return JWT tokens."""
    
    def post(self, request: HttpRequest, *args, **kwargs) -> Response:
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name
                },
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }, status=status.HTTP_200_OK)

        return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: HttpRequest) -> Response:
        """Handles POST request to logout the user by blacklisting the refresh token."""
        try:
            refresh_token = request.data.get("refresh_token")
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({"message": "User successfully logged out."}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class FollowAPIView(APIView):
    """
    API for following another user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request: HttpRequest, user_name: str) -> Response:
        user = request.user 
        profile_to_follow = get_object_or_404(Profile, user__username=user_name)

        if profile_to_follow.user == user:
            return Response({"detail": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)

        profile_to_follow.followers.add(user)
        return Response({"detail": "You are now following this user."}, status=status.HTTP_200_OK)


class UnfollowAPIView(APIView):
    """
    API for unfollowing another user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request: HttpRequest, user_name: str) -> Response:
        user = request.user
        profile_to_unfollow = get_object_or_404(Profile, user__username=user_name)

        if profile_to_unfollow.user == user:
            return Response({"detail": "You cannot unfollow yourself."}, status=status.HTTP_400_BAD_REQUEST)

        profile_to_unfollow.followers.remove(user)
        return Response({"detail": "You have unfollowed this user."}, status=status.HTTP_200_OK)
    
    
class ProfileFollowersListAPIView(APIView):
    """Returns a list of profiles following the specified profile ID."""
    permission_classes = [CanManageObjectPermission]

    def get(self, request: HttpRequest, user_name: str, format=None) -> Response:
        profile = get_object_or_404(Profile, user__username=user_name)
        follower_users = profile.followers.all()
        follower_profiles = Profile.objects.filter(user__in=follower_users)
        follower_serializer = ProfileSerializer(follower_profiles, many=True)
        return Response({"Followers": follower_serializer.data}, status=status.HTTP_200_OK)
            
            
class ProfileFollowingsListAPIView(APIView):
    """Returns a list of profiles followed by the specified profile."""
    permission_classes = [CanManageObjectPermission]

    def get(self, request: HttpRequest, user_name: str, format=None) -> Response:
        profile = get_object_or_404(Profile, user__username=user_name)
        following_profiles = profile.user.followings.all()
        following_serializer = ProfileSerializer(following_profiles, many=True, context={"request": request})
        return Response({"Following": following_serializer.data}, status=status.HTTP_200_OK)
    

class ProfileDetailView(APIView):
    """API for retrieving user profile details."""
    permission_classes = [CanManageObjectPermission]

    def get(self, request: HttpRequest, user_name: str) -> Response:
        profile = get_object_or_404(Profile, user__username=user_name)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request: HttpRequest, user_name: str) -> Response:
        """Partially update user profile details."""
        profile = get_object_or_404(Profile, user__username=user_name)
        print(f"Request User: {request.user}, Profile Owner: {profile.user}")
        if request.user != profile.user:
            return Response({"detail": "You do not have permission to edit this profile."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
