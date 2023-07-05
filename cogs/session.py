from discord import SlashCommandGroup
from discord.ext import commands
from discord.ext.commands import Context
from cogs.char import Stat

from cogs.game import getActiveGame
from utils.utils import error, get_db_connection


class SessionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    session_commands = SlashCommandGroup("session", "Tools for the gm")

    @session_commands.command(
        name="begin",
        description="Begin the session",
    )
    async def begin(self, ctx: Context):
        if ctx.author.id == (await getActiveGame(ctx))["GM"]:
            try:
                db = await get_db_connection()
                sql = f"""UPDATE char SET"""
                for stat in Stat:
                    sql += f"""\n\t{stat.cost.lower()} = MAX(0, {stat.cost.lower()} - 1),"""
                sql = sql[: len(sql) - 1]
                sql += """\nWHERE EXISTS
                            (SELECT c.*
                                FROM char c
                                JOIN char_game_join cgj ON c.id = cgj.char
                                JOIN active_game ag ON cgj.game = ag.game
                                JOIN game g ON ag.game = g.id
                                WHERE g.guild = ?)"""
                await db.execute(sql, [ctx.guild.id])
                await db.commit()
            except Exception as e:
                await error(ctx, e)
            finally:
                await db.close()
            await ctx.respond("Session begun!")
        else:
            await error(ctx, "Only the GM can invoke this command!")
