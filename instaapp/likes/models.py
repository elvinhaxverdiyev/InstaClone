from django.db import models
from profiles.models import Profile

class Like(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, related_name="post_likes") 
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")

    def __str__(self):
        return f"{self.user.username} liked post {self.post.title}"
