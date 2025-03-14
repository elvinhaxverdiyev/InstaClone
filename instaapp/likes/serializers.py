from rest_framework import serializers
from .models import Like

class LikeSerializer(serializers.ModelSerializer):
    profile = serializers.StringRelatedField() 
    post_title = serializers.CharField(source="post.title", read_only=True) 
    post_content = serializers.CharField(source="post.content", read_only=True)  
    
    class Meta:
        model = Like
        fields = [
            "profile",
            "post",
            "post_title",
            "post_content",
            "created_at"
            ]
        
        read_only_fields = ["created_at"]
