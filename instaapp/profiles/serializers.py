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
    username = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(write_only=True, required=False)
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        required=False,
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

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.user.followings.count()

    def validate_password(self, value):
        if value == "":
            raise serializers.ValidationError("Password cannot be empty.")
        return value

    def validate(self, attrs):
        username = attrs.get("username")
        email = attrs.get("email")
        instance = getattr(self, "instance", None) 
        if username and User.objects.exclude(pk=instance.user.pk if instance else None).filter(username=username).exists():
            raise serializers.ValidationError({"username": "This username is already taken."})
        if email and User.objects.exclude(pk=instance.user.pk if instance else None).filter(email=email).exists():
            raise serializers.ValidationError({"email": "This email is already registered."})

        return attrs

    def create(self, validated_data):
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
            last_name=last_name
        )

        profile = Profile.objects.create(user=user, **validated_data)
        return profile

    def update(self, instance, validated_data):
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