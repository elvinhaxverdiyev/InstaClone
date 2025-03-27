from celery import shared_task
from posts.models import Story

@shared_task
def delete_story_after_24_hours(story_id):
    """
    A Celery task to delete a story from the database 24 hours after it was created.

    Args:
        story_id (int): The ID of the story to be deleted.

    This task is triggered by the `Story` model's `save` method and is scheduled 
    to run 24 hours after the story is created.
    """
    try:
        story = Story.objects.get(id=story_id)
        story.delete()
    except Story.DoesNotExist:
        pass  