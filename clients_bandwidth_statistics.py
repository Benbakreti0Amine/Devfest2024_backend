import subprocess
import time
import re

class BandwidthMonitor:
    def __init__(self):
        self.clients = {
            '192.168.1.2': 'PC1',
            '192.168.1.3': 'PC2'
        }
        self.stats = {client_ip: {'frames': 0, 'bytes': 0} for client_ip in self.clients.keys()}

    def run_tshark(self):
        try:
            # Command to run tshark for each client
            for client_ip in self.clients:
                cmd = [
                    'tshark',
                    '-r', r"C:\Users\user\OneDrive\Desktop\f.pcapng",
                    '-q', '-z', 'io,stat,0', f'ip.addr=={client_ip}'
                ]

                # Run the command and capture the output
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output, _ = process.communicate()

                # Process the output
                self.process_output(client_ip, output.decode())

        except Exception as e:
            print(f"Error running tshark: {e}")

    def process_output(self, client_ip, output):
        # Regex to capture the frames and bytes statistics
        match = re.search(r'\| *(\d+) *\| *(\d+) *\|', output)

        if match:
            frames = int(match.group(1))
            bytes_ = int(match.group(2))

            # Store the statistics
            self.stats[client_ip]['frames'] += frames
            self.stats[client_ip]['bytes'] += bytes_

            # Display the statistics in an organized way
            self.display_statistics(client_ip)

    def display_statistics(self, client_ip):
        client_name = self.clients[client_ip]
        frames = self.stats[client_ip]['frames']
        bytes_ = self.stats[client_ip]['bytes']
        bandwidth_mbps = (bytes_ * 8) / (1024 * 1024)  # Convert bytes to Mbps

        print(f"\nClient: {client_name} ({client_ip})")
        print(f"Frames: {frames}")
        print(f"Bytes: {bytes_:,} bytes")
        print(f"Bandwidth: {bandwidth_mbps:.2f} Mbps")

def main():
    monitor = BandwidthMonitor()

    # Run the bandwidth monitor in real-time
    while True:
        monitor.run_tshark()
        time.sleep(10)  # Adjust the interval as needed

if __name__ == "__main__":
    main()
