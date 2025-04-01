from django.urls import path
from .posts_controls import *
from .profile_controls import *
from .stories_control import *
from .hashtags_control import *

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
         name="story-list-create"
         ),
    
    path(
        'stories/<int:story_id>/',
         StoryManagmentAPIView.as_view(), 
         name="story-detail"
         ),
    
    path(
        'stories/<int:story_id>/like/',
        StoryLikeAPIView.as_view(),
        name="story-like"
        ),
    
    path(
        'profiles/<str:user_name>/follow/', 
        FollowAPIView.as_view(),
        name="follow-user"
        ),
    
    path(
        'profiles/<str:user_name>/unfollow/',
        UnfollowAPIView.as_view(),
        name="unfollow-user"
        ),
    
    path(
        'profiles/<str:user_name>/',
        ProfileDetailView.as_view(),
        name="profile-detail"
        ),
    
    path(
        'profiles/<str:user_name>/followers/',
        ProfileFollowersListAPIView.as_view(),
        name="profile-follower-list"
        ),
    
    path(
        'profiles/<str:user_name>/followings/',
        ProfileFollowingsListAPIView.as_view(),
        name="profile-followings-list"
    ),
    
    path('hashtags/', 
         HashTagListAPIView.as_view(), 
         name="hashtags-list"
         ),
    
        path(
            'hashtags/<str:hashtaq_name>/',
            HashtagsPostListAPIView.as_view(),
            name="hashtags-posts"
            ),

]

