from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_index, name='blog'),
    path('article/<str:name>/', views.article, name='article')
]