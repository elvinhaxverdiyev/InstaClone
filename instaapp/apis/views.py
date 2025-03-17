from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import get_object_or_404

from posts.models import Post
from posts.serializers import PostCreateSerializer, PostSerializer
from profiles.models import Profile
from profiles.serializers import ProfileSerializer
from likes.models import Like
from likes.serializers import LikeSerializer
from comments.models import Comment
from comments.serializers import CommentSerializer


class Pagination(PageNumberPagination):
    """Pagination class that splits the movie list into pages."""
    page_size = 2


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
        profile_data = request.data
        serializer = ProfileSerializer(data=profile_data)
        if serializer.is_valid():
            profile = serializer.save()
            return Response(ProfileSerializer(profile).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailAPIView(APIView):
    """API View to get, update, and delete a specific post."""
    
    def get(self, request, id):
        """Handles GET request to fetch details of a specific post."""
        post = get_object_or_404(Post, pk=id)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    def patch(self, request, id):
        """Handles PATCH request to update a specific post partially."""
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
        """Handles DELETE request to delete a specific post."""
        post = get_object_or_404(Post, pk=id)
        post.delete()
        return Response({
            'message': 'Post successfully deleted!'
        }, status=status.HTTP_204_NO_CONTENT)


class PostListCreateAPIView(APIView):
    """API View to list all posts and create new posts."""
    pagination_class = Pagination 
    
    def get(self, request):
        """Handles GET request to list all posts with pagination."""
        posts = Post.objects.all()
        paginator = self.pagination_class() 
        result_page = paginator.paginate_queryset(posts, request)
        
        serializer = PostSerializer(result_page, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        """Handles POST request to create a new post."""
        serializer = PostCreateSerializer(data=request.data)

        if serializer.is_valid():
            post = serializer.save()
            return Response({
                "message": "Post successfully created!",
                "post": PostSerializer(post).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LikePostAPIView(APIView):
    """API View to manage likes on posts. Allows to get, create and delete likes."""
    permission_classes = [IsAuthenticated]  
    
    def get(self, request, post_id):
        """Handles GET request to fetch all likes for a specific post."""
        post = get_object_or_404(Post, id=post_id)
        likes = Like.objects.filter(post=post)
        likes_count = likes.count() 
        serializer = LikeSerializer(likes, many=True)

        response_data = serializer.data
        response_data.append({"likes_count": likes_count})

        return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request, post_id):
        """Handles POST request to create a like for a specific post."""
        post = get_object_or_404(Post, id=post_id)
        if Like.objects.filter(post=post, profile=request.user.profile).exists():
            return Response({"message": "You have already liked this post."}, status=status.HTTP_400_BAD_REQUEST)

        like = Like.objects.create(profile=request.user.profile, post=post)
        serializer = LikeSerializer(like)
        likes_count = post.likes.count()  
        response_data = serializer.data
        response_data.append({"likes_count": likes_count})

        return Response(response_data, status=status.HTTP_201_CREATED)

    def delete(self, request, post_id):
        """Handles DELETE request to remove a like from a specific post."""
        post = get_object_or_404(Post, id=post_id)
        like = Like.objects.filter(post=post, profile=request.user.profile).first()

        if like:
            like.delete()
            likes_count = post.likes.count()  

            return Response({"message": "Like removed successfully.", "likes_count": likes_count}, status=status.HTTP_204_NO_CONTENT)

        return Response({"message": "You have not liked this post."}, status=status.HTTP_400_BAD_REQUEST)


class CommentListAPIView(APIView):
    """
    API view to retrieve all comments across all posts.
    """
    permission_classes = [IsAuthenticated]  

    def get(self, request):
        """ Retrieve all comments for all posts """
        comments = Comment.objects.all().order_by("-created_at")  
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class CommentCreateAPIView(APIView):
    """
    API view for creating and retrieving comments for a specific post.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        """ Retrieve all comments for a specific post """
        comments = Comment.objects.filter(post_id=post_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, post_id):
        """ Create a new comment for a specific post """
        data = request.data
        data["user"] = request.user.profile.id 
        data["post"] = post_id  

        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)