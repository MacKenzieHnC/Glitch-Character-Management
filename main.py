import discord
import os  # default module
from dotenv import load_dotenv

load_dotenv()  # load all the variables from the env file
bot = discord.Bot()


bot.load_extension("cogs.game")
bot.load_extension("cogs.costs")
bot.load_extension("cogs.char")
bot.load_extension("cogs.session")

bot.run(os.getenv("TOKEN"))  # run the bot with the token
