import textwrap
from discord import SlashCommandGroup
from discord.ext import commands
from discord.ext.commands import Context
from cogs.char import Stat

from cogs.game import getActiveGame
from utils.utils import db_call, error, get_db_connection


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

            @db_call
            async def update(ctx):
                return [
                    {
                        "sql": (
                            f"""UPDATE char SET """
                            + (
                                ",\n\t".join(
                                    [
                                        f"{stat.cost.lower()} = MAX(0, {stat.cost.lower()} - 1)"
                                        for stat in Stat
                                    ]
                                )
                            )
                            + """\nWHERE EXISTS"""
                            + textwrap.dedent(
                                """
                            (
                                SELECT c.*
                                    FROM char c
                                    JOIN char_game_join cgj ON c.id = cgj.char
                                    JOIN active_game ag ON cgj.game = ag.game
                                    JOIN game g ON ag.game = g.id
                                    WHERE g.guild = ?
                            )"""
                            )
                        ),
                        "params": [ctx.guild.id],
                    }
                ]

            await update(ctx)
            await ctx.respond("Session begun!")
        else:
            await error(ctx, "Only the GM can invoke this command!")
