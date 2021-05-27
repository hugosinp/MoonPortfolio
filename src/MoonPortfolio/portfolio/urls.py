from django.urls import path
from . import views

urlpatterns = [
    path('dashboard', views.dashboard_selection, name='dashboard'),
    path('dashboard/<int:portfolio_id>/', views.dashboard, name='dashboard'),
    #path('edit_portfolio/<int:portfolio_id>/', views.edit_portfolio, name='edit_portfolio'),
    path('delete_portfolio/<int:portfolio_id>/', views.delete_portfolio, name='delete_portfolio'),

    path('delete_transaction/<int:portfolio_id>/<int:holding_id>/<int:transaction_id>/', views.delete_transaction, name='delete_transaction'),
    path('dashboard/<int:portfolio_id>/<int:holding_id>', views.holding_details, name='holding_details')
]