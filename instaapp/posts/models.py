from django.db import models
from profiles.models import Profile


class Post(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="posts")
    caption = models.CharField(max_length=2000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="images/", null=True, blank=True)
    video = models.FileField(upload_to="videos/", null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}: {self.caption[:20]}"