from rest_framework import serializers
from .models import Post, Story
from profiles.models import Profile
from likes.models import Like
from hashtags.models import HashTag

def add_hashtags_to_post(post, hashtags_data):
    if hashtags_data:
        hashtag_names = [name.strip() for name in hashtags_data.split(",")]
        for name in hashtag_names:
            if name:
                hashtag, created = HashTag.objects.get_or_create(name=name)
                post.hashtags.add(hashtag)
                

class PostSerializer(serializers.ModelSerializer):
    hashtags = serializers.CharField(write_only=True, required=False)
    profile = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all())
    likes_count = serializers.SerializerMethodField()
    hashtag_list = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "profile",
            "title",
            "content",
            "image",
            "video",
            "hashtags",
            "hashtag_list",
            "created_at",
            "updated_at",
            "likes_count"
            ]
        
    def get_likes_count(self, obj):
        return obj.get_likes_count()
    
    def get_hashtag_list(self, obj):
        return [hashtag.name for hashtag in obj.hashtags.all()]
    
    def create(self, validated_data):
        hashtags_data = validated_data.pop("hashtags", None)
        post = Post.objects.create(**validated_data)
        add_hashtags_to_post(post, hashtags_data)
        return post


class PostCreateSerializer(serializers.ModelSerializer):
    hashtags = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Post
        fields = [
            "title",
            "content",
            "image",
            "video",
            "hashtags"
            ]
        
    def create(self, validated_data):
        user = self.context["request"].user
        hashtags_data = validated_data.pop("hashtags", None) 
        post = Post.objects.create(profile=user.profile, **validated_data)
        if hashtags_data:  
            add_hashtags_to_post(post, hashtags_data)
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