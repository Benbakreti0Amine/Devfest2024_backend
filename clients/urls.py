from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet, MetricsBandwidthViewSet, BandwidthMonitorAPI

router = DefaultRouter()
router.register(r'clients', ClientViewSet)
router.register(r'metrics', MetricsBandwidthViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('bandwidth-monitor/', BandwidthMonitorAPI.as_view(), name='bandwidth_monitor_api'),
]

