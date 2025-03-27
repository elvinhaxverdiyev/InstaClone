from django.db import models
from posts.models import Post
from profiles.models import Profile
from likes.models import Like

class Comment(models.Model):
    """
    Model representing comments on posts.

    **Fields:**
    - `user`: The profile of the user who wrote the comment.
    - `post`: The post on which the comment is made.
    - `text`: The content of the comment (max 2200 characters).
    - `created_at`: The timestamp when the comment was created.

    **Related Names:**
    - `comments` on `Profile`: Allows reverse lookup to get all comments by a user.
    - `comments` on `Post`: Allows reverse lookup to get all comments on a post.
    """
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    text = models.CharField(max_length=2200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """
        Returns a string representation of the comment.

        **Format:** `<username> <first 20 characters of comment>`
        """
        return f"{self.user.user.username} {self.text[:20]}"

    @property
    def like_count(self) -> int:
        """
        Returns the total number of likes on this comment.
        """
        return Like.objects.filter(comment=self).count()  

    @property
    def liked_by_users(self) -> list:
        """
        Returns a list of usernames who liked this comment.
        """
        return [like.profile.user.username for like in Like.objects.filter(comment=self)]


