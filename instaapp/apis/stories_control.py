from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .permissions_cotrols import CanManageObjectPermission
from posts.models import Story
from posts.serializers import StoryCreateSerializer, StorySerializer


class StoryManagmentAPIView(APIView):
    """API view for retrieving and creating stories."""
    permission_classes = [CanManageObjectPermission]

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
    
    def patch(self, request, story_id):
        """Handle PATCH request to partially update a specific story."""
        story = get_object_or_404(Story, id=story_id)
        serializer = StoryCreateSerializer(story, data=request.data, partial=True, context={"request": request})

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Story successfully updated!",
                "story": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)