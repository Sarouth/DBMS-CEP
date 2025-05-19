from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, UserProfileView, AccountViewSet, CategoryViewSet,
    TransactionViewSet, BudgetViewSet, GoalViewSet, dashboard_summary
)

# Set up the router
router = DefaultRouter()
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'budgets', BudgetViewSet, basename='budget')
router.register(r'goals', GoalViewSet, basename='goal')

urlpatterns = [
    # Authentication endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    
    # Dashboard data
    path('dashboard/summary/', dashboard_summary, name='dashboard-summary'),
    
    # Include the router URLs
    path('', include(router.urls)),
]
