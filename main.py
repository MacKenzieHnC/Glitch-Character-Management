# Python 3.10.3
import asyncio
import os
import threading
import discord  # py-cord 2.6.1
from dotenv import load_dotenv
import tkinter as tk


class My_Bot:
    def __init__(self) -> None:
        # Set up bot
        self.loop = None
        load_dotenv()  # load all the variables from the env file
        self.bot = None

    def run(self):

        label.configure(text="Starting...")
        button.pack_forget()
        self.loop = asyncio.new_event_loop()
        self.bot = discord.Bot(loop=self.loop)

        for cog in ["cogs.game", "cogs.costs", "cogs.char", "cogs.session"]:
            self.bot.load_extension(cog)

        @self.bot.event
        async def on_ready():
            label.configure(text="Running")
            button.configure(text="STOP", command=self.close)
            button.pack(pady=10)

        t1 = threading.Thread(target=self.bot.run, args=(os.getenv("TOKEN"),))
        t1.start()

    async def internal_close(self):
        self.bot.clear()
        await self.bot.close()
        exit()

    def close(self):
        try:
            label.configure(text="Shutting down...")
            button.pack_forget()
            asyncio.run_coroutine_threadsafe(self.internal_close(), self.loop)
            label.configure(text="Idle")
            button.configure(text="RUN", command=self.run)
            button.pack(pady=10)
        except Exception as e:
            print(e)


def on_closing():
    bot.close()
    root.destroy()


bot = My_Bot()

# Create the main window
root = tk.Tk()
root.title("Glitch Character Management")
root.protocol("WM_DELETE_WINDOW", on_closing)
# Create a label widget
label = tk.Label(
    root,
    text="Idle",
    anchor=tk.CENTER,
    width=20,
    bd=3,
    font=("Arial", 16, "bold"),
    justify=tk.CENTER,
)
label.pack(
    padx=20,
    pady=10,
)
button = tk.Button(
    root,
    text="Start",
    command=bot.run,
    width=10,
    pady=10,
    font=("Arial", 16, "bold"),
)
button.pack(pady=10)

# Start the GUI event loop
root.mainloop()
