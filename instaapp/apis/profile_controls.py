from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated


from .posts_controls import Pagination
from profiles.models import Profile
from profiles.serializers import ProfileSerializer


class ProfileListAPIView(APIView):
    """API View to list all profiles with pagination support."""
    
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