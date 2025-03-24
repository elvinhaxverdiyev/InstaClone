from rest_framework import serializers
from .models import Post, Story
from profiles.models import Profile
from likes.models import Like


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
    

class StorySerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all())
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = "__all__"
        
    def get_likes_count(self, obj):
        return Like.objects.filter(story=obj).count()
    
    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            profile = request.user.profile
            return Like.objects.filter(story=obj, profile=profile).exists()
        return False

class StoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ["caption", "image", "video"] 

    def create(self, validated_data):
        user = self.context["request"].user.profile
        story = Story.objects.create(user=user, **validated_data)
        story.delete_after_24_hours()
        return story
    
    def validate(self, data):
        if data.get("image") and data.get("video"):
            raise serializers.ValidationError("Both an image and a video cannot be added.")
        return data