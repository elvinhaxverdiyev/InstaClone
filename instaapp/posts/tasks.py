from celery import shared_task
from posts.models import Story

@shared_task
def delete_story_after_24_hours(story_id):
    try:
        story = Story.objects.get(id=story_id)
        story.delete()
    except Story.DoesNotExist:
        pass  