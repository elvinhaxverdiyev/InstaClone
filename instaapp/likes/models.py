from django.apps import apps
from django.db import models
from profiles.models import Profile


class Like(models.Model):
    """
    Model representing a 'Like' action on different types of content (post, comment, story).

    **Fields:**
    - `profile` (ForeignKey): The user profile who liked the content.
    - `comment` (ForeignKey, null=True, blank=True): The comment that is liked (if applicable).
    - `post` (ForeignKey, null=True, blank=True): The post that is liked (if applicable).
    - `story` (ForeignKey, null=True, blank=True): The story that is liked (if applicable).
    - `created_at` (DateTimeField): The timestamp when the like was created.

    **Methods:**
    - `__str__()`: Returns a string representation of the like (comment, post, or story).
    - `get_post_model()`: Returns the Post model.
    - `get_comment_model()`: Returns the Comment model.
    - `get_story_model()`: Returns the Story model.
    """
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="likes")
    comment = models.ForeignKey("comments.Comment", on_delete=models.CASCADE, related_name="comment_likes", null=True, blank=True)
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, related_name="post_likes", null=True, blank=True)
    story = models.ForeignKey("posts.Story", on_delete=models.CASCADE, related_name="story_likes", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns a string representation of the like, indicating whether it's for a comment, post, or story.
        
        **Example Output:**
        - "{username} liked comment {comment_id}"
        - "{username} liked post {post_title}"
        - "{username} liked story {story_id}"
        """
        if self.comment:
            return f"{self.profile.user.username} liked comment {self.comment.id}"
        elif self.post:
            return f"{self.profile.user.username} liked post {self.post.title}"
        elif self.story:
            return f"{self.profile.user.username} liked story {self.story.id}"
        
        return f"{self.profile.user.username} liked something"
    
    @classmethod
    def get_post_model(cls):
        """
        Returns the Post model for the Like instance.
        
        **Returns:**
        - Post model class.
        """
        return apps.get_model("posts", "Post")

    @classmethod
    def get_comment_model(cls):
        """
        Returns the Comment model for the Like instance.
        
        **Returns:**
        - Comment model class.
        """
        return apps.get_model("comments", "Comment")
    
    @classmethod
    def get_story_model(cls):
        """
        Returns the Story model for the Like instance.
        
        **Returns:**
        - Story model class.
        """
        return apps.get_model("posts", "Story")
