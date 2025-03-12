from rest_framework import serializers
from django.contrib.auth.models import User
from profiles.models import Profile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "date_joined"
            ]


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    user = UserSerializer(read_only=True)

    followers = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "user", "followers", "followers_count", "following_count",
            "profile_picture", "bio", "website_link", "created_at",
            "username", "email", "password", "first_name", "last_name"
        ]

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.user.following.count()

    def validate(self, attrs):
        username = attrs.get("username")
        email = attrs.get("email")
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "This username is already taken."})
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "This email is already registered."})
        if not attrs.get("password"):
            raise serializers.ValidationError({"password": "This field is required."})
        return attrs

    def create(self, validated_data):
        user_data = {
            "username": validated_data.pop("username"),
            "email": validated_data.pop("email"),
            "password": validated_data.pop("password"),
            "first_name": validated_data.pop("first_name", ""),
            "last_name": validated_data.pop("last_name", "")
        }

        user = User.objects.create_user(**user_data)
        followers_data = validated_data.pop("followers", None)
        profile = Profile.objects.create(user=user, **validated_data)

        if followers_data is not None:
            profile.followers.set(followers_data)

        return profile