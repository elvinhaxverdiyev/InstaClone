from rest_framework import serializers
from .models import Post, Story
from profiles.models import Profile
from likes.models import Like
from hashtags.models import HashTag

def add_hashtags_to_post(post, hashtags_data):
    """
    Adds hashtags to a post by processing the input hashtag string.

    Args:
        post (Post): The post to which the hashtags will be added.
        hashtags_data (str): A comma-separated string of hashtags to be associated with the post.

    Returns:
        None
    """
    if hashtags_data:
        hashtag_names = [name.strip() for name in hashtags_data.split(",")]
        for name in hashtag_names:
            if name:
                hashtag, created = HashTag.objects.get_or_create(name=name)
                post.hashtags.add(hashtag)
                

class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for Post model, used to serialize a Post instance.

    This serializer handles the inclusion of hashtags as a string and includes the 
    like count and hashtag list as additional fields.
    """
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
        """
        Returns the count of likes associated with the post.

        Args:
            obj (Post): The post instance.

        Returns:
            int: The number of likes for the post.
        """
        return obj.get_likes_count()
    
    def get_hashtag_list(self, obj):
        """
        Returns a list of hashtags associated with the post.

        Args:
            obj (Post): The post instance.

        Returns:
            list: A list of hashtag names associated with the post.
        """
        return [hashtag.name for hashtag in obj.hashtags.all()]
    
    def create(self, validated_data):
        """
        Creates a new Post instance, including processing hashtags.

        Args:
            validated_data (dict): The validated data from the serializer.

        Returns:
            Post: The created Post instance.
        """
        hashtags_data = validated_data.pop("hashtags", None)
        post = Post.objects.create(**validated_data)
        add_hashtags_to_post(post, hashtags_data)
        return post


class PostCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new Post instance.

    This serializer handles post creation without retrieving the `likes_count` or `hashtag_list`.
    It also processes hashtags and assigns them to the post during creation.
    """
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
        """
        Creates a new Post instance and associates it with the current user.

        Args:
            validated_data (dict): The validated data from the serializer.

        Returns:
            Post: The created Post instance.
        """
        user = self.context["request"].user
        hashtags_data = validated_data.pop("hashtags", None) 
        post = Post.objects.create(profile=user.profile, **validated_data)
        if hashtags_data:  
            add_hashtags_to_post(post, hashtags_data)
        return post
    

class StorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Story model, used to serialize a Story instance.

    This serializer includes fields like `likes_count` and `is_liked` to indicate
    whether the current user has liked the story.
    """
    user = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all())
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = "__all__"
        
    def get_likes_count(self, obj):
        """
        Returns the count of likes for the story.

        Args:
            obj (Story): The story instance.

        Returns:
            int: The number of likes for the story.
        """
        return Like.objects.filter(story=obj).count()
    
    def get_is_liked(self, obj):
        """
        Checks if the current user has liked the story.

        Args:
            obj (Story): The story instance.

        Returns:
            bool: True if the current user has liked the story, False otherwise.
        """
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            profile = request.user.profile
            return Like.objects.filter(story=obj, profile=profile).exists()
        return False

class StoryCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new Story instance.

    This serializer allows creating a story with either an image or a video.
    It also validates that both an image and video cannot be included in the same story.
    """
    
    class Meta:
        model = Story
        fields = ["caption", "image", "video"] 

    def create(self, validated_data):
        """
        Creates a new Story instance and schedules its deletion after 24 hours.

        Args:
            validated_data (dict): The validated data from the serializer.

        Returns:
            Story: The created Story instance.
        """
        user = self.context["request"].user.profile
        story = Story.objects.create(user=user, **validated_data)
        story.delete_after_24_hours()
        return story
    
    def validate(self, data):
        """
        Validates the story creation data to ensure it has either an image or video, but not both.

        Args:
            data (dict): The validated data from the serializer.

        Raises:
            serializers.ValidationError: If both an image and video are included.
        
        Returns:
            dict: The validated data.
        """
        if data.get("image") and data.get("video"):
            raise serializers.ValidationError("Both an image and a video cannot be added.")
        return data