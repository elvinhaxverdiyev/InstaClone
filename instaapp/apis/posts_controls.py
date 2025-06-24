from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404
from django.http import HttpRequest
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .paginations import Pagination
from posts.models import Post
from posts.serializers import PostCreateSerializer, PostSerializer
from likes.models import Like
from likes.serializers import LikeSerializer
from comments.models import Comment
from comments.serializers import CommentSerializer, CommentCreateSerializer
from .permissions_cotrols import CanManageObjectPermission


class PostDetailAPIView(APIView):
    """Get, update, or delete a specific post."""
    permission_classes = [CanManageObjectPermission]
    
    @swagger_auto_schema(
        operation_description="Get post details by ID",
        responses={200: PostSerializer()}
    )
    
    def get(self, request: HttpRequest, id: int) -> Response:
        """Handles GET request to fetch details of a specific post."""
        post = get_object_or_404(Post, pk=id)
        serializer = PostSerializer(post)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Partially update a post",
        request_body=PostSerializer,
        responses={200: PostSerializer()}
    )

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
    
    @swagger_auto_schema(
        operation_description="Delete a post",
        responses={204: 'No Content'}
    )

    def delete(self, request: HttpRequest, id: int) -> Response:
        """Handles DELETE request to delete a specific post."""
        post = get_object_or_404(Post, pk=id)
        self.check_object_permissions(request, post) 
        post.delete()
        return Response({
            'message': 'Post successfully deleted!'
        }, status=status.HTTP_204_NO_CONTENT)


class PostListCreateAPIView(APIView):
    """List posts from followed users or create a new post."""

    permission_classes = [CanManageObjectPermission]
    pagination_class = Pagination
    
    @swagger_auto_schema(
        operation_description="List all likes for a post",
        responses={200: openapi.Response('Likes list', LikeSerializer(many=True))}
    )

    def get(self, request: HttpRequest) -> Response:
        """Get paginated posts from followed profiles."""

        following_profiles = request.user.followings.all()
        posts = Post.objects.filter(profile__in=following_profiles).order_by("-created_at")
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(posts, request)
        serializer = PostSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Like a post",
        responses={201: LikeSerializer()}
    )
        
    def post(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Create a new post for the authenticated user."""

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
    
    @swagger_auto_schema(
        operation_description="Get all likes for a specific post",
        responses={200: openapi.Response(
            description="List of likes and like count",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'likes': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT)),
                    'likes_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                }
            )
        )}
    )
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
    
    
    @swagger_auto_schema(
        operation_description="Create a like for a specific post",
        responses={
            201: LikeSerializer(),
            400: "Already liked"
        }
    )
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

    @swagger_auto_schema(
        operation_description="Remove a like from a specific post",
        responses={
            204: "Like removed successfully",
            400: "You have not liked this post"
        }
    )
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
    @swagger_auto_schema(
        operation_summary="Get all comments",
        responses={200: CommentSerializer(many=True)},
    )

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
    @swagger_auto_schema(
        operation_summary="Get comments for a specific post",
        responses={200: CommentSerializer(many=True)},
    )

    def get(self, request: HttpRequest, post_id: int) -> Response:
        """ Retrieve all comments for a specific post """
        comments = Comment.objects.filter(post_id=post_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary="Create a comment for a specific post",
        request_body=CommentCreateSerializer,
        responses={201: CommentSerializer}
    )
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
    
    @swagger_auto_schema(
        operation_summary="Delete a comment by ID",
        manual_parameters=[
            openapi.Parameter('comment_id', openapi.IN_PATH, description="ID of the comment to delete", type=openapi.TYPE_INTEGER)
        ],
        responses={
            204: openapi.Response(description="Comment deleted"),
            403: "You are not authorized to delete this comment",
            404: "Comment not found"
        }
    )
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
    
    @swagger_auto_schema(
        operation_summary="Like a comment",
        manual_parameters=[
            openapi.Parameter('comment_id', openapi.IN_PATH, description="ID of the comment to like", type=openapi.TYPE_INTEGER)
        ],
        responses={
            201: openapi.Response("Like added", CommentSerializer),
            400: "Already liked"
        }
    )
    def post(self, request: HttpRequest, comment_id: int) -> Response:
        """Creates a like for a comment if not already liked."""
        comment = get_object_or_404(Comment, id=comment_id)
        if Like.objects.filter(profile=request.user.profile, comment=comment).exists():
            return Response({"message": "You have already liked this comment"}, status=status.HTTP_400_BAD_REQUEST)
            
        Like.objects.create(profile=request.user.profile, comment=comment)
        serializer = CommentSerializer(comment)

        return Response({"message": "Like added","comment": serializer.data}, status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(
        operation_summary="Unlike a comment",
        manual_parameters=[
            openapi.Parameter('comment_id', openapi.IN_PATH, description="ID of the comment to unlike", type=openapi.TYPE_INTEGER)
        ],
        responses={
            200: "Like removed",
            400: "You have not liked this comment"
        }
    )
    def delete(self, request: HttpRequest, comment_id: int) -> Response:
        """Removes a like from a comment if it exists."""
        comment = get_object_or_404(Comment, id=comment_id)

        like = Like.objects.filter(profile=request.user.profile, comment=comment).first()

        if not like:
            return Response({"message": "You have not liked this comment"}, status=status.HTTP_400_BAD_REQUEST)

        like.delete()
        return Response({"message": "Like removed"}, status=status.HTTP_200_OK)
