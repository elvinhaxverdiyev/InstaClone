from django.db import models
from profiles.models import Profile
from likes.models import Like

class Post(models.Model):
    profile = models.ForeignKey(Profile, related_name="posts", on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default='Untitled Post')    
    content = models.TextField(default='No content provided')  
    image = models.ImageField(upload_to="post_images/", null=True, blank=True)
    video = models.FileField(upload_to="post_videos/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(Profile, through=Like, related_name="liked_posts")
    
    def __str__(self):
        return self.title

    def get_likes_count(self):
        return self.likes.count()

    def has_image(self):
        return bool(self.image)
