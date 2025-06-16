from django.db import models
from django.utils.timezone import now
from datetime import timedelta

from profiles.models import Profile
from likes.models import Like
from hashtags.models import HashTag


class Post(models.Model):
    """
    Model representing a post created by a user. The post can contain a title, content, image, 
    video, and hashtags. Users can like posts, and the post's like count can be fetched.

    **Fields:**
    - `profile`: The user who created the post (foreign key to Profile model).
    - `title`: The title of the post (defaults to 'Untitled Post').
    - `content`: The content or body of the post (defaults to 'No content provided').
    - `image`: Optional image attached to the post.
    - `video`: Optional video attached to the post.
    - `hashtags`: List of hashtags associated with the post (ManyToMany relationship with HashTag).
    - `created_at`: Timestamp when the post was created.
    - `updated_at`: Timestamp when the post was last updated.
    - `likes`: Many-to-many relationship to Profile (through Like model).

    **Methods:**
    - `get_likes_count()`: Returns the number of likes on the post.
    - `has_image()`: Returns True if the post has an attached image, False otherwise.
    """
    profile = models.ForeignKey(Profile, related_name="posts", on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default='Untitled Post')    
    content = models.TextField(default='No content provided')  
    image = models.ImageField(upload_to="media/", null=True, blank=True)
    video = models.FileField(upload_to="media/", null=True, blank=True)
    hashtags = models.ManyToManyField(HashTag, related_name="post_hashtag", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(Profile, through=Like, related_name="liked_posts")
    
    def __str__(self) -> str:
        return self.title

    def get_likes_count(self) -> int:
        """
        Returns the total number of likes the post has received.

        Returns:
            int: The number of likes.
        """
        return self.likes.count()

    def has_image(self) -> bool:
        """
        Checks if the post has an associated image.

        Returns:
            bool: True if the post has an image, False otherwise.
        """
        return bool(self.image)
    

class Story(models.Model):
    """
    Model representing a story created by a user. Stories can contain a caption, image, 
    or video, and are deleted automatically after 24 hours.

    **Fields:**
    - `user`: The user who created the story (foreign key to Profile).
    - `caption`: The caption for the story (optional).
    - `created_at`: Timestamp when the story was created.
    - `image`: Optional image attached to the story.
    - `video`: Optional video attached to the story.

    **Methods:**
    - `delete_after_24_hours()`: Schedules the story for deletion after 24 hours.
    - `visible_stories()`: Returns all stories created within the last 24 hours.
    """
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="stories")
    caption = models.CharField(max_length=2200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="media/", null=True, blank=True)
    video = models.FileField(upload_to="media/", null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.user.user.username}: {self.caption[:20]}"  

    def save(self, *args, **kwargs):
        """
        Overrides the save method to schedule story deletion after it is created.

        If the story is new (not yet saved), it schedules the deletion after 24 hours.
        """
        is_new = self.id is None
        super().save(*args, **kwargs) 
        if is_new: 
            self.delete_after_24_hours()

    def delete_after_24_hours(self):
        """
        Schedules the story for deletion after 24 hours.

        Calls the Celery task to delete the story after a 24-hour delay from the creation timestamp.
        """
        from posts.tasks import delete_story_after_24_hours
        delete_story_after_24_hours.apply_async(
            args=[self.id],
            eta=self.created_at + timedelta(hours=24) 
        )

    @classmethod
    def visible_stories(cls) -> models.QuerySet:
        """
        Returns stories created within the last 24 hours.
        Useful for displaying only currently active stories.
        """
        return cls.objects.filter(created_at__gte=now() - timedelta(hours=24))