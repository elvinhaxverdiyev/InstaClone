from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profiles")
    followers = models.ManyToManyField(User, related_name="following", symmetrical=False, blank=True)
    profile_picture = models.ImageField(upload_to="media/", null=True, blank=True)
    bio = models.CharField(max_length=150, null=True, blank=True)
    website_link = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if not self.user:  
            self.user = User.objects.create_user(username=self.user.username, email=self.user.email, password=self.user.password)
        super().save(*args, **kwargs)

