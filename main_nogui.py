import asyncio
import os
from bot import My_Bot
from dotenv import load_dotenv

load_dotenv()
bot = My_Bot(print, ["Bot online and ready to go!"])
bot.initialize(asyncio.new_event_loop())
bot.bot.run(os.getenv("TOKEN"))
