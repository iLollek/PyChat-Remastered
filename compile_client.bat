python -m PyInstaller --noconfirm --onefile --windowed --icon "PyChatREM.ico" --add-data "Assets/Graphics/PyChatREM.ico;Assets/Graphics/" --add-data "Assets/Graphics/PyChatREM.png;Assets/Graphics/" --add-data "Assets/Sounds/alt_join.mp3;Assets/Sounds/" --add-data "Assets/Sounds/alt_leave.mp3;Assets/Sounds/" --add-data "Assets/Sounds/alt_notification.mp3;Assets/Sounds/" --add-data "Assets/Sounds/alt_send.mp3;Assets/Sounds/" --add-data "Assets/Sounds/icq_join.mp3;Assets/Sounds/" --add-data "Assets/Sounds/icq_notification.mp3;Assets/Sounds/" --add-data "Assets/Sounds/icq_send.mp3;Assets/Sounds/" --add-data "Assets/Sounds/join.wav;Assets/Sounds/" --add-data "Assets/Sounds/leave.wav;Assets/Sounds/" --add-data "Assets/Sounds/notification.mp3;Assets/Sounds/" --add-data "Assets/Sounds/send_message.mp3;Assets/Sounds/"  "client.py"
