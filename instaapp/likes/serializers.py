from rest_framework import serializers
from .models import Like

class LikeSerializer(serializers.ModelSerializer):
    """
    Serializer for the Like model, converting Like instances to and from JSON format.

    **Fields:**
    - `profile`: The user profile who liked the content (represented as a string).
    - `post_title`: The title of the liked post (only available if the like is related to a post).
    - `post_content`: The content of the liked post (only available if the like is related to a post).
    - `comment_id`: The ID of the liked comment (only available if the like is related to a comment).
    - `comment_text`: The text of the liked comment (only available if the like is related to a comment).
    - `created_at`: The timestamp when the like was created (read-only).

    **Usage:**
    - Serializes data from the Like model for API responses.
    - Deserializes incoming data for creating or updating like instances.
    """
    profile = serializers.StringRelatedField()  
    post_title = serializers.CharField(source="post.title", read_only=True)
    post_content = serializers.CharField(source="post.content", read_only=True) 
    comment_id = serializers.IntegerField(source="comment.id", read_only=True)  
    comment_text = serializers.CharField(source="comment.text", read_only=True) 

    class Meta:
        model = Like
        fields = [
            "profile",
            "post",
            "post_title",
            "post_content",
            "comment_id",
            "comment_text",
            "created_at"
        ]
        
        read_only_fields = ["created_at"] 
