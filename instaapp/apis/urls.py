from django.urls import path
from .views import *

urlpatterns = [
    path('users_list/', ProfileListAPIView.as_view(), name="users-list"),
    path('register/', RegisterAPIView.as_view(), name="register"),
    path('posts/', PostListCreateAPIView.as_view(), name="post-create"),
    path('post/<int:id>/', PostDetailAPIView.as_view(), name="post-detail"),
    path('like/<int:post_id>/', LikeAPIView.as_view(), name="like-post"),

]
