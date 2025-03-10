from django.db import models

from posts.models import Post
from profiles.models import Profile
from comments.models import Comment

# Create your models here.

class Like(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes", null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likes", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [
            ("user", "post"),
            ("user", "comment")
            ]
    
    def __str__(self):
        if self.post:
            content = "post"
        elif self.comment:
            content = "comment"
        return f"{content} liked by {self.user.username}"