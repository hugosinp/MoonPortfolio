from django.urls import path
from . import views

urlpatterns = [
    path('simplified', views.market_simplified, name='market_simplified'),
    path('advanced', views.market_advanced, name='market_advanced'),
    path('asset/<str:asset_symbol>/', views.asset, name='asset'),
]