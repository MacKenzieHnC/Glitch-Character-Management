from aiosqlite import Row
from discord import SlashCommandGroup
from discord.ext import commands
from discord.ext.commands import Context
from utils.ui_shortcuts import (
    get_selector_input,
    get_text_input,
    get_user_selector_input,
)

from utils.utils import db_call, error, get_db_connection

GAME_KEYS = ["id", "GM", "Name"]


def game_from_row(row: Row):
    return {k: row[k.lower()] for k in GAME_KEYS}


async def get_guild_games(ctx: Context):
    @db_call
    async def select(ctx):
        return [
            {
                "sql": f"""SELECT *
                FROM game
                WHERE guild = ?""",
                "params": [ctx.guild.id],
            }
        ]

    games: list[dict] = [game_from_row(row) for row in (await select(ctx))]

    if len(games) < 1:
        await error(ctx, "No games found!")

    return games


async def setActiveGame(ctx: Context, game: dict):
    @db_call
    async def calls(ctx):
        return [
            {
                "sql": f"""DELETE
                    FROM active_game
                    WHERE game IN
                        (SELECT game
                        FROM active_game ag
                        JOIN game g ON ag.game = g.id
                        WHERE g.guild = ?)""",
                "params": [ctx.guild.id],
            },
            {
                "sql": f"""INSERT INTO active_game (game)
                        VALUES(?)""",
                "params": [game["id"]],
            },
        ]

    await calls(ctx)
    await ctx.respond(f"""Active game changed to "{game['Name']}"!""")


async def getActiveGame(ctx: Context):
    @db_call
    async def select(ctx):
        return [
            {
                "sql": f"""SELECT id, gm, name
                FROM active_game ag
                JOIN game g ON ag.game = g.id
                WHERE g.guild = ?""",
                "params": [ctx.guild.id],
            }
        ]

    games: list[dict] = [game_from_row(row) for row in (await select(ctx))]

    if len(games) < 1:
        await error(ctx, "No active game!")

    return games[0]


###################################
#   COMMANDS
###################################


class GameCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    game_commands = SlashCommandGroup("game", "Commands for games")

    @game_commands.command(name="add", description="Add a new game to this server")
    async def addGame(self, ctx: Context):
        # Get game data
        name = await get_text_input(
            ctx, "New Game!", "Name (the name that will appear in menus)"
        )
        gm = await get_user_selector_input(ctx, f"And who will be the GM for {name}?")

        # Add to db
        @db_call
        async def insert(ctx):
            return [
                {
                    "sql": f"""INSERT INTO game (guild, gm, name)
                    VALUES(?, ?, ?)""",
                    "params": [ctx.guild.id, gm, name],
                }
            ]

        await insert(ctx)
        await ctx.respond(f"Successfully added {name} to db!!")

    @game_commands.command(name="get_active", description="Display the active game")
    async def getActive(self, ctx: Context):
        if ctx.author.id == ctx.guild.owner_id:
            game = await getActiveGame(ctx)
            await ctx.respond(f"""Currently active game is "{game['Name']}"!""")
        else:
            await error(ctx, "Only the server owner can invoke this command!")

    @game_commands.command(name="set_active", description="Change the active game")
    async def setActive(self, ctx: Context):
        if ctx.author.id == ctx.guild.owner_id:
            game: GameCog = await get_selector_input(
                ctx,
                "What game will be active?",
                await get_guild_games(ctx),
            )

            await setActiveGame(ctx, game)
        else:
            await error(ctx, "Only the server owner can invoke this command!")
