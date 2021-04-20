from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_index, name='blog'),
    path('post/<str:post_name>/', views.post, name='post'),
    #CRUD
    path('add_post', views.add_post, name='add_post'),
    path('edit_post/<int:pk>/', views.edit_post, name='edit_post'),
    path('delete_post/<int:pk>/', views.delete_post, name='delete_post'),
]