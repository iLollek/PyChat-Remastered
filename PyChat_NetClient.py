import socket
import threading

def main():
    try:
        # Create socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to server
        client_socket.connect(('localhost', 5555))

        # Start a new thread to receive messages from the server

        while True:
            try:
                # Get message from user
                message = get_message_from_user()
                # Send message to server
                client_socket.send(message.encode())
            except Exception as e:
                print(f"Error: {e}")
                # If an error occurs, close connection
                client_socket.close()
                break
    except Exception as e:
        print(f"Error: {e}")