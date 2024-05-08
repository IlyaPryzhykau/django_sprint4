from django.urls import path

from . import views
from .views import UserProfileView


app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('profile/<str:username>/', UserProfileView.as_view(), name='profile'),

    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('category/<slug:category_slug>/', views.category_posts,
         name='category_posts'),
]
