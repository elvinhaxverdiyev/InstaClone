from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    """
    Profile model representing additional user information.

    This model extends the base `User` model to store additional data like:
    - Profile picture
    - Bio
    - Website link
    - Followers (Many-to-Many relationship with the `User` model)

    Attributes:
        user (OneToOneField): A one-to-one relationship with the User model.
        followers (ManyToManyField): Users who follow this profile.
        profile_picture (ImageField): The profile picture of the user.
        bio (CharField): A short biography for the user.
        website_link (URLField): A URL field for the user's personal or professional website.
        created_at (DateTimeField): The timestamp when the profile was created.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    followers = models.ManyToManyField(User, related_name="followings", symmetrical=False, blank=True)
    profile_picture = models.ImageField(upload_to="media/", null=True, blank=True)
    bio = models.CharField(max_length=150, null=True, blank=True)
    website_link = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        """
        String representation of the Profile model.

        Returns:
            str: The username of the associated User model.
        """
        return self.user.username


