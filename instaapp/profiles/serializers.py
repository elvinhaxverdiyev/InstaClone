from rest_framework import serializers
from django.contrib.auth.models import User

from profiles.models import Profile


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.

    This serializer is used to convert a User object into JSON format, and vice versa.
    It includes basic fields such as `username`, `email`, `first_name`, `last_name`, and `date_joined`.

    Fields:
        id (int): The unique ID of the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        first_name (str): The user's first name.
        last_name (str): The user's last name.
        date_joined (datetime): The date the user joined.
    """
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
    """
    Serializer for the Profile model.

    This serializer is used to convert a Profile object into JSON format, and vice versa.
    It also allows the creation and updating of the associated User object.
    The serializer includes user-related fields (username, email, password, etc.) and profile-specific fields.

    Fields:
        user (UserSerializer): The associated User object.
        followers (PrimaryKeyRelatedField): List of users who follow this profile.
        followers_count (int): The number of followers the profile has.
        following_count (int): The number of users this profile is following.
        profile_picture (ImageField): The profile picture of the user.
        bio (str): The biography of the user.
        website_link (str): The website link associated with the profile.
        created_at (datetime): The timestamp when the profile was created.
        username (str): The username of the associated User.
        email (str): The email address of the associated User.
        password (str): The password of the associated User (write-only).
        first_name (str): The first name of the associated User.
        last_name (str): The last name of the associated User.
    """
    username = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(write_only=True, required=True)
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        required=True,
        allow_blank=False  
    )
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    user = UserSerializer(read_only=True)
    followers = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.filter(is_active=True), 
        required=False
    )
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "user", "followers", "followers_count", "following_count",
            "profile_picture", "bio", "website_link", "created_at",
            "username", "email", "password", "first_name", "last_name"
        ]

    def get_followers_count(self, obj) -> int:
        """
        Returns the number of followers of a profile.

        Args:
            obj (Profile): The profile instance.

        Returns:
            int: The number of followers.
        """
        return obj.followers.count()

    def get_following_count(self, obj) -> bool:
        """
        Returns the number of users the profile is following.

        Args:
            obj (Profile): The profile instance.

        Returns:
            int: The number of followings.
        """
        return obj.user.followings.count()

    def validate_password(self, value):
        """
        Validates the password field to ensure it's not empty.

        Args:
            value (str): The password value.

        Returns:
            str: The validated password value.

        Raises:
            ValidationError: If the password is empty.
        """
        if value == "":
            raise serializers.ValidationError("Password cannot be empty.")
        return value

    def validate(self, attrs):
        """
        Validates the unique constraints for username and email.

        Args:
            attrs (dict): The validated data.

        Returns:
            dict: The validated attributes.

        Raises:
            ValidationError: If the username or email is already taken.
        """
        username = attrs.get("username")
        email = attrs.get("email")
        instance = getattr(self, "instance", None) 
        if username and User.objects.exclude(pk=instance.user.pk if instance else None).filter(username=username).exists():
            raise serializers.ValidationError({"username": "This username is already taken."})
        if email and User.objects.exclude(pk=instance.user.pk if instance else None).filter(email=email).exists():
            raise serializers.ValidationError({"email": "This email is already registered."})

        return attrs

    def create(self, validated_data):
        """
        Creates a new Profile instance along with the associated User instance.

        Args:
            validated_data (dict): The validated data for the profile.

        Returns:
            Profile: The newly created profile.
        """
        username = validated_data.pop("username")
        email = validated_data.pop("email")
        password = validated_data.pop("password")
        first_name = validated_data.pop("first_name", "")
        last_name = validated_data.pop("last_name", "")
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=False
        )

        profile = Profile.objects.create(user=user, **validated_data)
        return profile

    def update(self, instance, validated_data):
        """
        Updates an existing Profile instance and its associated User instance.

        Args:
            instance (Profile): The instance of the profile to update.
            validated_data (dict): The validated data to update the profile.

        Returns:
            Profile: The updated profile instance.
        """
        user_updated = False
        if "password" in validated_data:
            instance.user.set_password(validated_data.pop("password"))
            user_updated = True
        if "first_name" in validated_data:
            instance.user.first_name = validated_data.pop("first_name")
            user_updated = True
        if "last_name" in validated_data:
            instance.user.last_name = validated_data.pop("last_name")
            user_updated = True
        if "email" in validated_data:
            instance.user.email = validated_data.pop("email")
            user_updated = True
        if "username" in validated_data:
            instance.user.username = validated_data.pop("username")
            user_updated = True
        if user_updated:
            instance.user.save()

        profile_fields = ["followers", "profile_picture", "bio", "website_link"]
        for field in profile_fields:
            if field in validated_data:
                setattr(instance, field, validated_data.pop(field))

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance