import socket
import threading
import sys
import os
import customtkinter as tk
import logging
import signal
import time

import GUI

from ClientModules import SoundModule, AppConfigParser

# TODO: Check Hearbeat Timeout (Maximum Time) - Interval?

VERSION = "v0.1"
CLIENT_TYPE = "unregistered"
USERNAME = os.getlogin()
HEADERS = {"client-type" : CLIENT_TYPE, "VERSION" : VERSION, "username" : USERNAME}

users = []

if getattr(sys, 'frozen', False):
   program_directory = os.path.dirname(os.path.abspath(sys.executable))
   ENV = "PROD" # Run in .exe File. Assume it's a production environment.
else:
   program_directory = os.path.dirname(os.path.abspath(__file__))
   ENV = "DEV" # Run in .py File. Assume it's a development environment.
os.chdir(program_directory)

def get_app_config():
    """Starts the AppConfigParser and reads it."""
    global appconfig
    appconfig = AppConfigParser("app.config")
    appconfig.parse_config()
get_app_config()

def fill_userbox():
    """Fills the Userbox using the global "users" List."""

    GUI.App.clear_userbox(root)

    for user in users:
        GUI.App.insert_into_userbox(root, user)

def close():
    """Closes the PyChat-Remastered Client."""
    print(f'Closing PyChat Remastered...')
    print(f'The GUI needed {ticks} Ticks to start.')
    try:
        client_socket.send(f'REQ=LEAVE'.encode())
    except socket.error as e:
        pass
    os.kill(os.getpid(), signal.SIGTERM) # This is the last line that gets executed.

def run_gui():
    global root
    root = tk.CTk()
    app = GUI.App(root, get_message_from_user)
    root.mainloop()
    print("Main Window Closed.")
    close()

