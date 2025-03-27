from rest_framework import serializers
from .models import Comment
from posts.models import Post

class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving comment data.

    **Fields:**
    - `id`: Unique identifier of the comment.
    - `user`: The username of the comment's author.
    - `post`: The ID of the post associated with the comment.
    - `text`: The content of the comment.
    - `created_at`: Formatted timestamp when the comment was created.
    - `like_count`: Number of likes the comment has received.
    - `liked_by_users`: List of usernames who liked the comment.

    **Read-Only Fields:**
    - `user`
    - `created_at`
    - `like_count`
    - `liked_by_users`
    """
    user = serializers.CharField(source="user.user.username", read_only=True) 
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())  
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)  

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "post",
            "text",
            "created_at",
            "like_count", 
            "liked_by_users" 
        ]


class CommentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new comment.

    **Fields:**
    - `text`: The content of the comment (max 1000 characters).

    **Validation:**
    - Ensures the user is authenticated before creating a comment.
    - Assigns the current user’s profile to the comment.
    - Associates the comment with the specified post.
    """
    text = serializers.CharField(max_length=1000)  

    class Meta:
        model = Comment
        fields = ["text"]

    def create(self, validated_data):
        """
        Creates a new comment and associates it with the authenticated user and a post.

        **Logic:**
        1. Retrieves the current authenticated user from the request context.
        2. Ensures the user has a profile and is logged in.
        3. Associates the comment with the specified post.
        4. Saves and returns the newly created comment.

        **Raises:**
        - `ValidationError` if the user is not authenticated.

        **Returns:**
        - The created `Comment` instance.
        """
        request = self.context.get("request", None)
        if request and request.user.is_authenticated:
            validated_data["user"] = request.user.profile  
            validated_data["post"] = Post.objects.get(id=self.context["post_id"])  
            return super().create(validated_data) 
        raise serializers.ValidationError({"error": "User must be authenticated to create a comment"}) 

