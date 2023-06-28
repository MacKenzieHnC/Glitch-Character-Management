import aiosqlite
from discord import SlashCommandGroup
from discord.ext import commands
from discord.ext.commands import Context

from utils import (
    error,
    get_selector_input,
    get_text_input,
    get_user_selector_input,
)


class Game:
    def __init__(self, id, gm, name):
        self.id = id
        self.gm = gm
        self.name = name


async def get_guild_games(ctx):
    games: list[Game] = []
    try:
        db = await aiosqlite.connect("data/Assets.db")
        async with db.execute(
            f"""SELECT id, gm, name
                                    FROM game
                                    WHERE guild = ?""",
            [ctx.guild.id],
        ) as cursor:
            async for row in cursor:
                games.append(Game(*row))
        await cursor.close()
    except Exception as e:
        await error(ctx, e)
    finally:
        await db.close()

    return games


async def setActiveGame(ctx, game: Game):
    try:
        db = await aiosqlite.connect("data/Assets.db")
        # Remove all currently active games (should only be 0 or 1 tho)
        cursor = await db.execute(
            f"""DELETE
                    FROM active_game
                    WHERE game IN
                        (SELECT game
                        FROM active_game ag
                        JOIN game g ON ag.game = g.id
                        WHERE g.guild = ?)""",
            [ctx.guild.id],
        )
        await cursor.execute(
            f"""INSERT INTO active_game (game)
                        VALUES(?)""",
            [game.id],
        )
        await db.commit()
        await ctx.respond(f"""Active game changed to "{game.name}"!""")
    except Exception as e:
        await error(ctx, e)
    finally:
        if cursor:
            await cursor.close()
        await db.close()


async def getActiveGame(ctx):
    games: list[Game] = []
    try:
        cursor = None
        db = await aiosqlite.connect("data/Assets.db")
        cursor = await db.execute(
            f"""SELECT id, gm, name
                FROM active_game ag
                JOIN game g ON ag.game = g.id
                WHERE g.guild = ?""",
            [ctx.guild.id],
        )
        async for row in cursor:
            games.append(Game(*row))
    except Exception as e:
        await error(ctx, e)
    finally:
        if cursor:
            await cursor.close()
        await db.close()

    return games[0]


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
        gm = await get_user_selector_input(ctx, f"And who will be the GM for {name}?")

        # Add to db
        try:
            db = await aiosqlite.connect("data/Assets.db")
            cursor = await db.execute(
                f"""INSERT INTO game (guild, gm, name)
                    VALUES("{ctx.guild.id}", "{gm}", "{name}")"""
            )
            await db.commit()
            await ctx.respond(f"Successfully added {name} to db!!", ephemeral=True)
        except Exception as e:
            await error(ctx, e)
        finally:
            if cursor:
                await cursor.close()
            await db.close()

    @game_commands.command(name="get_active", description="Display the active game")
    async def getActive(self, ctx):
        if ctx.author.id == ctx.guild.owner_id:
            game = await getActiveGame(ctx)
            await ctx.respond(f"""Currently active game is "{game.name}"!""")
        else:
            await error(ctx, "Only the server owner can invoke this command!")

    @game_commands.command(name="set_active", description="Change the active game")
    async def setActive(self, ctx):
        if ctx.author.id == ctx.guild.owner_id:
            game: GameCog = await get_selector_input(
                ctx,
                "What game will be active?",
                await get_guild_games(ctx),
            )

            await setActiveGame(ctx, game)
        else:
            await error(ctx, "Only the server owner can invoke this command!")
