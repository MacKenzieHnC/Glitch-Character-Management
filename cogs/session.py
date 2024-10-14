from discord import SlashCommandGroup
import discord
from discord.ext import commands
from cogs.char import Stat, get_single_character
from cogs.game import getActiveGame
from utils.utils import db_call, error


def gm_command(func):
    async def wrapper(*args, **kwargs):
        ctx = args[1]
        if ctx.author.id == (await getActiveGame(ctx))["GM"]:
            return await func(*args, **kwargs)
        else:
            await error(ctx, "Only the GM can invoke this command!")

    return wrapper


class SessionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    session_commands = SlashCommandGroup("session", "Tools for the gm")

    @gm_command
    @session_commands.command(
        name="begin",
        description="Begin the session",
    )
    async def begin(self, ctx):
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
                        + """(
                                SELECT c.*
                                    FROM char c
                                    JOIN char_game_join cgj ON c.id = cgj.char
                                    JOIN active_game ag ON cgj.game = ag.game
                                    JOIN game g ON ag.game = g.id
                                    WHERE g.guild = ?
                            )"""
                    ),
                    "params": [ctx.guild.id],
                }
            ]

        await update(ctx)
        await ctx.respond("Session begun!")

    @gm_command
    @session_commands.command(
        name="xp",
        description="Begin the session",
    )
    @discord.option("xp", description="Amount of xp to give out", required=True)
    async def xp(self, ctx, xp: int):
        char = await get_single_character(
            ctx, choose_msg=f"Who's getting {xp}xp?", everyone_allowed=True
        )

        @db_call
        async def update(ctx):
            return [
                {
                    "sql": (f"""UPDATE char SET xp = xp + ?""")
                    + """\nWHERE EXISTS"""
                    + """
                            (
                                SELECT c.*
                                    FROM char c
                                    JOIN char_game_join cgj ON c.id = cgj.char
                                    JOIN active_game ag ON cgj.game = ag.game
                                    JOIN game g ON ag.game = g.id
                                    WHERE g.guild = ?)"""
                    + (f" AND id = {char['id']}" if char["id"] != -69 else ""),
                    "params": [xp, ctx.guild.id],
                }
            ]

        await update(ctx)
        await ctx.respond(f"{char['Name']} got {xp} XP!")


def setup(bot):
    bot.add_cog(SessionCog(bot))
