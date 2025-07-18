from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import HttpRequest
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .permissions_cotrols import CanManageObjectPermission
from posts.models import Story
from posts.serializers import StoryCreateSerializer, StorySerializer
from likes.models import Like


class StoryManagmentAPIView(APIView):
    """API view for retrieving a single story."""
    permission_classes = [CanManageObjectPermission]
    
    @swagger_auto_schema(
        operation_summary="Hekayəni əldə et",
        responses={200: StorySerializer()},
        manual_parameters=[
            openapi.Parameter('story_id', openapi.IN_PATH, description="Hekayə ID-si", type=openapi.TYPE_INTEGER)
        ]
    )
    def get(self, request: HttpRequest, story_id: int) -> Response:
        """Handle GET request to retrieve a story by ID."""
        story = get_object_or_404(Story, id=story_id)
        serializer = StorySerializer(story, context={"request": request})  
        return Response(serializer.data, status=status.HTTP_200_OK)
  
    @swagger_auto_schema(
        operation_summary="Yeni hekayə yarat",
        request_body=StoryCreateSerializer,
        responses={201: StorySerializer()}
    )
    def post(self, request: HttpRequest) -> Response:
        """Create a new story for the authenticated user."""
        serializer = StoryCreateSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_summary="Hekayəni yenilə",
        request_body=StoryCreateSerializer,
        responses={200: StorySerializer()},
        manual_parameters=[
            openapi.Parameter('story_id', openapi.IN_PATH, description="Yenilənəcək hekayənin ID-si", type=openapi.TYPE_INTEGER)
        ]
    )
    def patch(self, request: HttpRequest, story_id: int) -> Response:
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
    
    @swagger_auto_schema(
        operation_summary="Hekayəni sil",
        responses={204: 'Silinib'},
        manual_parameters=[
            openapi.Parameter('story_id', openapi.IN_PATH, description="Silinəcək hekayənin ID-si", type=openapi.TYPE_INTEGER)
        ]
    )
    def delete(self, request: HttpRequest, story_id: int) -> Response:
        """Delete a specific story."""
        story = get_object_or_404(Story, id=story_id)
        story.delete()
        return Response(
            {"message": "The story deleted successfuly"},
            status=status.HTTP_204_NO_CONTENT
        )
        
        
class StoryLikeAPIView(APIView):
    """API view to handle liking and unliking stories."""
    permission_classes = [CanManageObjectPermission] 

    @swagger_auto_schema(
        operation_summary="Hekayəni bəyən",
        responses={201: StorySerializer()},
        manual_parameters=[
            openapi.Parameter('story_id', openapi.IN_PATH, description="Bəyəniləcək hekayənin ID-si", type=openapi.TYPE_INTEGER)
        ]
    )
    def post(self, request: HttpRequest, story_id: int) -> Response:
        """Handle POST request to like a specific story."""
        
        story = get_object_or_404(Story, id=story_id)
        profile = request.user.profile
        if Like.objects.filter(story=story, profile=profile).exists():
            return Response({"message": "You have already liked this story!"}, status=status.HTTP_400_BAD_REQUEST)

        Like.objects.create(profile=profile, story=story)
        likes_count = Like.objects.filter(story=story).count()
        serializer = StorySerializer(story, context={"request": request})
        return Response({
            "message": "Story liked successfully!",
            "story": serializer.data,
            "likes_count": likes_count
        }, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="Hekayəyə qoyulan bəyənməni sil",
        responses={200: StorySerializer()},
        manual_parameters=[
            openapi.Parameter('story_id', openapi.IN_PATH, description="Bəyənməsi silinəcək hekayənin ID-si", type=openapi.TYPE_INTEGER)
        ]
    )
    def delete(self, request: HttpRequest, story_id: int) -> Response:
        """Handle DELETE request to unlike a specific story."""
        story = get_object_or_404(Story, id=story_id)
        profile = request.user.profile
        like = Like.objects.filter(story=story, profile=profile).first()
        if like:
            like.delete()
            likes_count = Like.objects.filter(story=story).count()
            serializer = StorySerializer(story, context={"request": request})

            return Response({
                "message": "Story unliked successfully!",
                "story": serializer.data,
                "likes_count": likes_count
            }, status=status.HTTP_200_OK)

        return Response({"message": "You haven't liked this story!"}, status=status.HTTP_400_BAD_REQUEST)