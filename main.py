import discord
import os  # default module
from dotenv import load_dotenv
from cogs.char import CharCog, init_spend
from cogs.game import GameCog

load_dotenv()  # load all the variables from the env file
bot = discord.Bot()


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")


bot.add_cog(GameCog(bot))
bot.add_cog(CharCog(bot))
init_spend(bot)

bot.run(os.getenv("TOKEN"))  # run the bot with the token
