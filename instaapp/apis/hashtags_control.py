from rest_framework.views import APIView, status
from rest_framework.response import Response
from django.shortcuts import get_list_or_404, get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .permissions_cotrols import CanManageObjectPermission
from posts.models import Post
from hashtags.models import HashTag
from posts.serializers import PostSerializer
from hashtags.serializers import HashTagSerializer


class HashTagListAPIView(APIView):
    """
    API view for listing all hashtags.

    Permissions:
        - Custom permission: CanManageObjectPermission

    Returns:
        - 200 OK: List of all hashtags
        - 404 Not Found: If no hashtags are found
    """
    permission_classes = [CanManageObjectPermission]
    
    @swagger_auto_schema(
        operation_description="Retrieve the list of all hashtags",
        responses={200: HashTagSerializer(many=True)},
    )
    def get(self, request):
        hashtags = get_list_or_404(HashTag)
        seralizer = HashTagSerializer(hashtags, many=True)
        return Response(seralizer.data, status=status.HTTP_200_OK)
    
    
class HashtagsPostListAPIView(APIView):
    """
    API view for retrieving posts associated with a specific hashtag.

    Permissions:
        - Custom permission: CanManageObjectPermission

    Path Parameters:
        - hashtag_name (str): The name of the hashtag

    Returns:
        - 200 OK: List of posts associated with the hashtag
        - 404 Not Found: If the hashtag or posts are not found
    """
    permission_classes = [CanManageObjectPermission]
    @swagger_auto_schema(
        operation_description="Retrieve all posts related to a hashtag",
        manual_parameters=[
            openapi.Parameter(
                'hashtag_name', openapi.IN_PATH, 
                description="Name of the hashtag",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={200: PostSerializer(many=True)},
    )

    def get(self, request, hashtaq_name):
        hashtag = get_object_or_404(HashTag, name=hashtaq_name)
        posts = get_list_or_404(Post, hashtags=hashtag)  
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)