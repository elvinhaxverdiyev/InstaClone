from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import HttpRequest
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .posts_controls import Pagination
from profiles.models import Profile
from profiles.serializers import ProfileSerializer
from .permissions_cotrols import CanManageObjectPermission
from utils.send_mail import send_verification_email


class ProfileListAPIView(APIView):
    """
    Get a paginated list of all user profiles.

    - Authenticated access required.
    - Results are ordered by ID.
    - Supports pagination via custom class.
    """

    permission_classes = [IsAuthenticated]
    pagination_class = Pagination 
    
    @swagger_auto_schema(
        responses={200: ProfileSerializer(many=True)},
        operation_description="List all profiles with pagination support"
    )
    def get(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Handles GET request to list all profiles with pagination."""
        profiles = Profile.objects.all().order_by("id") 
        paginator = self.pagination_class() 
        result_page = paginator.paginate_queryset(profiles, request)
        
        serializer = ProfileSerializer(result_page, many=True)  
        return Response(serializer.data, status=status.HTTP_200_OK) 
    

class ProfileSearchAPIView(APIView):
    """API View to search profiles by username."""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'q', openapi.IN_QUERY, description="Search query for username", type=openapi.TYPE_STRING, required=False
            )
        ],
        responses={200: ProfileSerializer(many=True)},
        operation_description="Search profiles by username"
    )
    def get(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Handles GET request to search profiles by username."""
        query = request.query_params.get('q', None)
        if query:
            profiles = Profile.objects.filter(user__username__icontains=query)
        else:
            profiles = Profile.objects.all()
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class VerifyEmailViewAPI(APIView):
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'code'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
                'code': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            200: openapi.Response('Email verified successfully', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'message': openapi.Schema(type=openapi.TYPE_STRING)})),
            400: 'Invalid verification code',
            404: 'Profile not found'
        },
        operation_description="Verify email using the verification code"
    )
    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")
        try:
            profile = Profile.objects.get(user__email=email)
            if profile.verification_code == code:
                profile.email_verified = True
                profile.verification_code = None
                profile.user.is_active = True 
                profile.user.save()
                profile.save()
                return Response({"message": "Email verified successfully! Registration completed."}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid verification code."}, status=status.HTTP_400_BAD_REQUEST)
        except Profile.DoesNotExist:
            return Response({"error": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)


class RegisterAPIView(APIView):
    """API View to register a new profile."""

    @swagger_auto_schema(
        request_body=ProfileSerializer,
        responses={
            201: ProfileSerializer,
            400: 'Bad Request',
        },
        operation_description="Register a new user profile."
    )
    def post(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Handles POST request to create a new profile."""
        serializer = ProfileSerializer(data=request.data)

        if serializer.is_valid():
            profile = serializer.save()  
            send_verification_email(profile)  
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
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format='password'),
            }
        ),
        responses={
            200: openapi.Response('Successful login', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'user': openapi.Schema(type=openapi.TYPE_OBJECT,
                                           properties={
                                               'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                               'username': openapi.Schema(type=openapi.TYPE_STRING),
                                               'email': openapi.Schema(type=openapi.TYPE_STRING),
                                               'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                                               'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                                           }),
                    'access': openapi.Schema(type=openapi.TYPE_STRING),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )),
            400: 'Username and password are required',
            401: 'Invalid credentials',
        },
        operation_description="Authenticate user and return JWT tokens"
    )
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
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh_token'],
            properties={
                'refresh_token': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response('Logout successful', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'message': openapi.Schema(type=openapi.TYPE_STRING)})),
            400: 'Bad Request',
        },
        operation_description="Logout user by blacklisting refresh token"
    )
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

    @swagger_auto_schema(
        responses={
            200: openapi.Response('Follow success', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'detail': openapi.Schema(type=openapi.TYPE_STRING)})),
            400: 'Bad Request',
            404: 'Not Found'
        },
        operation_description="Follow another user by username"
    )
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

    @swagger_auto_schema(
        responses={
            200: openapi.Response('Unfollow success', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'detail': openapi.Schema(type=openapi.TYPE_STRING)})),
            400: 'Bad Request',
            404: 'Not Found'
        },
        operation_description="Unfollow another user by username"
    )
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

    @swagger_auto_schema(
        responses={
            200: openapi.Response('List of followers', ProfileSerializer(many=True)),
            404: 'Not Found'
        },
        operation_description="List profiles following the specified user"
    )
    def get(self, request: HttpRequest, user_name: str, format=None) -> Response:
        profile = get_object_or_404(Profile, user__username=user_name)
        follower_users = profile.followers.all()
        follower_profiles = Profile.objects.filter(user__in=follower_users)
        follower_serializer = ProfileSerializer(follower_profiles, many=True)
        return Response({"Followers": follower_serializer.data}, status=status.HTTP_200_OK)
            
            
class ProfileFollowingsListAPIView(APIView):
    """Returns a list of profiles followed by the specified profile."""
    permission_classes = [CanManageObjectPermission]

    @swagger_auto_schema(
        responses={
            200: openapi.Response('List of followings', ProfileSerializer(many=True)),
            404: 'Not Found'
        },
        operation_description="List profiles followed by the specified user"
    )
    def get(self, request: HttpRequest, user_name: str, format=None) -> Response:
        profile = get_object_or_404(Profile, user__username=user_name)
        following_profiles = profile.user.followings.all()
        following_serializer = ProfileSerializer(following_profiles, many=True, context={"request": request})
        return Response({"Following": following_serializer.data}, status=status.HTTP_200_OK)
    

class ProfileDetailView(APIView):
    """API for retrieving user profile details."""
    permission_classes = [CanManageObjectPermission]
    
    @swagger_auto_schema(
        responses={200: ProfileSerializer, 404: 'Not Found'},
        operation_description="Get user profile details by username"
    )
    def get(self, request: HttpRequest, user_name: str) -> Response:
        profile = get_object_or_404(Profile, user__username=user_name)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        request_body=ProfileSerializer,
        responses={
            200: ProfileSerializer,
            400: 'Bad Request',
            403: 'Forbidden',
            404: 'Not Found'
        },
        operation_description="Partially update user profile details"
    )
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
