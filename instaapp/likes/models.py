from django.apps import apps
from django.db import models
from profiles.models import Profile

class Like(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="likes")
    comment = models.ForeignKey("comments.Comment", on_delete=models.CASCADE, related_name="comment_likes", null=True, blank=True)
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, related_name="post_likes", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.comment:
            return f"{self.profile.user.username} liked comment {self.comment.id}"
        return f"{self.profile.user.username} liked post {self.post.title}"

    @classmethod
    def get_post_model(cls):
        return apps.get_model("posts", "Post")

    @classmethod
    def get_comment_model(cls):
        return apps.get_model("comments", "Comment")
