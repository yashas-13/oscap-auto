#!/bin/bash

# Define project name
PROJECT_NAME="grcofcyberjeet_client"

# Create project directory
mkdir -p $PROJECT_NAME
cd $PROJECT_NAME

# Install necessary packages
sudo apt-get update
sudo apt-get install -y python3-tk libopenscap8

# Install required Python modules
pip install subprocess os

# Clone the repository if it doesn't exist
if [ ! -d "oscap-auto" ]; then
    git clone https://github.com/yashas-13/oscap-auto.git
fi

# Create client.py
cat <<EOL > client.py
import socket
import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

def install_dependencies():
    # Install libopenscap8
    install_libopenscap_command = "apt-get install -y libopenscap8"
    subprocess.run(install_libopenscap_command, shell=True)

    # Install required Python modules
    python_modules = ["subprocess", "os"]
    for module in python_modules:
        install_module_command = f"pip install {module}"
        subprocess.run(install_module_command, shell=True)

    # Clone the repository if it doesn't exist
    if not os.path.exists("oscap-auto"):
        subprocess.run(["git", "clone", "https://github.com/yashas-13/oscap-auto.git"])

def perform_scan():
    # Navigate to the cloned directory
    os.chdir("oscap-auto")

    # Get information about the XML file
    result_info = subprocess.run(["oscap", "info", "ssg-ubuntu2204-ds-1.2.xml"], capture_output=True, text=True)
    output_info = result_info.stdout

    # Extract profiles with IDs
    profiles_start = output_info.find("Profiles:")
    profiles_end = output_info.find("Referenced check files:")
    profiles_text = output_info[profiles_start:profiles_end].strip()
    profiles_list = profiles_text.split("\\n")

    profile_ids = []
    for profile_line in profiles_list:
        if "Id:" in profile_line:
            profile_id = profile_line.split("Id:")[1].strip()
            profile_ids.append(profile_id)

    # Display profile IDs
    print("Profile IDs:")
    for idx, profile_id in enumerate(profile_ids, start=1):
        print(f"{idx}. {profile_id}")

    # Select profile ID for scan
    selected_idx = input("Enter the number corresponding to the profile ID you want to scan: ")
    selected_profile_id = profile_ids[int(selected_idx) - 1]

    # Perform the scan with the selected profile ID
    scan_command = f"oscap xccdf eval --profile {selected_profile_id} --results-arf scan_result.xml ssg-ubuntu2204-ds-1.2.xml"
    print("Executing scan command:")
    subprocess.run(scan_command, shell=True)

    # Convert the results to HTML
    report_command = "oscap xccdf generate report scan_result.xml > scan_result.html"
    print("Executing report generation command:")
    subprocess.run(report_command, shell=True)

    return "scan_result.html"

def send_file_to_server(file_path, host='192.168.254.142', port=65432):
    if not os.path.isfile(file_path):
        print(f"File '{file_path}' does not exist.")
        return

    file_size = os.path.getsize(file_path)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            print(f"Connected to server at {host}:{port}")

            s.sendall(str(file_size).encode())
            s.recv(1024)  # Wait for acknowledgment from the server

            with open(file_path, 'rb') as f:
                file_data = f.read()
                s.sendall(file_data)

            print(f"File '{file_path}' sent to server.")
            messagebox.showinfo("Success", f"File '{file_path}' sent to server.")
        except ConnectionRefusedError:
            print("Connection refused. Please check if the server is running and reachable.")
        except Exception as e:
            print(f"An error occurred: {e}")

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("HTML files", "*.html")])
    if file_path:
        file_label.config(text=file_path)
        send_file_to_server(file_path)

def run_scan_and_send():
    install_dependencies()
    scan_file = perform_scan()
    send_file_to_server(scan_file)

root = tk.Tk()
root.title("HTML File Sender")

frame = tk.Frame(root)
frame.pack(pady=20, padx=20)

file_label = tk.Label(frame, text="No file selected", wraplength=400)
file_label.pack(pady=10)

browse_button = tk.Button(frame, text="Browse", command=browse_file)
browse_button.pack(pady=5)

scan_button = tk.Button(frame, text="Run Scan and Send", command=run_scan_and_send)
scan_button.pack(pady=5)

root.mainloop()
EOL

echo "Client setup completed in $PROJECT_NAME."
