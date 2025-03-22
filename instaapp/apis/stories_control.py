from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from posts.models import Story
from posts.serializers import StoryCreateSerializer, StorySerializer

class StoryManagmentAPIView(APIView):
    """API view for retrieving and creating stories."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve all stories ordered by creation date (newest first)."""
        stories = Story.objects.all().order_by("-created_at")  
        serializer = StorySerializer(stories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Create a new story for the authenticated user."""
        serializer = StoryCreateSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)