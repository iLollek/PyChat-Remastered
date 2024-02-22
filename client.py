import socket
import threading
import sys
import os
import customtkinter as tk
import logging
import signal
import time
from datetime import datetime

import GUI

from ClientModules import SoundModule, AppConfigParser, Popup, NetworkManager, LogFileClear, Installer

logging.basicConfig(filename='app.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

VERSION = "v0.1"
CLIENT_TYPE = "unregistered"
USERNAME = os.getlogin()
HEADERS = {"client-type" : CLIENT_TYPE, "VERSION" : VERSION, "username" : USERNAME}

users = []

def resource_path():
    """ Change CWD to the AppData path """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        os.chdir(base_path)
    except Exception:
        base_path = os.path.abspath(".")
        os.chdir(base_path)

if getattr(sys, 'frozen', False):
   program_directory = os.path.dirname(os.path.abspath(sys.executable))
   ENV = "PROD" # Run in .exe File. Assume it's a production environment.
   if Installer.check_if_first_time_run(program_directory) == True:
       print(f'No app.config found, the program is probably being run the first time. Creating Desktop shortcut...')
       logging.warn(f'No app.config found, the program is probably being run the first time. Creating Desktop shortcut...')
       Popup.show_info_box(f'PyChat-Remastered - Welcome!', f'Thank you for installing PyChat-Remastered!\n\nThe program will now create a shortcut on your Desktop.\nPlease review the content of your app.config - A Server should be preconfigured and point to xcloud.ddns.net on Port 5555.\n\nPyChat-Remastered & the original PyChat are Products of iLollek. All rights reserved.')
       Installer.create_desktop_shortcut(program_directory)
   resource_path()
   AppConfigParser.create_config(program_directory)
else:
   program_directory = os.path.dirname(os.path.abspath(__file__))
   ENV = "DEV" # Run in .py File. Assume it's a development environment.
   AppConfigParser.create_config(program_directory)

def timestamp():
    now = datetime.now()
    formatted_timestamp = now.strftime("%d %b %Y - %H:%M:%S")
    return formatted_timestamp

def log_chatmessage(message: str):
    """Logs a Chatmessage if log_chatmessages in app.config is set to True. Filters out Replies."""

    if message.startswith(f'ACK=') == False:
        if parser.get_config("log_chatmessages") == "True":
            f = open(f'{program_directory}\\chat.log', 'a')
            f.write(f'[{timestamp()}] {message}\n')
            f.close()

def get_app_config():
    """Starts the AppConfigParser and reads it."""
    global appconfig
    appconfig = AppConfigParser(f'{program_directory}\\app.config')
    appconfig.parse_config()
get_app_config()

def fill_userbox():
    """Fills the Userbox using the global "users" List."""

    GUI.App.clear_userbox(root)

    for user in users:
        GUI.App.insert_into_userbox(root, user)

def close():
    """Closes the PyChat-Remastered Client."""
    print(f'Closing PyChat-Remastered...')
    logging.info(f'Closing PyChat-Remastered...')
    print(f'The GUI needed {ticks} Ticks to start.')
    logging.info(f'The GUI needed {ticks} Ticks to start.')
    try:
        client_socket.send(f'REQ=LEAVE'.encode())
    except socket.error as e:
        pass
    except NameError as e:
        pass
    os.kill(os.getpid(), signal.SIGTERM) # This is the last line that gets executed.

def run_gui():
    global root
    GUI.get_theme()
    root = tk.CTk()
    app = GUI.App(root, get_message_from_user)
    root.mainloop()
    print("Main Window Closed.")
    logging.info("Main Window Closed.")
    close()

import logging

class PyChatREMProtocol:
    
    class EventHandler:

        def user_join_event(client_socket: socket):
            """Handles a User join Event. (%USERJOIN%)"""

            logging.info("User joined event")
            SoundModule.play_sound_user_join(appconfig.get_config("soundpack"))
            PyChatREMProtocol.RequestSender.request_userlist(client_socket)

        def user_leave_event(client_socket: socket):
            """Handles a User leave Event. (%USERLEAVE%)"""

            logging.info("User leave event")
            SoundModule.play_sound_user_leave(appconfig.get_config("soundpack"))
            PyChatREMProtocol.RequestSender.request_userlist(client_socket)

        def on_message_received(message: str):
            """Checks if the Message has been sent by the User himself. 
            If True, it doesn't play a sound. If False, it plays a Sound."""

            logging.info("Message received")
            if message.startswith(USERNAME) == False:
                SoundModule.play_sound_message_received(appconfig.get_config("soundpack"))
        
        def on_message_sent():
            """Plays a sound when a Message is sent."""

            logging.info("Message sent")
            SoundModule.play_sound_message_sent(appconfig.get_config("soundpack"))

    class RequestReceiver:

        def response_userlist(request: str):
            global users
            """Parses the ACK=USERS reply from the Server and fills it into the "users" global List."""
            logging.info("Received user list response")
            users.clear()
            request = request.split("$")
            users = request[1].split("%")
            fill_userbox()

        def assign_request_to_method(client_socket: socket, request: str):
            """Assigns a Request to the approriate Method for Handling."""
            logging.info("Assigning request to method")
            if "ACK=USERS" in request:
                PyChatREMProtocol.RequestReceiver.response_userlist(request)  

    class RequestSender:

        def request_userlist(client_socket: socket) -> bool:
            """Sends an "Request Userlist" Request to the Server.
            
            Args:
                - client_socket (socket): The Client Socket Stream to send the Request

            Returns:
                - success (bool): True if the Server Accepted, False otherwise"""
            
            logging.info("Sending user list request")
            try:
                client_socket.send(f'REQ=GETUSERS'.encode())
                return True
            except socket.error as e:
                print(f'Socket Exception: {e}')
                logging.error(f'Socket Exception: {e}')
                return False
            

        def request_authentification(client_socket: socket, headers: str) -> bool:
            """Sends an Authentification Request to the Server.
            
            Args:
                - client_socket (socket): The Client Socket Stream to send the Request
                - headers (str): The Standardized Headers for Unauthorized Clients
            
            Returns:
                - success (bool): True if the Server Accepted, False otherwise"""

            logging.info("Sending authentication request")
            try:
                client_socket.send(f'REQ=AUTH${str(HEADERS)}'.encode())
                reply = client_socket.recv(512).decode()
                if reply == "ACK=OK":
                    return True
                else:
                    return False
            except socket.error as e:
                print(f'Socket Exception: {e}')
                logging.error(f'Socket Exception: {e}')
                return False


    def receive_messages(client_socket: socket):
        PyChatREMProtocol.RequestSender.request_userlist(client_socket)
        while True:
            try:
                # Receive message from server
                message = client_socket.recv(1024).decode()

                print(f'Received Message: {message}')

                if str(message).startswith("[SERVER]") == True:
                    # This is a Server Announcement / Broadcast.
                    if str(message).count('%') == 2:
                        # The Message has 2 Percent-Signs. This could mean that we have some Event.
                        if "%USERJOIN%" in message:
                            message = str(message).replace("%USERJOIN%", "")
                            if USERNAME not in message:
                                threading.Thread(target=PyChatREMProtocol.EventHandler.user_join_event, args=(client_socket,)).start()
                        elif "%USERLEAVE%" in message:
                            message = str(message).replace("%USERLEAVE%", "")
                            threading.Thread(target=PyChatREMProtocol.EventHandler.user_leave_event, args=(client_socket,)).start()

                if str(message) == "Disconnected from Server":
                    root.title(f'PyChat Remastered - Not Connected!')

                if str(message).startswith("ACK=") == False:
                    GUI.App.insert_into_chatbox(root, message)
                    threading.Thread(target=PyChatREMProtocol.EventHandler.on_message_received, args=(message,)).start()
                    log_chatmessage(str(message))
                else:
                    PyChatREMProtocol.RequestReceiver.assign_request_to_method(client_socket, message)
                

                if not message:
                    # If no message received, close connection
                    client_socket.close()
                    print(f'Disconnected from server.')
                    logging.warn(f'Disconnected from server.')
                    break
                
            except socket.error as e:
                print(f"Error: {e}")
                # If an error occurs, close connection
                client_socket.close()
                print("Disconnected from server.")
                logging.warn(f'Disconnected from server.')
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
                Popup.show_error_box("PyChat-Remastered - Server Authentification Error!", f"The Server you have Connected to is active, however it denied your Request to join the Chatroom. This might be because of your Clients Settings, Configuration or Version.\n\nServer Address: {parser.get_config('server_address')}\nServer Port: {parser.get_config('server_port')}\nClient-Type: {HEADERS['client-type']}\nClient-Version: {HEADERS['VERSION']}")
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
            logging.error(f'Error: {e}')
            root.title(f'PyChat Remastered - Not Connected!')

def get_message_from_user():
    """Grabs the Message in the tkinter Input (Entry). Is Called via a Callback from the GUI."""
    # Here you can implement a function to get a message from the user
    # For simplicity, we'll just return a hardcoded message for now
    user_message_content = GUI.App.get_entry_content(root)
    if len(user_message_content) != 0:
        try:
            client_socket.send(f'{USERNAME}: {user_message_content}'.encode())
            threading.Thread(target=SoundModule.play_sound_message_sent, args=(appconfig.get_config("soundpack"),)).start()
        except socket.error as e:
            print(f'Error: {e}')
            logging.error(f'Error: {e}')
            client_socket.close()
            root.title(f'PyChat Remastered - Not Connected!')

if __name__ == "__main__":
    parser = AppConfigParser(f'{program_directory}\\app.config')
    parser.parse_config()
    theme = parser.get_config("theme")
    soundpack = parser.get_config("soundpack")

    LogFileClear.clear_log_if_needed("app.log", "25KB")

    server_ip = NetworkManager.get_ip_address(parser.get_config("server_address"))
    print(f'Server Address (from app.config): {parser.get_config("server_address")} -> Server IP: {server_ip}')
    logging.info(f'Server Address (from app.config): {parser.get_config("server_address")} -> Server IP: {server_ip}')

    ticks = 0
    gui_thread = threading.Thread(target=run_gui).start()
    while True:
        try:
            PyChatREMProtocol.connect_to_server(server_ip, int(parser.get_config("server_port")))
        except NameError as e:
            ticks += 1
        except socket.error as e:
            Popup.show_error_box(f'PyChat-Remastered - Unable to get Server IP', f'The NetworkManager is unable to resolve the Domain you specified in app.config! Are you sure that it is set correctly?\n\nServer Name: {parser.get_config("server_address")}')
            close()
