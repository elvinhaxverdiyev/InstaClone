from rest_framework import serializers
from .models import Post
from profiles.models import Profile


class PostSerializer(serializers.ModelSerializer):
    profile = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all())
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = "__all__"
        
    def get_likes_count(self, obj):
        return obj.get_likes_count()


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            "title",
            "content",
            "image",
            "video"
        ]
        
    def create(self, validated_data):
        user = self.context["request"].user
        post = Post.objects.create(profile=user.profile, **validated_data)
        return post