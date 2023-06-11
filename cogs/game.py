import aiosqlite
from discord import SlashCommandGroup
from discord.ext import commands

from utils import error_text, get_text_input, get_user_selector_input


###################################
#   COMMANDS
###################################


class GameCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    game_commands = SlashCommandGroup("game", "Commands for games")

    @game_commands.command(name="add", description="Add a new game to this server")
    async def addGame(self, ctx):
        # Get game data
        name = await get_text_input(
            ctx, "New Game!", "Name (the name that will appear in menus)"
        )
        gm = await get_user_selector_input(ctx, "And who will be the GM?")

        # Add to db
        try:
            db = await aiosqlite.connect("data/Assets.db")
            cursor = await db.execute(
                f"""INSERT INTO game (guild, gm, name)
                    VALUES("{ctx.guild.id}", "{gm}", "{name}")"""
            )
            await db.commit()
            await ctx.respond(f"Successfully added {name} to db!!")
        except Exception as e:
            await ctx.respond(error_text(e))
        finally:
            if cursor:
                await cursor.close()
            await db.close()
