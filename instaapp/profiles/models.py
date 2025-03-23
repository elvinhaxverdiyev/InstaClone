from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    followers = models.ManyToManyField(User, related_name="followings", symmetrical=False, blank=True)
    profile_picture = models.ImageField(upload_to="media/", null=True, blank=True)
    bio = models.CharField(max_length=150, null=True, blank=True)
    website_link = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user.username


