from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404

from posts.models import Post
from posts.serializers import PostCreateSerializer, PostSerializer
from profiles.models import Profile
from profiles.serializers import ProfileSerializer


class ProfileListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        profiles = Profile.objects.all()  
        serializer = ProfileSerializer(profiles, many=True)  
        return Response(serializer.data, status=status.HTTP_200_OK) 


class RegisterAPIView(APIView):
    def post(self, request):
        profile_data = request.data
        serializer = ProfileSerializer(data=profile_data)
        if serializer.is_valid():
            profile = serializer.save()
            return Response(ProfileSerializer(profile).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailAPIView(APIView):
    def get(self, request, id):
        
        post = get_object_or_404(Post, pk=id)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    def patch(self, request, id):
        post = get_object_or_404(Post, pk=id)
        serializer = PostCreateSerializer(post, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Post successfully updated!',
                'post': serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        post = get_object_or_404(Post, pk=id)
        post.delete()
        return Response({
            'message': 'Post successfully deleted!'
        }, status=status.HTTP_204_NO_CONTENT)


class PostListCreateAPIView(APIView):
    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        serializer = PostCreateSerializer(data=request.data)

        if serializer.is_valid():
            post = serializer.save()
            return Response({
                "message": "Post successfully created!",
                "post": PostSerializer(post).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

