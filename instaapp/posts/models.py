from django.db import models
from django.utils.timezone import now
from datetime import timedelta

from profiles.models import Profile
from likes.models import Like
from hashtags.models import HashTag


class Post(models.Model):
    profile = models.ForeignKey(Profile, related_name="posts", on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default='Untitled Post')    
    content = models.TextField(default='No content provided')  
    image = models.ImageField(upload_to="media/", null=True, blank=True)
    video = models.FileField(upload_to="media/", null=True, blank=True)
    hashtags = models.ManyToManyField(HashTag, related_name="post_hashtag", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(Profile, through=Like, related_name="liked_posts")
    
    def __str__(self):
        return self.title

    def get_likes_count(self):
        return self.likes.count()

    def has_image(self):
        return bool(self.image)
    

class Story(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="stories")
    caption = models.CharField(max_length=2200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="media/", null=True, blank=True)
    video = models.FileField(upload_to="media/", null=True, blank=True)

    def __str__(self):
        return f"{self.user.user.username}: {self.caption[:20]}"  

    def save(self, *args, **kwargs):
        is_new = self.id is None
        super().save(*args, **kwargs) 
        if is_new: 
            self.delete_after_24_hours()

    def delete_after_24_hours(self):
        from posts.tasks import delete_story_after_24_hours
        delete_story_after_24_hours.apply_async(
            args=[self.id],
            eta=self.created_at + timedelta(hours=24) 
        )

    @classmethod
    def visible_stories(cls):
        return cls.objects.filter(created_at__gte=now() - timedelta(hours=24))