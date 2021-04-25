from django.urls import path
from . import views

urlpatterns = [
    path('dashboard', views.dashboard, name='dashboard'),

    #path('add_portfolio', views.add_portfolio, name='add_portfolio'),
    #path('edit_portfolio/<int:pk>/', views.edit_portfolio, name='edit_portfolio'),
    #path('deletes_portfolio/<int:pk>/', views.deletes_portfolio, name='deletes_portfolio'),
]