#!/bin/bash

# Define project name
PROJECT_NAME="grcofcyberjeet_server"

# Create project directory
mkdir -p $PROJECT_NAME
cd $PROJECT_NAME

# Create server.py
cat <<EOL > server.py
import socket

def start_server(host='0.0.0.0', port=65432):  # Bind to all interfaces
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server listening on {host}:{port}")

        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            file_size = int(conn.recv(1024).decode())
            conn.sendall(b'ACK')

            data_received = 0
            file_data = b''
            while data_received < file_size:
                data = conn.recv(1024)
                data_received += len(data)
                file_data += data

            with open('received_file.html', 'wb') as f:
                f.write(file_data)

            print("File received and saved as 'received_file.html'")

            with open('received_file.html', 'r') as f:
                html_content = f.read()
                print("Displaying HTML file content:")
                print(html_content)

if __name__ == "__main__":
    start_server()
EOL

echo "Server setup completed in $PROJECT_NAME."
