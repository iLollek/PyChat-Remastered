import customtkinter as tk
import tkinter.font as tkFont

from functools import partial

class App:
    def __init__(self, root, send_message_callback):
        global GListBox_146
        global GListBox_82
        global GLineEdit_267

        # Send Message Method Callback
        self.send_message_callback = send_message_callback

        # setting title
        root.title("PyChat Remastered - Starting...")

        # setting icon
        root.iconbitmap(f"Assets\\Graphics\\PyChatREM.ico")

        # setting window size
        root.geometry("900x600")

        # making the window resizable
        root.resizable(width=True, height=True)

        GLineEdit_267 = tk.CTkEntry(root, width=1159, height=41)
        GLineEdit_267["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times', size=10)
        GLineEdit_267["font"] = ft
        GLineEdit_267["fg"] = "#333333"
        GLineEdit_267["justify"] = "center"
        GLineEdit_267["text"] = "Entry"
        GLineEdit_267.grid(row=1, column=0, padx=20, pady=20, sticky="ew")

        GButton_67 = tk.CTkButton(root, width=158, height=45, text="Send Message", command=self.GButton_67_command)
        GButton_67["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times', size=10)
        GButton_67["font"] = ft
        GButton_67["fg"] = "#000000"
        GButton_67["justify"] = "center"
        GButton_67["text"] = "Button"
        GButton_67.grid(row=1, column=1, padx=20, pady=20, sticky="e")
        GButton_67["command"] = self.GButton_67_command

        GListBox_82 = tk.CTkTextbox(root, width=1100, height=629, font=tk.CTkFont(family="system", size=10))
        GListBox_82["borderwidth"] = "1px"
        font = tk.CTkFont(family="system", size=10)
        ft = tkFont.Font(family='Times', size=10)
        GListBox_82["font"] = ft
        GListBox_82["fg"] = "#333333"
        GListBox_82["justify"] = "center"
        GListBox_82.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        GListBox_146 = tk.CTkTextbox(root, width=231, height=630, font=tk.CTkFont(family="system", size=10))
        GListBox_146["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times', size=10)
        GListBox_146["font"] = ft
        GListBox_146["fg"] = "#333333"
        GListBox_146["justify"] = "center"
        GListBox_146.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # configure row and column weights to allow resizing
        root.grid_rowconfigure(0, weight=2)
        root.grid_columnconfigure(0, weight=2)

        root.bind('<Return>',lambda event:self.GButton_67_command())

        GListBox_146.configure(state='disabled')
        GListBox_82.configure(state='disabled')

    def insert_into_chatbox(self, text: str):
        """Inserts a given String (text) into the end Index of the Main Chatbox and scrolls to the bottom"""
        GListBox_82.configure(state='normal')
        GListBox_82.insert("end", text + "\n")
        GListBox_82.yview_moveto(1)
        GListBox_82.configure(state='disabled')

    def insert_into_userbox(self, username: str):
        """Inserts a User at the end Index of the Userbox"""
        GListBox_146.configure(state='normal')
        GListBox_146.insert("end", username + "\n")
        GListBox_146.configure(state='disabled')

    def clear_userbox(self):
        GListBox_146.configure(state='normal')
        GListBox_146.delete("0.0", "end")
        GListBox_146.configure(state='disabled')

    def clear_chatbox(self):
        GListBox_82.configure(state='normal')
        GListBox_82.delete("0.0", "end")
        GListBox_82.configure(state='disabled')

    def GButton_67_command(self):
        print("Send Message")
        if self.send_message_callback:
            self.send_message_callback()

    def get_entry_content(self):
        CONTENT = GLineEdit_267.get()
        GLineEdit_267.delete(0, "end")
        return CONTENT

if __name__ == "__main__":
    root = tk.CTk()
    app = App(root, None)
    root.mainloop()
