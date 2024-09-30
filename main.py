import discord
import os  # default module
from dotenv import load_dotenv


def boot():
    load_dotenv()  # load all the variables from the env file
    bot = discord.Bot()
    for cog in ["cogs.game", "cogs.costs", "cogs.char", "cogs.session"]:
        bot.load_extension(cog)
    bot.run(os.getenv("TOKEN"))  # run the bot with the token


boot()
