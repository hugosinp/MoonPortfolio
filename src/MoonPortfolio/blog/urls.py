from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_index, name='blog'),
    path('post/<str:post_name>/', views.post, name='post'),
    path('add_post', views.add_post, name='add_post'),
    path('edit_post', views.edit_post, name='edit_post'),
]