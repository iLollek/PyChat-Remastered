import socket
import threading
import sys
import ast
import subprocess
import time
import logging
from datetime import datetime

def get_outbound_local_ip():
    """Gets the Verified & Used outbound IP-Address for a LAN Environment"""

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


SERVER_IP = get_outbound_local_ip()
SERVER_PORT = 5555

SERVER_TYPE = "unregistered"
SERVER_VERSION = "v0.1"
SERVER_ALLOW_FOREIGN_VERSIONS = True

users = []
client_user_combo = {}
clients = []

SERVER_CONFIG = {
    "log_chatmessages" : True
}

def timestamp():
    now = datetime.now()
    formatted_timestamp = now.strftime("%d %b %Y - %H:%M:%S")
    return formatted_timestamp

def log_chatmessage(message: str):
    """Logs a Chatmessage if log_chatmessages in SERVER_CONFIG is set to True. Filters out Requests."""

    if message.startswith(f'REQ=') == False:
        if SERVER_CONFIG["log_chatmessages"] == True:
            f = open(f'server_chat.log', 'a')
            f.write(f'[{timestamp()}] {message}\n')
            f.close()

def request_handler(client_socket, request: str, clients) -> bool:
    """The PyChat-REM according Request Handler.
    Requests are sent through the same communication channel (socket) as normal Messages, but they usually
    want Information and they are not rendered in the Chat.
    
    If the Request Handler returns False for some reason, it always means that the Client will get force Disconnected from the Server.
    
    TODO: This implementation might only be doable in the unofficial Server."""

    if "REQ=AUTH" in request:
        request = request.split("$")
        headers = request[1]
        headers = ast.literal_eval(headers)
        if SERVER_TYPE != headers["client-type"]:
            return False
        if SERVER_VERSION != headers["VERSION"]:
            if SERVER_ALLOW_FOREIGN_VERSIONS == False:
                return False
        client_socket.send("ACK=OK".encode())
        client_user_combo[client_socket] = headers["username"]
        users.append(headers["username"])
        broadcast_announcement(clients, f'{headers["username"]} joined the Chatroom. %USERJOIN%')
        log_chatmessage(f'{headers["username"]} joined the Chatroom.')
        return True

    elif "REQ=HEARTBEAT" in request:
        client_socket.send(f'ACK=OK'.encode())
        return True

    elif "REQ=LEAVE" in request:
        try:
            username = client_user_combo[client_socket]
            users.remove(username)
            broadcast_announcement(clients, f'{username} left the Chatroom. (Left by Request) %USERLEAVE%')
            log_chatmessage(f"{username} left the Chatroom. (Left by Request)")
            return False
        except KeyError as e:
            print(f'KeyError: {e}')

    elif "REQ=GETUSERS" in request:
        user_string = ""
        for user in users:
            user_string = user_string + f"{user}%"
        client_socket.send(f"ACK=USERS${user_string}".encode())



def broadcast_announcement(clients, message):
    """Broadcasts a Message to all Clients. Starts with [SERVER]"""
    for c in clients:
        if str(message).startswith("REQ=") == False:
            message = f'[SERVER] {message}'
            c.send(message.encode())



# Function to handle client connections
def handle_client(client_socket, clients):
    print(f"New connection: {client_socket}")
    while True:
        try:
            # Receive message from client
            message = client_socket.recv(1024).decode()
            print(f'Message: {message}')
            log_chatmessage(message)

            if str(message).startswith("REQ="):
                exit_code = request_handler(client_socket, message, clients)
                if exit_code == False:
                    client_socket.close()
                    clients.remove(client_socket)
                    print(f"Connection closed: {client_socket}")
                    break

            if not message:
                # If no message received, close connection
                client_socket.close()
                clients.remove(client_socket)
                print(f"Connection closed: {client_socket}")
                break
            # Broadcast message to all clients
            for c in clients:
                if str(message).startswith("REQ=") == False:
                    c.send(message.encode())
        except Exception as e:
            print(f"Error: {e}")
            # If an error occurs, close connection
            client_socket.close()
            clients.remove(client_socket)
            if client_user_combo[client_socket] in users:
                broadcast_announcement(clients, f'{client_user_combo[client_socket]} left the Chatroom. ({e})')
                log_chatmessage(f'{client_user_combo[client_socket]} left the Chatroom. ({e})')
                users.remove(client_user_combo[client_socket])
            print(f"Connection closed: {client_socket}")
            break

def main():
    global clients
    # Create socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind socket to localhost and port 5555
    server_socket.bind((SERVER_IP, SERVER_PORT))
    # Listen for incoming connections
    server_socket.listen(5)

    print("Server is listening for connections...")

    # List to keep track of connected clients
    clients = []

    while True:
        # Accept incoming connection
        client_socket, _ = server_socket.accept()
        # Add client socket to the list of clients
        clients.append(client_socket)
        # Start a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, clients))
        client_thread.start()

def update_windowtitle_thread():
    while True:
        subprocess.Popen(["title", f"Connected Clients: {len(clients)} - Users in Users list: {len(users)} - Socket-Username Combos: {len(client_user_combo)} - Version: {SERVER_VERSION} - Type: {SERVER_TYPE}"], shell=True)
        time.sleep(5)

if __name__ == "__main__":
    t1 = threading.Thread(target=update_windowtitle_thread).start()
    main()