from playsound import playsound
import threading
from tkinter import messagebox
import tkinter as tk
import os
import socket
import datetime
import logging
from win32com.client import Dispatch

class SoundModule:

    BaseFilePath = "Assets\\Sounds"

    def play_sound_user_join(soundpack: str):
        """Plays the selected sound for User Join. If the value is not found (i.e. broken config File) it will play the default."""
        if soundpack == "AOL":
            threading.Thread(target=playsound(f"{SoundModule.BaseFilePath}\\alt_join.mp3"))
        elif soundpack == "ICQ":
            threading.Thread(target=playsound(f"{SoundModule.BaseFilePath}\\icq_join.mp3"))
        else:
            threading.Thread(target=playsound(f"{SoundModule.BaseFilePath}\\join.wav"))
    
    def play_sound_user_leave(soundpack: str):
        """Plays the selected sound for User Leave. If the value is not found (i.e. broken config File) it will play the default."""
        if soundpack == "AOL":
            threading.Thread(target=playsound(f"{SoundModule.BaseFilePath}\\alt_leave.mp3"))
        elif soundpack == "ICQ":
            threading.Thread(target=playsound(f"{SoundModule.BaseFilePath}\\leave.wav"))
        else:
            threading.Thread(target=playsound(f"{SoundModule.BaseFilePath}\\leave.wav"))
    
    def play_sound_message_sent(soundpack: str):
        """Plays the selected sound for sending a Message. If the value is not found (i.e. broken config File) it will play the default."""

        if soundpack == "AOL":
            threading.Thread(target=playsound(f"{SoundModule.BaseFilePath}\\alt_send.mp3"))
        elif soundpack == "ICQ":
            threading.Thread(target=playsound(f"{SoundModule.BaseFilePath}\\icq_send.mp3"))
        else:
            threading.Thread(target=playsound(f"{SoundModule.BaseFilePath}\\send_message.mp3"))
    
    def play_sound_message_received(soundpack: str):
        """Plays the selected sound for receiving a Message. If the value is not found (i.e. broken config File) it will play the default."""

        if soundpack == "AOL":
            threading.Thread(target=playsound(f"{SoundModule.BaseFilePath}\\alt_notification.mp3"))
        elif soundpack == "ICQ":
            threading.Thread(target=playsound(f"{SoundModule.BaseFilePath}\\icq_notification.mp3"))
        else:
            threading.Thread(target=playsound(f"{SoundModule.BaseFilePath}\\notification.mp3"))
    
class AppConfigParser:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = {}

    def parse_config(self):
        with open(self.config_file, 'r') as f:
            for line in f:
                if ':' in line:
                    key, value = line.strip().split(':')
                    self.config[key.strip()] = value.strip()

    def get_config(self, key):
        if key == "server_port":
            return self.config.get(key, 5555)
        else:
            return self.config.get(key, 'default')
        
    def create_config(path: str):
        """Creates an app.config if it doesn't exist at the path"""
        if not os.path.exists(f'{path}\\app.config'):
            with open(f'{path}\\app.config', 'w') as f:
                f.write("""# This is your app.config - You can set themes, soundpacks, the Server Address & Port and other stuff here.
# 
# themes: default, dark-blue, green
# soundpacks: default, AOL, ICQ

theme : default
soundpack : default
server_address : xcloud.ddns.net
server_port : 5555
log_chatmessages : False""")
        else:
            print(f'app.config already exists at {path}\\app.config')
            logging.info(f'app.config already exists at {path}\\app.config')

class Installer:
    def check_if_first_time_run(program_directory: str) -> bool:
        """Checks if the Program is being run for the first time by checking if app.config exists at program_directory"""
        config_file_path = os.path.join(program_directory, 'app.config')
        return not os.path.exists(config_file_path)
    
    def create_desktop_shortcut(program_directory: str) -> bool:
        # Create a desktop shortcut with the icon
        path = os.path.join(os.environ['USERPROFILE'], 'Desktop', f'PyChat-Remastered.lnk')
        target = f"{program_directory}\\client.exe"  # The shortcut target file or folder
        work_dir = program_directory  # The parent folder of your file

        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = work_dir
        shortcut.IconLocation = f"{program_directory}\\client.exe"
        shortcut.save()

class LogFileClear:

    def clear_log_if_needed(log_file_path, max_file_size):
        if os.path.exists(log_file_path):
            # Get the size of the log file in bytes
            file_size = os.path.getsize(log_file_path)
            
            # Convert max file size to bytes if it's given in KB or MB
            if max_file_size.endswith('KB'):
                max_file_size = int(max_file_size[:-2]) * 1024
            elif max_file_size.endswith('MB'):
                max_file_size = int(max_file_size[:-2]) * 1024 * 1024
            else:
                max_file_size = int(max_file_size)
            
            if file_size > max_file_size:
                # Clear the log file
                with open(log_file_path, 'w') as log_file:
                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    log_file.write(f"APPLOG CLEARED AT ({current_time})\n")
                print(f"Log file '{log_file_path}' cleared at {current_time}.")
            else:
                print(f"Log file '{log_file_path}' is within size limits.")
        else:
            print(f"Log file '{log_file_path}' not found.")



class Popup:
    def show_info_box(title, body):
        """Shows a tkinter Info box with a Info Icon."""
        # Create a Tkinter window (optional if you already have a Tkinter window created)
        window = tk.Tk()
        window.withdraw()  # Hide the window to only show the message box

        # Show the message box with the given title and body
        messagebox.showinfo(title, body)

        # Destroy the Tkinter window (optional if you already have a Tkinter window created)
        window.destroy()
    
    def show_error_box(title, body):
        """Shows a tkinter Info box with a Error Icon."""
        # Create a Tkinter window (optional if you already have a Tkinter window created)
        window = tk.Tk()
        window.withdraw()  # Hide the window to only show the message box

        # Show the message box with the given title and body
        messagebox.showerror(title, body)

        # Destroy the Tkinter window (optional if you already have a Tkinter window created)
        window.destroy()

    def show_warning_box(title, body):
        """Shows a tkinter Info box with a Warning Icon."""
        # Create a Tkinter window (optional if you already have a Tkinter window created)
        window = tk.Tk()
        window.withdraw()  # Hide the window to only show the message box

        # Show the message box with the given title and body
        messagebox.showwarning(title, body)

        # Destroy the Tkinter window (optional if you already have a Tkinter window created)
        window.destroy()

class NetworkManager:
    def get_ip_address(input_str: str) -> str:
        """Returns the IP Address of a Fully Qualified Domain Name (FQDN), if input_str is a FQDN. Returns the IP back out otherwise.
        
        Args:
            - input_str (str): The IP Address or FQDN
            
        Returns:
            - IP Address (str)"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            socket.inet_aton(input_str)
            return input_str
        except OSError:
            return socket.gethostbyname(input_str)

if __name__ == "__main__":
    AppConfigParser.create_config(r"C:\Users\loris\Desktop\Coding\PyChat-Remastered\dist")