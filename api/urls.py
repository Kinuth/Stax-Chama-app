from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoanViewSet, UserViewSet, ChamaGroupViewSet, RegisterView, DashboardAnalyticsView, ContributionViewSet, migrate_db


# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'contributions', ContributionViewSet, basename='contribution')
router.register(r'groups', ChamaGroupViewSet, basename='group')
router.register(r'loans', LoanViewSet, basename='loan')

urlpatterns = [
    # This includes all the auto-generated routes (list, detail, etc.)
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='auth_register'),
    # Custom endpoint example for M-Pesa callbacks or analytics
    # path('analytics/<int:group_id>/', GroupAnalyticsView.as_view(), name='group-analytics'),
    path('analytics/', DashboardAnalyticsView.as_view(), name='dashboard-analytics'),
    path('migrate/', migrate_db, name='migrate_db'),
]