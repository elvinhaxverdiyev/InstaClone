from rest_framework import serializers
from .models import Comment
from posts.models import Post 

class CommentSerializer(serializers.ModelSerializer):
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
            "created_at"
        ]


class CommentCreateSerializer(serializers.ModelSerializer):
    text = serializers.CharField(max_length=1000) 

    class Meta:
        model = Comment
        fields = ["text"]

    def create(self, validated_data):
        """ Assigns the authenticated user's profile to the comment before saving. """
        request = self.context.get("request", None)
        if request and request.user.is_authenticated:
            validated_data["user"] = request.user.profile
            validated_data["post"] = Post.objects.get(id=self.context["post_id"])  
            return super().create(validated_data)
        raise serializers.ValidationError({"error": "User must be authenticated to create a comment"})