import asyncio
import os
import threading
import tkinter as tk
from bot import My_Bot
from dotenv import load_dotenv


class GUI:
    def __init__(self):
        load_dotenv()
        self.loop = None
        self.root = tk.Tk()
        self.root.title("Glitch Character Management")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.button = tk.Button(
            self.root,
            text="Start",
            command=self.run,
            width=10,
            pady=10,
            font=("Arial", 16, "bold"),
        )
        self.label = tk.Label(
            self.root,
            text="Idle",
            anchor=tk.CENTER,
            width=20,
            bd=3,
            font=("Arial", 16, "bold"),
            justify=tk.CENTER,
        )

        self.bot = None

    def startup(self):
        self.bot = My_Bot(self.on_ready, [self.label, self.button])

        # Start the GUI event loop
        self.label.pack(
            padx=20,
            pady=10,
        )
        self.button.pack(pady=10)
        self.root.mainloop()

    def run(self):

        self.label.configure(text="Starting...")
        self.button.pack_forget()
        self.loop = asyncio.new_event_loop()
        self.bot.initialize(self.loop)
        t1 = threading.Thread(target=self.bot.bot.run, args=(os.getenv("TOKEN"),))
        t1.start()

    def close(self):
        try:
            self.label.configure(text="Shutting down...")
            self.button.pack_forget()
            asyncio.run_coroutine_threadsafe(self.bot.close(), self.loop)
            self.label.configure(text="Idle")
            self.button.configure(text="RUN", command=self.run)
            self.button.pack(pady=10)
        except Exception as e:
            print(e)

    def on_closing(self):
        self.close()
        self.root.destroy()

    def on_ready(self, label, button):
        label.configure(text="Running")
        button.configure(text="STOP", command=self.close)
        button.pack(pady=10)


GUI().startup()
