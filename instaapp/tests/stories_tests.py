from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from posts.models import Story
from likes.models import Like
from django.urls import reverse
from datetime import timedelta
from django.utils import timezone

User = get_user_model()


class StoryAPIViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", password="password123")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.story = Story.objects.create(
            user=self.user,
            image="stories/test.jpg", 
            created_at=timezone.now()
        )

    def test_get_story(self):
        url = reverse('story-detail', kwargs={'story_id': self.story.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.story.id)

    def test_create_story(self):
        url = reverse('story-list')
        data = {
            "image": "stories/new_image.jpg"  
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_story(self):
        url = reverse('story-detail', kwargs={'story_id': self.story.id})
        data = {
            "image": "stories/updated.jpg"
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['story']['image'], "stories/updated.jpg")

    def test_delete_story(self):
        url = reverse('story-detail', kwargs={'story_id': self.story.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Story.objects.filter(id=self.story.id).exists())

    def test_like_story(self):
        url = reverse('story-like', kwargs={'story_id': self.story.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.filter(story=self.story, profile=self.user.profile).count(), 1)

    def test_unlike_story(self):
        Like.objects.create(story=self.story, profile=self.user.profile)
        url = reverse('story-like', kwargs={'story_id': self.story.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Like.objects.filter(story=self.story, profile=self.user.profile).count(), 0)
