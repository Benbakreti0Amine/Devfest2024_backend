from scapy.all import sniff, IP
import time
from collections import defaultdict

def packet_callback(packet):
    if IP in packet:
        if packet[IP].src == "192.168.1.2" or packet[IP].dst == "192.168.1.2":
            return len(packet)
    return 0

def calculate_bandwidth(bytes, interval):
    return (bytes * 8) / (interval * 1000000)  # Convert to Mbps

def main():
    print("Starting real-time bandwidth monitoring for IP 192.168.1.2")
    print("Press Ctrl+C to stop")

    interval = 1  # Update interval in seconds
    total_bytes = 0
    start_time = time.time()

    try:
        while True:
            current_time = time.time()
            if current_time - start_time >= interval:
                bandwidth = calculate_bandwidth(total_bytes, interval)
                print(f"Bandwidth: {bandwidth:.2f} Mbps")
                total_bytes = 0
                start_time = current_time
            
            # Capture packets for a short duration
            packets = sniff(timeout=0.1, prn=packet_callback, store=0)
            total_bytes += sum(packets)

    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    main()


