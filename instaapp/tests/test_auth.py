import json
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from profiles.serializers import ProfileSerializer
from profiles.models import Profile

User = get_user_model()

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
        

class LoginAPIViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/login/"
        self.test_user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="strongpassword123"
        )
        self.test_profile = Profile.objects.create(user=self.test_user)

    def test_login_success(self):
        """Test successful login with valid credentials and profile check."""
        data = {
            "username": "testuser",
            "password": "strongpassword123"
        }
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertIn("access", response_data)
        self.assertIn("refresh", response_data)
        self.assertTrue(Profile.objects.filter(user=self.test_user).exists())
        print("OK: Successful login with profile")

    def test_login_invalid_password(self):
        """Test login with incorrect password."""
        data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response_data = response.json()
        self.assertIn("error", response_data)  
        self.assertEqual(response_data["error"], "Invalid credentials.")  
        print("OK: Invalid password rejected")

    def test_login_invalid_username(self):
        """Test login with non-existent username."""
        data = {
            "username": "nonexistentuser",
            "password": "strongpassword123"
        }
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response_data = response.json()
        self.assertIn("error", response_data) 
        self.assertEqual(response_data["error"], "Invalid credentials.")  
        print("OK: Invalid username rejected")

    def test_login_missing_data(self):
        """Test login with missing credentials."""
        data = {
            "username": "testuser"
        }
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertIn("error", response_data) 
        self.assertEqual(response_data["error"], "Username and password are required.")
        print("OK: Missing data rejected")


class LogoutAPIViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = "/api/v1/login/"
        self.logout_url = "/api/v1/logout/"
        self.test_user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="strongpassword123"
        )
        self.test_profile = Profile.objects.create(user=self.test_user)
        login_data = {
            "username": "testuser",
            "password": "strongpassword123"
        }
        response = self.client.post(self.login_url, json.dumps(login_data), content_type="application/json")
        self.access_token = response.json()["access"]
        self.refresh_token = response.json()["refresh"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_logout_success(self):
        """Test successful logout with valid JWT token."""
        response = self.client.post(self.logout_url, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("OK: Successful logout")

    def test_logout_without_authentication(self):
        """Test logout attempt without JWT token."""
        self.client.credentials()  
        response = self.client.post(self.logout_url, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response_data = response.json()
        self.assertIn("detail", response_data)  
        self.assertEqual(response_data["detail"], "Authentication credentials were not provided.")
        print("OK: Logout rejected without authentication")

    def test_logout_with_invalid_token(self):
        """Test logout with an invalid JWT token."""
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalidtoken123")
        response = self.client.post(self.logout_url, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response_data = response.json()
        self.assertIn("detail", response_data) 
        self.assertEqual(response_data["detail"], "Given token not valid for any token type")
        self.assertIn("code", response_data)
        self.assertEqual(response_data["code"], "token_not_valid")
        print("OK: Logout rejected with invalid token")

    def test_logout_after_logout(self):
        """Test logout attempt after already logged out."""
        self.client.post(self.logout_url, content_type="application/json")
        response = self.client.post(self.logout_url, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("OK: Logout allowed after already logged out")
        

class ProfileListAPIViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.profile1 = Profile.objects.create(
            user=self.user,
            bio="Test bio 1"
        )
        self.profile2 = Profile.objects.create(
            user=User.objects.create_user(username="user2", password="pass"),
            bio="Test bio 2"
        )
        self.url = reverse('users-list') 

    def test_get_profile_list_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        profiles = Profile.objects.all()
        serializer = ProfileSerializer(profiles, many=True)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_profile_list_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_pagination(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url, {"page": 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        profiles = Profile.objects.all()
        serializer = ProfileSerializer(profiles, many=True)
        self.assertTrue(len(response.data) <= len(serializer.data))

    def tearDown(self):
        self.client.force_authenticate(user=None)
        User.objects.all().delete()
        Profile.objects.all().delete()
