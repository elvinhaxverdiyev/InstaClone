from django.db import models


class HashTag(models.Model):
    """
    Model representing hashtags used in posts.

    **Fields:**
    - `name` (CharField, max_length=50, unique=True): The unique name of the hashtag.

    **Methods:**
    - `__str__()`: Returns the hashtag name as a string.
    """
    name = models.CharField(max_length=50, unique=True)
    
    
    def __str__(self) -> str:
        """Returns the string representation of the hashtag."""
        return self.name


