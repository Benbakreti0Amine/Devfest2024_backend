import sqlite3
from datetime import datetime

# Connect to the existing SQLite database
def connect_db():
    conn = sqlite3.connect('db.sqlite3')  # Change to the existing database name
    return conn

# Create tables if they don't exist
def create_tables(conn):
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

# Check if the client exists, otherwise insert client data
def get_or_insert_client(conn, ip_address):
    cursor = conn.execute("SELECT id FROM clients WHERE ip_address = ?;", (ip_address,))
    result = cursor.fetchone()
    if result:
        return result[0]  # Return the client ID if it exists
    else:
        with conn:
            cursor = conn.execute("INSERT INTO clients (ip_address) VALUES (?);", (ip_address,))
            return cursor.lastrowid  # Return the newly inserted client ID

# Insert metrics data
def insert_metrics(conn, client_id, requested_bw, frames, bytes_data):

    with conn:
        conn.execute("""
            INSERT INTO metrics_bandwidth (client_id, bw_requested, frames, bytes, bandwidth, timestamp)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (client_id, requested_bw, frames, bytes_data, datetime.now().isoformat()))

# Sample data with requested bandwidths
data = [
    {"client": "PC1", "ip": "192.168.1.2", "requested_bw": 0.8, "frames": 183, "bytes": 18048},
    {"client": "PC2", "ip": "192.168.1.3", "requested_bw": 1.0, "frames": 183, "bytes": 18048},
    {"client": "PC1", "ip": "192.168.1.2", "requested_bw": 1.4, "frames": 366, "bytes": 36096},
    {"client": "PC2", "ip": "192.168.1.3", "requested_bw": 1.6, "frames": 366, "bytes": 36096}
]

# Main function to insert data
def main():
    conn = connect_db()
    create_tables(conn)

    for entry in data:
        # Get or insert client and get their ID
        client_id = get_or_insert_client(conn, entry["ip"])
        # Insert metrics for the client
        insert_metrics(conn, client_id, entry["requested_bw"], entry["frames"], entry["bytes"])

    conn.close()
    print("Data insertion complete.")

if __name__ == "__main__":
    main()
