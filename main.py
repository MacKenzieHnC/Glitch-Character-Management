import discord
import os  # default module
import aiosqlite
from dotenv import load_dotenv
from utils import error_text, select_menu

load_dotenv()  # load all the variables from the env file
bot = discord.Bot()


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")


@bot.slash_command(name="add_char", description="Add a character")
@discord.option(
    "name", description="Name to type when accessing this character", required=True
)
async def addChar(ctx, name: str):
    try:
        db = await aiosqlite.connect("data/Assets.db")
        cursor = await db.execute(
            f'INSERT INTO char VALUES("{ctx.guild.id}", "{ctx.author}", "{name}")'
        )
        await db.commit()
        await ctx.respond("Made it!")
    except Exception as e:
        await ctx.respond(error_text(e))
    finally:
        await cursor.close()
        await db.close()


@bot.slash_command()
async def select(ctx):
    print(
        await select_menu(
            ctx, {"1": "I am 1's value", "2": "I am 2's value", "3": "I am 3's value"}
        )
    )


bot.run(os.getenv("TOKEN"))  # run the bot with the token
