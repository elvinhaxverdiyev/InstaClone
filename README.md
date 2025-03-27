InstaApp API README 🚀
InstaApp 📸 is an app that provides social network features. It allows users to create profiles, post content, comment, share stories, and follow/unfollow others through a RESTful API. The API uses JWT (JSON Web Token) for authentication and ensures secure user management.
Ready? Let’s dive in! 😊

Core Features ✨
User Registration and Login 📝
User Profiles 👤
Create, Update, and Delete Posts 🖼️
Add and Delete Comments 💬
Create and Like Stories 📖❤️
Follow and Unfollow Users 🔍👥

API Endpoints 🔑
1. User Operations 👥
Get Users List
GET /users_list/
Retrieve a list of all users. 👀

User Search
GET /user_search/
Search for a user by their username. 🔍

User Registration
POST /register/
Register a new user.

User Login
POST /login/
Login with a username and password.

User Logout
POST /logout/
Log out the current user. 🚪

2. Post Operations 📝
Create and List Posts
POST /posts/ (Create Post)
GET /posts/ (Get Posts List)
Create and list posts with a title, description, and image. 🖼️

Get Post Details
GET /post/{id}/
Get details of a specific post. 📑

Like a Post
POST /like/{post_id}/
Like a post. 👍

Add a Comment to a Post
POST /comments/{post_id}/
Add a comment to a post. 💬

Delete a Comment
DELETE /comments/delete/{comment_id}/
Delete a comment from a post. 🗑️

3. Comment Operations 💬
Like a Comment
POST /like/comment/{comment_id}/
Like a comment. 💖

Get Comment List
GET /comments/
Get a list of all comments. 📜

4. Story Operations 📖
Create and List Stories
POST /stories/ (Create Story)
GET /stories/ (Get Stories List)
Create and view stories. 🎥

Like a Story
POST /stories/{story_id}/like/
Like a story. ❤️

Get Story Details
GET /stories/{story_id}/
Get details of a specific story. 📖

5. Follow Operations 🔄
Follow a User
POST /profiles/{user_name}/follow/
Follow a user. 🔔

Unfollow a User
POST /profiles/{user_name}/unfollow/
Unfollow a user. ❌

Get a User's Followings
GET /profiles/{user_name}/followings/
View the people a user is following. 👥

Get a User's Followers
GET /profiles/{user_name}/followers/
View the followers of a user. 👣

Authentication 🔐
JWT (JSON Web Token) is used for secure authentication.
The user receives a JWT token upon registration and login, and this token is used to authenticate API requests.

Additional Information 📚
Custom Permissions ⚖️
The CanManageObjectPermission custom permission class is designed to manage access to resources. This permission ensures that only the object owner or an admin can modify or delete objects, and that users can access certain resources if they are following the object owner.

Permission Overview:
For GET, POST requests:
Access is granted if the user is the object owner or an admin.
If the user is not the owner but follows the object owner, they can access the object (GET).
For PUT, PATCH, DELETE requests:
Access is granted only if the user is the object owner or an admin.
If the object has no profile or user attribute, only staff members can access it.


