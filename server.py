import socket
import threading
import sys
import ast
import subprocess
import time
import logging
from datetime import datetime
import asyncio
import websockets

# WebSocket clients list
websocket_clients = set()

def get_outbound_local_ip():
    """Gets the Verified & Used outbound IP-Address for a LAN Environment"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

SERVER_IP = get_outbound_local_ip()
SERVER_PORT = 5555
WS_PORT = 8765  # WebSocket port

SERVER_TYPE = "unregistered"
SERVER_VERSION = "v0.1"
SERVER_ALLOW_FOREIGN_VERSIONS = True

users = []
client_user_combo = {}
clients = []

SERVER_CONFIG = {
    "log_chatmessages": True
}

def timestamp():
    now = datetime.now()
    formatted_timestamp = now.strftime("%d %b %Y - %H:%M:%S")
    return formatted_timestamp

def log_chatmessage(message: str):
    """Logs a Chatmessage if log_chatmessages in SERVER_CONFIG is set to True. Filters out Requests."""
    if not message.startswith('REQ='):
        if SERVER_CONFIG["log_chatmessages"]:
            with open('server_chat.log', 'a') as f:
                f.write(f'[{timestamp()}] {message}\n')

def request_handler(client_socket, request: str, clients) -> bool:
    """Handle requests from TCP clients."""
    if "REQ=AUTH" in request:
        request = request.split("$")
        headers = ast.literal_eval(request[1])
        if SERVER_TYPE != headers["client-type"]:
            return False
        if SERVER_VERSION != headers["VERSION"]:
            if not SERVER_ALLOW_FOREIGN_VERSIONS:
                return False
        client_socket.send("ACK=OK".encode())
        client_user_combo[client_socket] = headers["username"]
        users.append(headers["username"])
        broadcast_announcement(clients, f'{headers["username"]} joined the Chatroom. %USERJOIN%')
        log_chatmessage(f'{headers["username"]} joined the Chatroom.')
        return True

    elif "REQ=HEARTBEAT" in request:
        client_socket.send('ACK=OK'.encode())
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
        user_string = "%".join(users)
        client_socket.send(f"ACK=USERS${user_string}".encode())
        return True

def broadcast_announcement(clients, message):
    """Broadcasts a message to all TCP clients."""
    for c in clients:
        if not str(message).startswith("REQ="):
            c.send(f'[SERVER] {message}'.encode())

def handle_client(client_socket, clients):
    """Handles TCP client connections."""
    print(f"New connection: {client_socket}")
    while True:
        try:
            message = client_socket.recv(1024).decode()
            print(f"Message: {message}")
            log_chatmessage(message)

            if message.startswith("REQ="):
                exit_code = request_handler(client_socket, message, clients)
                if exit_code is False:
                    client_socket.close()
                    clients.remove(client_socket)
                    print(f"Connection closed: {client_socket}")
                    break

            if not message:
                client_socket.close()
                clients.remove(client_socket)
                print(f"Connection closed: {client_socket}")
                break

            for c in clients:
                if not message.startswith("REQ="):
                    c.send(message.encode())
            # Broadcast message to WebSocket clients
            asyncio.run(broadcast_to_websocket_clients(message))

        except Exception as e:
            print(f"Error: {e}")
            client_socket.close()
            clients.remove(client_socket)
            if client_user_combo[client_socket] in users:
                broadcast_announcement(clients, f'{client_user_combo[client_socket]} left the Chatroom. ({e})')
                log_chatmessage(f'{client_user_combo[client_socket]} left the Chatroom. ({e})')
                users.remove(client_user_combo[client_socket])
            print(f"Connection closed: {client_socket}")
            break

async def websocket_handler(websocket, path):
    """Handles WebSocket client connections."""
    print(f"New WebSocket connection: {websocket.remote_address}")
    websocket_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"Message from WebSocket client: {message}")
            log_chatmessage(message)
            # Broadcast to both TCP and WebSocket clients
            broadcast_announcement(clients, message)
            await broadcast_to_websocket_clients(message)
    except websockets.ConnectionClosed:
        print(f"WebSocket connection closed: {websocket.remote_address}")
    finally:
        websocket_clients.remove(websocket)

async def broadcast_to_websocket_clients(message: str):
    if websocket_clients:  # Ensure there are connected clients
        # Create tasks for each websocket client send operation
        await asyncio.wait([asyncio.create_task(ws.send(f"[SERVER] {message}")) for ws in websocket_clients])

def main():
    global clients
    # Start TCP server
    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server_socket.bind((SERVER_IP, SERVER_PORT))
    tcp_server_socket.listen(5)
    print("TCP server is listening for connections...")

    # Start WebSocket server
    loop = asyncio.get_event_loop()
    start_server = websockets.serve(websocket_handler, SERVER_IP, WS_PORT)

    # Create TCP client handling thread
    tcp_thread = threading.Thread(target=tcp_server_loop, args=(tcp_server_socket,))
    tcp_thread.start()

    # Run the WebSocket server
    loop.run_until_complete(start_server)
    loop.run_forever()

def tcp_server_loop(server_socket):
    """Handles incoming TCP client connections."""
    global clients
    clients = []
    while True:
        client_socket, _ = server_socket.accept()
        clients.append(client_socket)
        client_thread = threading.Thread(target=handle_client, args=(client_socket, clients))
        client_thread.start()

if __name__ == "__main__":
    main()
