# Python 3.10.3
import os
import discord  # py-cord 2.6.1
from dotenv import load_dotenv


load_dotenv()  # load all the variables from the env file
bot = discord.Bot()
for cog in ["cogs.game", "cogs.costs", "cogs.char", "cogs.session"]:
    bot.load_extension(cog)
bot.run(os.getenv("TOKEN"))  # run the bot with the token
