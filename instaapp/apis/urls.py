from django.urls import path
from .views import *

urlpatterns = [
    path('users_list/', ProfileListAPIView.as_view(), name="users-list"),
     path('user_search/', ProfileSearchAPIView.as_view(), name="user-search"),
    path('register/', RegisterAPIView.as_view(), name="register"),
    path('posts/', PostListCreateAPIView.as_view(), name="posts-create"),
    path('post/<int:id>/', PostDetailAPIView.as_view(), name="post-detail"),
    path('like/<int:post_id>/', LikePostAPIView.as_view(), name="like-post"),
    path('comments/', CommentCreateAPIView.as_view(), name="comment-create"), 
]
