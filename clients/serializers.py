from rest_framework import serializers
from .models import Clients, MetricsBandwidth

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clients
        fields = '__all__'

class MetricsBandwidthSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetricsBandwidth
        fields = '__all__' 
