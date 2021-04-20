from django.urls import path
from . import views

urlpatterns = [
    path('', views.market, name='market'),
    path('asset/<str:asset_symbol>/', views.asset, name='asset'),
]