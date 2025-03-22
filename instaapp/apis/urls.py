from django.urls import path
from .posts_controls import *
from .profile_controls import *

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
        )
 
]
