from playsound import playsound
import threading

class SoundModule:

    BaseFilePath = "Assets\\Sounds"

    def play_sound_user_join(soundpack: str):
        """Plays the selected sound for User Join. If the value is not found (i.e. broken config File) it will play the default."""
        raise NotImplementedError
    
    def play_sound_user_leave(soundpack: str):
        """Plays the selected sound for User Leave. If the value is not found (i.e. broken config File) it will play the default."""
        raise NotImplementedError
    
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
        return self.config.get(key, 'default')

if __name__ == "__main__":
    SoundModule.play_sound_message_sent("AOL")