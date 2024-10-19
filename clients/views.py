from rest_framework import viewsets
from .models import Clients, MetricsBandwidth
from .serializers import ClientSerializer, MetricsBandwidthSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from .client_ip_monitor import BandwidthMonitor
import os
import tempfile

class ClientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Clients.objects.all()
    serializer_class = ClientSerializer

class MetricsBandwidthViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MetricsBandwidth.objects.all()
    serializer_class = MetricsBandwidthSerializer

class BandwidthMonitorAPI(APIView):
    def post(self, request):
        # Get the uploaded file and client IP from the request
        pcap_file = request.FILES.get('pcap_file')
        client_ip = request.data.get('client_ip')

        if not pcap_file or not client_ip:
            return Response({"error": "pcap_file and client_ip are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Create a temporary file for the pcap file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pcap') as tmp_file:
            tmp_file_path = tmp_file.name  # Save the path of the temporary file

            try:
                # Write the uploaded file content to the temporary file
                for chunk in pcap_file.chunks():
                    tmp_file.write(chunk)
                tmp_file.flush()  # Ensure all content is written

            except Exception as e:
                return Response({"error": "Error writing the temporary file: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Ensure the file is closed before processing it with tshark
        try:
            # Check if the file exists before running tshark
            if not os.path.exists(tmp_file_path):
                return Response({"error": f"Temporary file not found: {tmp_file_path}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Run the BandwidthMonitor with the saved file and client IP
            monitor = BandwidthMonitor(tmp_file_path, client_ip)
            monitor.run_tshark()  # Capture the statistics

            # Prepare the response data
            data = {
                "client_ip": client_ip,
                "frames": monitor.stats['frames'],
                "bytes": monitor.stats['bytes'],
                "bandwidth_mbps": (monitor.stats['bytes'] * 8) / (1024 * 1024)  # Convert bytes to Mbps
            }

            # Return the stats as a JSON response
            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            # Ensure the file is deleted after tshark finishes using it
            try:
                if os.path.exists(tmp_file_path):
                    os.remove(tmp_file_path)
            except Exception as e:
                print(f"Error deleting temporary file: {e}")