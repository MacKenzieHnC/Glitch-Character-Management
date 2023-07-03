from aiosqlite import Row
from discord import SlashCommandGroup
from discord.ext import commands
from discord.ext.commands import Context
from cogs.form import Field, get_form
from cogs.game import GameCog, get_guild_games, getActiveGame
from enum import Enum

from utils import (
    error,
    get_db_connection,
    get_selector_input,
    validate_int,
    validate_str,
)


class Stat(Enum):
    def __init__(self, stat, cost):
        self.stat = stat
        self.cost = cost

    EIDE = ("Eide", "Stillness")
    FLORE = ("Flore", "Immersion")
    LORE = ("Lore", "Fugue")
    WYRD = ("Wyrd", "Burn")
    ABILITY = ("Ability", "Wear")


DEFAULT_CHAR = {
    "id": -1,
    "author": 0,
    "Name": "",
    "XP": 0,
    "Eide": 0,
    "Flore": 0,
    "Lore": 0,
    "Wyrd": 0,
    "Ability": 0,
    "Stillness": 0,
    "Immersion": 0,
    "Fugue": 0,
    "Burn": 0,
    "Wear": 0,
}

CHAR_KEYS = [
    "id",
    "author",
    "Name",
    "XP",
    "Eide",
    "Flore",
    "Lore",
    "Wyrd",
    "Ability",
    "Stillness",
    "Immersion",
    "Fugue",
    "Burn",
    "Wear",
]


def to_dict(char: dict):
    return {
        "Name": [
            Field("Name", char["Name"], validate_str),
            Field("XP", char["XP"], validate_int),
        ],
        "Stats": [Field(stat.stat, char[stat.stat], validate_int) for stat in Stat],
        "Costs": [Field(stat.cost, char[stat.cost], validate_int) for stat in Stat],
    }


def char_from_row(row: Row):
    return {k: row[k.lower()] for k in CHAR_KEYS}


async def get_characters(ctx: Context):
    chars = []
    game = await getActiveGame(ctx)

    try:
        cursor = None
        db = await get_db_connection()
        sql = [
            f"""SELECT c.*
                FROM char c
                JOIN char_game_join cgj ON c.id = cgj.char
                JOIN active_game ag ON cgj.game = ag.game
                JOIN game g ON ag.game = g.id
                WHERE guild =  ?""",
            [ctx.guild.id],
        ]
        if ctx.author.id != game["GM"]:
            sql[0] += " AND c.author = ?"
            sql[1].append(str(ctx.author.id))

        cursor = await db.execute(sql[0], sql[1])

        rows = await cursor.fetchall()
        for row in rows:
            chars.append(char_from_row(row))
        await cursor.close()
    except Exception as e:
        await error(ctx, e)
    finally:
        await db.close()

    return chars


async def get_single_character(ctx: Context, choose_msg: str):
    chars = await get_characters(ctx)
    if len(chars) == 0:
        raise Exception(
            "You have no characters in this game yet!",
        )
    elif len(chars) == 1:
        char = chars[0]
    else:
        char = await get_selector_input(ctx, choose_msg, chars)
    return char


###################################
#   COMMANDS
###################################


class CharCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    char_commands = SlashCommandGroup("char", "Commands for characters")

    @char_commands.command(name="add", description="Add a character")
    async def addChar(self, ctx: Context):
        game: GameCog = await get_selector_input(
            ctx,
            "What game will this character belong to?",
            await get_guild_games(ctx),
        )

        options = to_dict(DEFAULT_CHAR)

        options: dict[list[Field]] = await get_form(ctx, options)

        options = [field for key in list(options.keys()) for field in options[key]]

        sql = "INSERT INTO char (author"
        for field in options:
            sql += ",\n\t" + field.label.lower()
        sql += ")\nVALUES(?"
        for field in options:
            sql += ", ?"
        sql += ")"

        try:
            db = await get_db_connection()
            cursor = await db.execute(
                sql,
                (
                    ctx.author.id,
                    *[field.value for field in options],
                ),
            )
            char_id = cursor.lastrowid
            await cursor.execute(
                """INSERT INTO char_game_join (char, game)
                                    VALUES(?, ?)""",
                (char_id, game["id"]),
            )
            await cursor.close()
            await db.commit()
            await ctx.respond(content=f"{options[0].value} added to {game['Name']}!")
        except Exception as e:
            await error(ctx, e)
        finally:
            await db.close()

    @char_commands.command(name="display", description="Display character sheet")
    async def displayChar(self, ctx: Context):
        char = to_dict(
            await get_single_character(ctx, "What character would you like to display?")
        )
        await get_form(ctx, char, display_only=True)

    @char_commands.command(name="edit", description="Edit character sheet")
    async def displayChar(self, ctx: Context):
        char = await get_single_character(
            ctx, "What character would you like to display?"
        )
        id = char["id"]

        char = await get_form(ctx, to_dict(char), display_only=False)

        char: list[Field] = [field for key in list(char.keys()) for field in char[key]]

        sql = "UPDATE char SET "
        for field in char:
            sql += field.label.lower() + " = ?,\n"
        sql = sql[: len(sql) - 2]
        sql += "\nWHERE id = ?"

        try:
            db = await get_db_connection()
            cursor = await db.execute(
                sql,
                [*[field.value for field in char], id],
            )
            await cursor.close()
            await db.commit()
            await ctx.respond(content=f"{char[0].value} successfully updated!")
        except Exception as e:
            await error(ctx, e)
        finally:
            await db.close()
