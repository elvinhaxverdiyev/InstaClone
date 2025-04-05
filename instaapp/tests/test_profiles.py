import json
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from profiles.models import Profile


class RegisterAPIViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/register/"

    def test_register_success(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "strongpassword123"
        }
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.json()
        self.assertIn("user", response_data)
        self.assertIn("access", response_data)
        self.assertIn("refresh", response_data)
        self.assertTrue(Profile.objects.filter(user__email="test@example.com").exists())
        print("OK")  

    def test_register_invalid_data(self):
        data = {
            "username": "testuser",
            "password": "strongpassword123"
        }
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertIn("email", response_data)
        print("OK") 