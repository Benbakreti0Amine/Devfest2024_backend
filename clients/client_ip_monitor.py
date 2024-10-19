import subprocess
import time
import re
from datetime import datetime

class BandwidthMonitor:
    def __init__(self, pcap_file, client_ip):
        self.pcap_file = pcap_file
        self.client_ip = client_ip
        self.stats = {'frames': 0, 'bytes': 0}

    def run_tshark(self):
        
        try:
            # Command to run tshark for the specified client IP
            cmd = [
                'tshark',
                '-r', self.pcap_file,  # Path to the pcap file
                '-q', '-z', 'io,stat,1', f'ip.addr=={self.client_ip}'  # 1 second interval for stats
            ]

            # Run the command and capture the output
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, _ = process.communicate()

            # Check if the process finished successfully
            if process.returncode != 0:
                print(f"Error: tshark command failed with return code {process.returncode}")
                print(output.decode())
                return

            # Process the output
            self.process_output(output.decode())

        except Exception as e:
            print(f"Error running tshark: {e}")

    def process_output(self, output):
        # Regex to capture the frames and bytes statistics
        match = re.search(r'\|\s*(\d+)\s*\|\s*(\d+)\s*\|', output)

        if match:
            frames = int(match.group(1))
            bytes_ = int(match.group(2))

            # Store the statistics
            self.stats['frames'] += frames
            self.stats['bytes'] += bytes_

            # Display the statistics
            self.display_statistics()

    def display_statistics(self):
        frames = self.stats['frames']
        bytes_ = self.stats['bytes']
        bandwidth_mbps = (bytes_ * 8) / (1024 * 1024)  # Convert bytes to Mbps

        # Get the current time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"\n[{current_time}] Client: {self.client_ip}")
        print(f"Frames: {frames}")
        print(f"Bytes: {bytes_:,} bytes")
        print(f"Bandwidth: {bandwidth_mbps:.2f} Mbps")

def main(client_ip):
    pcap_file = r"C:\Users\asus\OneDrive\Bureau\DevFest2024\Devfest2024_backend\udp.pcapng"
    monitor = BandwidthMonitor(pcap_file, client_ip)

    # Run the bandwidth monitor in real-time
    try:
        while True:
            monitor.run_tshark()
            time.sleep(2)  # Adjust the interval as needed
    except KeyboardInterrupt:
        print("Monitoring stopped.")

if __name__ == "__main__":
    # Example client IP; replace this with the desired IP address
    client_ip = '192.168.1.2'  # Change to the desired IP address
    main(client_ip)
