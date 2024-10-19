from rest_framework import viewsets
from .models import Clients, MetricsBandwidth
from .serializers import ClientSerializer, MetricsBandwidthSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from .clients_bandwidth_statistics import BandwidthMonitor
import os
import tempfile
import time
from datetime import datetime
import sqlite3

class ClientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Clients.objects.all()
    serializer_class = ClientSerializer

class MetricsBandwidthViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MetricsBandwidth.objects.all()
    serializer_class = MetricsBandwidthSerializer

# Reuse the BandwidthMonitor class with minimal modifications to suit the API context



class BandwidthMonitorAPI(APIView):
    def post(self, request):
        pcap_file = request.FILES.get('pcap_file')
        
        if not pcap_file :
            return Response({"error": "pcap_file  are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Create a temporary file for the pcap file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pcap') as tmp_file:
            tmp_file_path = tmp_file.name
            for chunk in pcap_file.chunks():
                tmp_file.write(chunk)

        try:
            results = []  # Initialize a list to store multiple statistics entries
            # Initialize the bandwidth monitor
            monitor = BandwidthMonitor(tmp_file_path)

            conn = self.connect_db()  # Connect to the database
            self.create_tables(conn)  # Ensure tables are created

            for _ in range(5):  # This will loop 5 times with 2-second intervals
                monitor.run_tshark()

                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                client_ips = monitor.client_ips  # Assuming this returns a list of client IPs

                for client_ip in client_ips:
                    frames = monitor.stats[client_ip]['frames']  # Collect the frames for this client
                    bytes_ = monitor.stats[client_ip]['bytes']  # Collect the bytes for this client
                    bandwidth_mbps = (bytes_ * 8) / (1024 * 1024)  # Convert bytes to Mbps

                    # Prepare a statistics entry for this iteration
                    entry = {
                        "time": current_time,
                        "client_ip": client_ip,
                        "frames": frames,
                        "bytes": bytes_,
                        "bandwidth_mbps": bandwidth_mbps,
                    }

                    # Append the entry to the results list
                    results.append(entry)

                    # Get or insert client and get their ID
                    client_id = self.get_or_insert_client(conn, client_ip)

                    # Insert metrics for the client
                    self.insert_metrics(conn, client_id, bandwidth_mbps, frames, bytes_)

                time.sleep(2)  # Wait for 2 seconds between each run

            return Response(results, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            # Clean up the temporary file
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
            if 'conn' in locals():
                conn.close()  # Ensure the database connection is closed

    def connect_db(self):
        """Connect to the existing SQLite database."""
        return sqlite3.connect('db.sqlite3')  # Change to your existing database name

    def create_tables(self, conn):
        """Create tables if they don't exist."""
        with conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip_address TEXT NOT NULL UNIQUE
                );
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS metrics_bandwidth (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER NOT NULL,
                    bw_requested REAL NOT NULL,
                    frames INTEGER NOT NULL,
                    bytes INTEGER NOT NULL,
                    bandwidth REAL NOT NULL,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (client_id) REFERENCES clients(id)
                );
            ''')

    def get_or_insert_client(self, conn, ip_address):
        """Check if the client exists, otherwise insert client data."""
        cursor = conn.execute("SELECT id FROM clients WHERE ip_address = ?;", (ip_address,))
        result = cursor.fetchone()
        if result:
            return result[0]  # Return the client ID if it exists
        else:
            with conn:
                cursor = conn.execute("INSERT INTO clients (ip_address) VALUES (?);", (ip_address,))
                return cursor.lastrowid  # Return the newly inserted client ID

    def insert_metrics(self, conn, client_id, requested_bw, frames, bytes_data):
        """Insert metrics data into the database."""
        with conn:
            conn.execute("""
                INSERT INTO metrics_bandwidth (client_id, bw_requested, frames, bytes, timestamp)
                VALUES (?, ?, ?, ?,  ?);
            """, (client_id, requested_bw, frames, bytes_data, datetime.now().isoformat()))