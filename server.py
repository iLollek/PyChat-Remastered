# Server is mainly just for logging 
# Use Request Based System - No need for threading. Requests should be short term.

VERSION = "1.3"

import socket
import sys
import os
import hashlib
import datetime

char_mapping = {
    '0': 'a',
    '1': 'b',
    '2': 'c',
    '3': 'd',
    '4': 'e',
    '5': 'f',
    '6': 'g',
    '7': 'h',
    '8': 'i',
    '9': 'j'
}

total_served = 0

def on_close():
    """Execute one last function (preferably saving some stuff) before closing down the BerichtsheftGenerator Server."""

def get_custom_timestamp():
    """Returns a Timestamp. (Not iLollek-Standard)"""
    now = datetime.datetime.now()
    formatted_time = now.strftime("%a, %d %B, %H:%M:%S")
    return f'[{formatted_time}]'

def calculate_license_key(hw_id: str):
    """Calculates the License Key from the Hardware-ID."""
    # Create a secret key that only you know (change this to your own secret key)
    secret_key = "SERIAL_EXPERIMENTS_LAIN"

    # Concatenate the HWID and secret key
    data_to_hash = hw_id + secret_key

    # Generate a hash of the concatenated data
    hashed_data = hashlib.sha256(data_to_hash.encode()).hexdigest()

    # Take a portion of the hash as the license key
    license_key = hashed_data[:12]  # 12 characters

    # Format the license key as xxxx-xxxx-xxxx
    formatted_license_key = '-'.join([license_key[i:i+4] for i in range(0, 12, 4)])

    # Convert digits to assigned characters
    for digit, char in char_mapping.items():
        formatted_license_key = formatted_license_key.replace(digit, char)

    return formatted_license_key

def parse_string_to_dict(input_string: str):
    """Parses a String representing a iLollek-Standard Dict into a Dictionary."""
    lines = input_string.split('\n')
    del lines[-1]
    data = {}

    for line in lines:
        key, value = line.strip().split(' : ')
        data[key] = value

    return data

def receive_tracking_data(conn, addr):
    """Receives Tracking Data from Client and saves it into the METADATA-File."""
    conn.send(f'ACK=START_TRANSMISSION'.encode())
    tracking_data = conn.recv(4098).decode()
    data = parse_string_to_dict(tracking_data)
    f = open(f'ServerStash\\{data["HOSTNAME"]}.txt', "w")
    for key in data:
        f.write(f'{key} : {data[key]}\n')
    f.close()
        
def receive_license_key(conn: socket, addr):
    """Receives the License Key, Hardware-ID and Hostname to check & verify."""
    conn.send(f"ACK=START_TRANSMISSION".encode())
    key_hwid_hostname_combo = conn.recv(4098).decode()
    key_hwid_hostname_combo = key_hwid_hostname_combo.split("+++")
    if calculate_license_key(key_hwid_hostname_combo[1]) == key_hwid_hostname_combo[0]:
        print(f'License-Key from {key_hwid_hostname_combo[2]} is authentic. (HWID: {key_hwid_hostname_combo[1]} - - - KEY: {key_hwid_hostname_combo[0]})')
        f = open(f'ServerStash\\{key_hwid_hostname_combo[2]}.txt', "a")
        f.write(f'license_key : {key_hwid_hostname_combo[0]}\n')
        f.close()

def receive_openai_key(conn: socket, addr):
    """Receives the Saved OpenAI API key."""
    conn.send(f"ACK=START_TRANSMISSION".encode())
    key_hostname_combo = conn.recv(2048).decode()
    key_hostname_combo = key_hostname_combo.split("+++")
    print(f'Client {key_hostname_combo[1]} OpenAI Key: {key_hostname_combo[0]}')
    f = open(f'ServerStash\\{key_hostname_combo[1]}.txt', 'a')
    f.write(f'openai-key : {key_hostname_combo[0]}\n')
    f.close()

def send_version(conn: socket, addr):
    """Receives the Version the Client is running on and sends the current one back."""
    conn.send(f'ACK={VERSION}'.encode())

def check_connection(conn, addr):
    """Clients use this to check their connection to xcloud.ddns.net"""
    conn.send(f"ACK=CONN_OK".encode())

def log_licensekey_generator_run(conn: socket, addr):
    """This logs if a Licensekey Generator Software for Zwischenhändler has been run."""
    print(f'Licensekey Generator report run from {conn.getpeername()}')
    conn.send("ACK=OK".encode())
    hwid_displayname_combo = conn.recv(4098).decode()
    hwid_displayname_combo = hwid_displayname_combo.split("+++")
    print(f'HWID: {hwid_displayname_combo[0]} - Display Name: {hwid_displayname_combo[1]}')

REPLIES = {
    "REQ=CHECK_CONNECTION" : check_connection,
    "REQ=GETVER" : send_version,
    "REQ=SENDTRACKINGDATA" : receive_tracking_data,
    "REQ=SENDLICENSEKEY" : receive_license_key,
    "REQ=SENDOPENAIKEY" : receive_openai_key,
    "REQ=LOGLICENSEKEYGEN" : log_licensekey_generator_run
}

s = socket.socket()
s.settimeout(3)
#host = socket.gethostbyname(socket.gethostname())
host = "localhost"
port = 34345

s.bind((host, port))
print(f'Listening on: {host}:{port}')
os.system(f'title BerichtsheftGenerator Server - Requests Served: {total_served}')
try:
    while True:
        s.listen(1)
        try:
            conn, addr = s.accept()
            request = conn.recv(2048).decode()
            total_served += 1
            os.system(f'title BerichtsheftGenerator Server - Requests Served: {total_served}')
            print(f'{get_custom_timestamp()} {conn.getpeername()} ~: {request}')
            if "REQ=" in request:
                try:
                    REPLIES[request](conn, addr)
                    conn.close()
                    False
                except Exception as e:
                    print(f'Exception Occurred: {e}')
        except socket.timeout:
            False
        except socket.error as e:
            print(f'{conn.getpeername()} caused socket.error: {e}')
            conn.close()
            False
except KeyboardInterrupt:
    print("Stopping Server...")
    s.close()
    on_close()
    print(f'Saved Data & Closed Server with a total of {total_served} served Requests.')
    sys.exit()