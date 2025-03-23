from django.urls import path
from .posts_controls import *
from .profile_controls import *
from .stories_control import *

urlpatterns = [
    path(
        'users_list/',
        ProfileListAPIView.as_view(), 
        name="users-list"
        ),
    
    path(
        'user_search/',
        ProfileSearchAPIView.as_view(), 
        name="user-search"
        ),
    
    path(
        'register/',
        RegisterAPIView.as_view(),
        name="register"
        ),
    
    path(
        'login/',
        LoginAPIView.as_view(),
        name="login"
        ),
    
    path(
        'logout/',
        LogoutAPIView.as_view(),
        name="logout"
        ),
    
    path(
        'posts/', 
        PostListCreateAPIView.as_view(),
        name="posts-create"
        ),
    
    path(
        'post/<int:id>/',
        PostDetailAPIView.as_view(),
        name="post-detail"
        ),
    
    path(
        'like/<int:post_id>/',
        LikePostAPIView.as_view(),
        name="like-post"
        ),
    
    path(
        'comments/<int:post_id>/',
        CommentManagmentAPIView.as_view(),
        name="post-comments"
        ),
    
    path(
        'comments/delete/<int:comment_id>/',
        CommentManagmentAPIView.as_view(),
        name="comment-delete"
        ),
    
    path(
        'like/comment/<int:comment_id>/', 
         LikeCommentAPIView.as_view(), name="like-comment"
         ),
    
    path(
        'comments/', CommentListAPIView.as_view(),
        name="comments-list"
        ),
    
    path(
        'stories/', 
         StoryManagmentAPIView.as_view(),
         name="story-api"
         ),
    path(
        'profiles/<int:user_id>/follow/', 
        FollowAPIView.as_view(),
        name="follow-user"
        ),
    
    path(
        'profiles/<int:user_id>/unfollow/',
        UnfollowAPIView.as_view(),
        name="unfollow-user"
        ),
    
    path(
        'profiles/<int:user_id>/',
        ProfileDetailView.as_view(),
        name="profile-detail"
        ),
    
    path(
        'profiles/<int:profile_id>/followers/',
        ProfileFollowersListAPIView.as_view(),
        name="profile-follower-list"
        ),
    
    path(
        'profiles/<int:profile_id>/followings/',
        ProfileFollowingsListAPIView.as_view(),
        name="profile-followings-list"
    ),
    
]

