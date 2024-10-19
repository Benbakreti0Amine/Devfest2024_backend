from rest_framework import viewsets
from .models import Clients, MetricsBandwidth
from .serializers import ClientSerializer, MetricsBandwidthSerializer

class ClientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Clients.objects.all()
    serializer_class = ClientSerializer

class MetricsBandwidthViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MetricsBandwidth.objects.all()
    serializer_class = MetricsBandwidthSerializer
