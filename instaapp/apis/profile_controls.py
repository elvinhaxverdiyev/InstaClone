from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .posts_controls import Pagination
from profiles.models import Profile
from profiles.serializers import ProfileSerializer, UserSerializer


class ProfileListAPIView(APIView):
    """API View to list all profiles with pagination support."""
    permission_classes = [IsAuthenticated]
    pagination_class = Pagination 
    
    def get(self, request, *args, **kwargs):
        """Handles GET request to list all profiles with pagination."""
        profiles = Profile.objects.all()  
        paginator = self.pagination_class() 
        result_page = paginator.paginate_queryset(profiles, request)
        
        serializer = ProfileSerializer(result_page, many=True)  
        return Response(serializer.data, status=status.HTTP_200_OK) 
    

class ProfileSearchAPIView(APIView):
    """API View to search profiles by username."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
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

    def post(self, request, *args, **kwargs):
        """Handles POST request to create a new profile."""
        serializer = ProfileSerializer(data=request.data)

        if serializer.is_valid():
            profile = serializer.save()
            refresh = RefreshToken.for_user(profile)
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
    
    def post(self, request, *args, **kwargs):
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

    def post(self, request):
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

    def post(self, request, user_id):
        user = request.user 
        profile_to_follow = get_object_or_404(Profile, id=user_id)

        if profile_to_follow.user == user:
            return Response({"detail": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)

        profile_to_follow.followers.add(user)
        return Response({"detail": "You are now following this user."}, status=status.HTTP_200_OK)


class UnfollowAPIView(APIView):
    """
    API for unfollowing another user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        user = request.user
        profile_to_unfollow = get_object_or_404(Profile, id=user_id)

        if profile_to_unfollow.user == user:
            return Response({"detail": "You cannot unfollow yourself."}, status=status.HTTP_400_BAD_REQUEST)

        profile_to_unfollow.followers.remove(user)
        return Response({"detail": "You have unfollowed this user."}, status=status.HTTP_200_OK)
    
    
class ProfileFollowListAPIView(APIView):
    """
    API endpoint to retrieve lists of followers and following profiles using the Profile model by ID
    """

    def get(self, request, profile_id, format=None):
        try:
            profile = get_object_or_404(Profile, id=profile_id)
            follower_users = profile.followers.all()
            follower_profiles = Profile.objects.filter(user__in=follower_users)
            follower_serializer = ProfileSerializer(follower_profiles, many=True)
            following_users = profile.user.followings.values_list("user", flat=True) 
            following_profiles = Profile.objects.filter(user__in=following_users)
            following_serializer = ProfileSerializer(following_profiles, many=True)

            data = {
                "followers": follower_serializer.data,
                "following": following_serializer.data
            }
            
            return Response(data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": f"Profile not found or an error occurred: {str(e)}"},
                status=status.HTTP_404_NOT_FOUND
            )
            

class ProfileDetailView(APIView):
    """
    API for retrieving user profile details.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        profile = get_object_or_404(Profile, user__id=user_id)  
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
