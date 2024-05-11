from django.urls import path

from . import views
from .views import (UserProfileView, PostsListView, PostCreateView,
                    EditPostView, EditProfileView, PostDetailView, PostDeleteView,
                    CommentCreateView, CommentEditView, CommentDeleteView, CategoryPostsView)


app_name = 'blog'

urlpatterns = [
    path('', PostsListView.as_view(), name='index'),
    path('posts/create/', PostCreateView.as_view(), name='create_post'),
    path('posts/<int:post_id>/edit/', EditPostView.as_view(), name='edit_post'),
    path('posts/<int:post_id>/delete/', PostDeleteView.as_view(), name='delete_post'),
    path('posts/<int:post_id>/', PostDetailView.as_view(), name='post_detail'),
    path('profile/<str:username>/', UserProfileView.as_view(), name='profile'),
    path('profile/<str:username>/edit/', EditProfileView.as_view(), name='edit_profile'),
    path('posts/<int:post_id>/comment/', CommentCreateView.as_view(), name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/', CommentEditView.as_view(), name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/', CommentDeleteView.as_view(), name='delete_comment'),

    path('category/<slug:category_slug>/', CategoryPostsView.as_view(),
         name='category_posts'),
]
