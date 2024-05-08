from django.urls import path

from . import views
from .views import UserProfileView, PostsListView, PostCreateView


app_name = 'blog'

urlpatterns = [
    path('', PostsListView.as_view(), name='index'),
    path('posts/create/', PostCreateView.as_view(), name='create_post'),
    path('profile/<str:username>/', UserProfileView.as_view(), name='profile'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('category/<slug:category_slug>/', views.category_posts,
         name='category_posts'),
]
