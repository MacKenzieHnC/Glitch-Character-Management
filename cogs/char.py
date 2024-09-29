from aiosqlite import Row
from discord import SlashCommandGroup
from discord.ext import commands
from discord.ext.commands import Context
from cogs.game import GameCog, get_guild_games, getActiveGame
from enum import Enum
from utils.ui_shortcuts import get_selector_input
from utils.ui_shortcuts import Field, get_form
from utils.utils import db_call, get_db_connection, validate_int, validate_str, error


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
    **{stat.stat: 0 for stat in Stat},
    **{stat.cost: 0 for stat in Stat},
}


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
    return {k: row[k.lower()] for k in DEFAULT_CHAR.keys()}


async def get_characters(ctx):
    game = await getActiveGame(ctx)

    @db_call
    async def select(ctx):
        sql = {
            "sql": f"""SELECT c.*
                FROM char c
                JOIN char_game_join cgj ON c.id = cgj.char
                JOIN active_game ag ON cgj.game = ag.game
                JOIN game g ON ag.game = g.id
                WHERE guild =  ?""",
            "params": [ctx.guild.id],
        }
        if ctx.author.id != game["GM"]:
            sql["sql"] += " AND c.author = ?"
            sql["params"].append(str(ctx.author.id))
        return [sql]

    chars: list[dict] = [char_from_row(row) for row in (await select(ctx))]
    if len(chars) < 1:
        await error(ctx, f"No characters in {game['Name']}!")
    return chars


async def get_single_character(ctx, choose_msg: str, everyone_allowed=False):
    chars = await get_characters(ctx)
    if len(chars) == 1:
        char = chars[0]
    else:
        char = await get_selector_input(
            ctx,
            choose_msg,
            [{"id": -69, "Name": "Everyone"}, *chars] if everyone_allowed else chars,
        )
    return char


###################################
#   COMMANDS
###################################


class CharCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    char_commands = SlashCommandGroup("char", "Commands for characters")

    @char_commands.command(name="add", description="Add a character")
    async def addChar(self, ctx):
        game: GameCog = await get_selector_input(
            ctx,
            "What game will this character belong to?",
            await get_guild_games(ctx),
        )

        options = to_dict(DEFAULT_CHAR)
        options: dict[list[Field]] = await get_form(ctx, options)
        options = [field for key in list(options.keys()) for field in options[key]]

        @db_call
        async def insert(ctx):
            return [
                {
                    "sql": ", ".join(
                        [
                            "INSERT INTO char (author",
                            *[field.label.lower() for field in options],
                        ]
                    )
                    + (", ".join([")\nVALUES(?", *["?" for field in options]]) + ")"),
                    "params": [ctx.author.id, *[field.value for field in options]],
                },
                {
                    "sql": """INSERT INTO char_game_join (char, game)
                                    VALUES(last_insert_rowid(), ?)""",
                    "params": [game["id"]],
                },
            ]

        await insert(ctx)
        await ctx.respond(content=f"{options[0].value} added to {game['Name']}!")

    @char_commands.command(name="display", description="Display character sheet")
    async def displayChar(self, ctx):
        char = to_dict(
            await get_single_character(ctx, "What character would you like to display?")
        )
        await get_form(ctx, char, display_only=True)

    @char_commands.command(name="edit", description="Edit character sheet")
    async def displayChar(self, ctx):
        char = await get_single_character(
            ctx, "What character would you like to display?"
        )
        id = char["id"]

        char = await get_form(ctx, to_dict(char), display_only=False)

        char: list[Field] = [field for key in list(char.keys()) for field in char[key]]

        @db_call
        async def update(ctx):
            return [
                {
                    "sql": "UPDATE char SET "
                    + ",\n".join([field.label.lower() + " = ?" for field in char])
                    + "\nWHERE id = ?",
                    "params": [*[field.value for field in char], id],
                }
            ]

        await update(ctx)
        await ctx.respond(f"{char[0].value} successfully updated!")


def setup(bot):
    bot.add_cog(CharCog(bot))