class PyChatREMProtocol:
    
    class EventHandler:

        def user_join_event(client_socket: socket):
            """Handles a User join Event. (%USERJOIN%)"""

            SoundModule.play_sound_user_join(appconfig.get_config("soundpack"))
            PyChatREMProtocol.RequestSender.request_userlist(client_socket)

        def user_leave_event(client_socket: socket):
            """Handles a User leave Event. (%USERLEAVE%)"""

            SoundModule.play_sound_user_leave(appconfig.get_config("soundpack"))
            PyChatREMProtocol.RequestSender.request_userlist(client_socket)

        def on_message_received(message: str):
            """Checks if the Message has been sent by the User himself. 
            If True, it doesn't play a sound. If False, it plays a Sound."""

            if message.startswith(USERNAME) == False:
                SoundModule.play_sound_message_received(appconfig.get_config("soundpack"))
        
        def on_message_sent():
            """Plays a sound when a Message is sent."""

            SoundModule.play_sound_message_sent(appconfig.get_config("soundpack"))

    class RequestReceiver:

        def response_userlist(request: str):
            global users
            """Parses the ACK=USERS reply from the Server and fills it into the "users" global List."""
            users.clear()
            request = request.split("$")
            users = request[1].split("%")
            fill_userbox()

        def assign_request_to_method(client_socket: socket, request: str):
            """Assigns a Request to the approriate Method for Handling."""
            if "ACK=USERS" in request:
                PyChatREMProtocol.RequestReceiver.response_userlist(request)
                

    class RequestSender:

        def request_userlist(client_socket: socket) -> bool:
            """Sends an "Request Userlist" Request to the Server.
            
            Args:
                - client_socket (socket): The Client Socket Stream to send the Request

            Returns:
                - success (bool): True if the Server Accepted, False otherwise"""
            
            try:
                client_socket.send(f'REQ=GETUSERS'.encode())
                return True
            except socket.error as e:
                print(f'Socket Exception: {e}')
                return False
            

        def request_authentification(client_socket: socket, headers: str) -> bool:
            """Sends an Authentification Request to the Server.
            
            Args:
                - client_socket (socket): The Client Socket Stream to send the Request
                - headers (str): The Standardized Headers for Unauthorized Clients
            
            Returns:
                - success (bool): True if the Server Accepted, False otherwise"""

            try:
                client_socket.send(f'REQ=AUTH${str(HEADERS)}'.encode())
                reply = client_socket.recv(512).decode()
                if reply == "ACK=OK":
                    return True
                else:
                    return False
            except socket.error as e:
                print(f'Socket Exception: {e}')
                return False

    def receive_messages(client_socket: socket):
        PyChatREMProtocol.RequestSender.request_userlist(client_socket)
        while True:
            try:
                # Receive message from server
                message = client_socket.recv(1024).decode()

                print(f'Received Message: {message}') # TODO: Delete this line later?

                if str(message).startswith("[SERVER]") == True:
                    # This is a Server Announcement / Broadcast.
                    if str(message).count('%') == 2:
                        # The Message has 2 Percent-Signs. This could mean that we have some Event.
                        if "%USERJOIN%" in message:
                            message = str(message).replace("%USERJOIN%", "")
                            threading.Thread(target=PyChatREMProtocol.EventHandler.user_join_event, args=(client_socket,)).start()
                        elif "%USERLEAVE%" in message:
                            message = str(message).replace("%USERLEAVE%", "")
                            threading.Thread(target=PyChatREMProtocol.EventHandler.user_leave_event, args=(client_socket,)).start()

                if str(message) == "Disconnected from Server":
                    root.title(f'PyChat Remastered - Not Connected!')

                if str(message).startswith("ACK=") == False:
                    GUI.App.insert_into_chatbox(root, message)
                    threading.Thread(target=PyChatREMProtocol.EventHandler.on_message_received, args=(message,)).start()
                else:
                    PyChatREMProtocol.RequestReceiver.assign_request_to_method(client_socket, message)
                

                if not message:
                    # If no message received, close connection
                    client_socket.close()
                    print("Disconnected from server.")
                    break
                
            except socket.error as e:
                print(f"Error: {e}")
                # If an error occurs, close connection
                client_socket.close()
                print("Disconnected from server.")
                root.title(f'PyChat Remastered - Not Connected!')
                break

    def connect_to_server(domain_or_ip="localhost", port=5555):
        """This Initiates the Connection to the Server using the PyChat-REM Protocol.
        
        Args:
            - domain_or_ip (str): The FQDN or IP Address of the Server (defaults to localhost)
            - port (int): The TCP Port of the Server (defaults to 5555)"""
        try:
            global client_socket
            root.title(f'PyChat Remastered - Connecting...')
            # Create socket
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Connect to server
            client_socket.connect((domain_or_ip, port))
            authentification_success = PyChatREMProtocol.RequestSender.request_authentification(client_socket, HEADERS)
            if authentification_success == False:
                # TODO: ErrorBox
                close()
            else:
                root.title(f'PyChat Remastered - Connected!')

            # Start a new thread to receive messages from the server
            receive_thread = threading.Thread(target=PyChatREMProtocol.receive_messages, args=(client_socket,))
            receive_thread.start()

            while True:
                # This is the Heartbeat loop
                time.sleep(15)
                print(f'Sending Heartbeat...')
                client_socket.send(f'REQ=HEARTBEAT'.encode())
                print(f'Sent Heartbeat!')
        except socket.error as e:
            print(f"Error: {e}")
            root.title(f'PyChat Remastered - Not Connected!')

def get_message_from_user():
    """Grabs the Message in the tkinter Input (Entry). Is Called via a Callback from the GUI."""
    # Here you can implement a function to get a message from the user
    # For simplicity, we'll just return a hardcoded message for now
    user_message_content = GUI.App.get_entry_content(root)
    if user_message_content != None: # TODO: None or string.empty()
        try:
            client_socket.send(f'{USERNAME}: {user_message_content}'.encode())
            threading.Thread(target=SoundModule.play_sound_message_sent, args=(appconfig.get_config("soundpack"),)).start()
        except socket.error as e:
            print(f'Error: {e}')
            client_socket.close()
            root.title(f'PyChat Remastered - Not Connected!')

if __name__ == "__main__":
    parser = AppConfigParser("app.config")
    parser.parse_config()
    theme = parser.get_config("theme")
    soundpack = parser.get_config("soundpack")

    ticks = 0
    gui_thread = threading.Thread(target=run_gui).start()
    while True:
        try:
            PyChatREMProtocol.connect_to_server()
        except NameError as e:
            ticks += 1
