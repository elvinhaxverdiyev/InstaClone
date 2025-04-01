from rest_framework.views import APIView, status
from rest_framework.response import Response
from django.shortcuts import get_list_or_404, get_object_or_404

from .permissions_cotrols import CanManageObjectPermission
from posts.models import Post
from hashtags.models import HashTag
from posts.serializers import PostSerializer
from hashtags.serializers import HashTagSerializer


class HashTagListAPIView(APIView):
    """API view for listing the all hastags"""
    permission_classes = [CanManageObjectPermission]
    def get(self, request):
        hashtags = get_list_or_404(HashTag)
        seralizer = HashTagSerializer(hashtags, many=True)
        return Response(seralizer.data, status=status.HTTP_200_OK)
    
    
class HashtagsPostListAPIView(APIView):
    permission_classes = [CanManageObjectPermission]

    def get(self, request, hashtaq_name):
        hashtag = get_object_or_404(HashTag, name=hashtaq_name)
        posts = get_list_or_404(Post, hashtags=hashtag)  
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)