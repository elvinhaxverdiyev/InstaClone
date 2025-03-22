from django.db import models
from posts.models import Post
from profiles.models import Profile
from likes.models import Like

class Comment(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    text = models.CharField(max_length=2200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.user.username} {self.text[:20]}"

    @property
    def like_count(self):
        return Like.objects.filter(comment=self).count()  

    @property
    def liked_by_users(self):
        return [like.profile.user.username for like in Like.objects.filter(comment=self)]


