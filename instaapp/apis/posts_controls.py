from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404
from django.http import HttpRequest

from .paginations import Pagination
from posts.models import Post
from posts.serializers import PostCreateSerializer, PostSerializer
from likes.models import Like
from likes.serializers import LikeSerializer
from comments.models import Comment
from comments.serializers import CommentSerializer, CommentCreateSerializer
from .permissions_cotrols import CanManageObjectPermission


class PostDetailAPIView(APIView):
    """API View to get, update, and delete a specific post."""
    permission_classes = [CanManageObjectPermission]
    
    def get(self, request: HttpRequest, id: int) -> Response:
        """Handles GET request to fetch details of a specific post."""
        post = get_object_or_404(Post, pk=id)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    def patch(self, request: HttpRequest, id: int) -> Response:
        """Handles PATCH request to update a specific post partially."""
        post = get_object_or_404(Post, pk=id)
        serializer = PostSerializer(post, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Post successfully updated!",
                "post": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: HttpRequest, id: int) -> Response:
        """Handles DELETE request to delete a specific post."""
        post = get_object_or_404(Post, pk=id)
        self.check_object_permissions(request, post) 
        post.delete()
        return Response({
            'message': 'Post successfully deleted!'
        }, status=status.HTTP_204_NO_CONTENT)


class PostListCreateAPIView(APIView):
    """
    API view for listing posts from followed profiles and creating new posts.

    - **GET**: Returns paginated posts from profiles the authenticated user follows.
    - **POST**: Allows the authenticated user to create a new post.
    
    **Permissions:**
    - Only authenticated users can access this endpoint.
    """
    permission_classes = [CanManageObjectPermission]
    pagination_class = Pagination

    def get(self, request: HttpRequest) -> Response:
        """
        Handles GET requests to retrieve posts from followed users.
        
        **Logic:**
        1. Fetches all profiles that the authenticated user follows.
        2. Retrieves posts created by these profiles, ordered by creation date (newest first).
        3. Paginates the posts and returns a paginated response.

        **Returns:**
        - `200 OK`: Paginated list of posts.
        """
        following_profiles = request.user.followings.all()
        posts = Post.objects.filter(profile__in=following_profiles).order_by("-created_at")
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(posts, request)
        serializer = PostSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
        
    def post(self, request: HttpRequest, *args, **kwargs) -> Response:
        """
        Handles POST requests to create a new post.

        **Logic:**
        1. Validates the request data using `PostCreateSerializer`.
        2. If valid, saves the new post.
        3. Returns a success response with the created post details.

        **Returns:**
        - `201 Created`: Post successfully created.
        - `400 Bad Request`: Validation errors.
        """
        serializer = PostCreateSerializer(data=request.data, context={"request": request})

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
    
    def get(self, request: HttpRequest, post_id: int) -> Response:
        """Handles GET request to fetch all likes for a specific post."""
        post = get_object_or_404(Post, id=post_id)
        likes = Like.objects.filter(post=post)
        likes_count = likes.count() 
        serializer = LikeSerializer(likes, many=True)
        response_data = {
            "likes": serializer.data, 
            "likes_count": likes_count
            }

        return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request: HttpRequest, post_id: int) -> Response:
        """Handles POST request to create a like for a specific post."""
        post = get_object_or_404(Post, id=post_id)
        if Like.objects.filter(post=post, profile=request.user.profile).exists():
            return Response({"message": "You have already liked this post."}, status=status.HTTP_400_BAD_REQUEST)

        like = Like.objects.create(profile=request.user.profile, post=post)
        serializer = LikeSerializer(like)
        likes_count = post.likes.count()  
        response_data = {
            "like": serializer.data,  
            "likes_count": likes_count  
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

    def delete(self, request: HttpRequest, post_id: int) -> Response:
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

    def get(self, request: HttpRequest) -> Response:
        """ Retrieve all comments for all posts """
        comments = Comment.objects.all().order_by("-created_at")  
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class CommentManagmentAPIView(APIView):
    """
    API view for creating and retrieving comments for a specific post.
    """
    permission_classes = [CanManageObjectPermission]

    def get(self, request: HttpRequest, post_id: int) -> Response:
        """ Retrieve all comments for a specific post """
        comments = Comment.objects.filter(post_id=post_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: HttpRequest, post_id: int) -> Response:
        """ Create a new comment for a specific post """
        if not request.user.is_authenticated:
            return Response({"error": "User must be authenticated to create a comment"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CommentCreateSerializer(data=request.data, context={"request": request, "post_id": post_id})
        
        if serializer.is_valid():
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request: HttpRequest, comment_id: int) -> Response:
        """ Delete a specific comment if the user is the author """
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

        if comment.user == request.user.profile:
            comment.delete()
            return Response({"message": "Comment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "You are not authorized to delete this comment"}, status=status.HTTP_403_FORBIDDEN)
        

class LikeCommentAPIView(APIView):
    """API view for liking/unliking comments with authentication required."""
    
    permission_classes = [IsAuthenticated]

    def post(self, request: HttpRequest, comment_id: int) -> Response:
        """Creates a like for a comment if not already liked."""
        comment = get_object_or_404(Comment, id=comment_id)
        if Like.objects.filter(profile=request.user.profile, comment=comment).exists():
            return Response({"message": "You have already liked this comment"}, status=status.HTTP_400_BAD_REQUEST)
            
        Like.objects.create(profile=request.user.profile, comment=comment)
        serializer = CommentSerializer(comment)

        return Response({"message": "Like added","comment": serializer.data}, status=status.HTTP_201_CREATED)

    def delete(self, request: HttpRequest, comment_id: int) -> Response:
        """Removes a like from a comment if it exists."""
        comment = get_object_or_404(Comment, id=comment_id)

        like = Like.objects.filter(profile=request.user.profile, comment=comment).first()

        if not like:
            return Response({"message": "You have not liked this comment"}, status=status.HTTP_400_BAD_REQUEST)

        like.delete()
        return Response({"message": "Like removed"}, status=status.HTTP_200_OK)
