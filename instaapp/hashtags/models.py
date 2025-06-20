from django.db import models


class HashTag(models.Model):
    """Represents a unique hashtag used in posts."""

    name = models.CharField(max_length=50, unique=True)
    
    
    def __str__(self) -> str:
        """Returns the string representation of the hashtag."""
        return self.name


