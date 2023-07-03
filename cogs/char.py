import aiosqlite
from discord import SlashCommandGroup
from discord.ext import commands
from discord.ext.commands import Context
from cogs.form import Field, get_form
from cogs.game import GameCog, get_guild_games, getActiveGame

from utils import (
    error,
    get_selector_input,
    validate_int,
    validate_str,
)


class Character:
    def __init__(
        # discord access
        self,
        id,
        author,
        name,
        # stats
        xp,
        eide,
        flore,
        lore,
        wyrd,
        ability,
        # cost pools
        stillness,
        immersion,
        fugue,
        burn,
        wear
        # # flavor
        # discipline,
        # sphere,
        # technique,
        # sanctuary,
        # destruction,
        # bonds,
        # geasa,
        # gifts,
        # treasures,
        # arcana,
        # levers,
        # quests,
    ):
        self.id = id
        self.author = author
        self.name = name
        self.xp = xp
        self.eide = eide
        self.flore = flore
        self.lore = lore
        self.wyrd = wyrd
        self.ability = ability
        self.stillness = stillness
        self.immersion = immersion
        self.fugue = fugue
        self.burn = burn
        self.wear = wear
        # self.discipline = discipline
        # self.sphere = sphere
        # self.technique = technique
        # self.sanctuary = sanctuary
        # self.destruction = destruction
        # self.bonds = bonds
        # self.geasa = geasa
        # self.gifts = gifts
        # self.treasures = treasures
        # self.arcana = arcana
        # self.levers = levers
        # self.quests = quests


DEFAULT_CHAR = Character(
    id=0,
    author="No One",
    name="",
    xp=0,
    eide=0,
    flore=0,
    lore=0,
    wyrd=0,
    ability=0,
    stillness=0,
    immersion=0,
    fugue=0,
    burn=0,
    wear=0,
)


def to_dict(char: Character):
    return {
        "Name": [
            Field("Name", char.name, validate_str),
            Field("XP", char.xp, validate_int),
        ],
        "Stats": [
            Field(stat[0], stat[1], validate_int)
            for stat in [
                ("Eide", char.eide),
                ("Lore", char.lore),
                ("Flore", char.flore),
                ("Wyrd", char.wyrd),
                ("Ability", char.ability),
            ]
        ],
        "Costs": [
            Field(cost[0], cost[1], validate_int)
            for cost in [
                ("Stillness", char.stillness),
                ("Immersion", char.immersion),
                ("Fugue", char.fugue),
                ("Burn", char.burn),
                ("Wear", char.wear),
            ]
        ],
    }


def char_from_row(row: aiosqlite.Row):
    return Character(*row[:14])


async def get_characters(ctx: Context):
    chars = []
    game = await getActiveGame(ctx)

    try:
        cursor = None
        db = await aiosqlite.connect("data/Assets.db")
        sql = [
            f"""SELECT c.*
                FROM char c
                JOIN char_game_join cgj ON c.id = cgj.char
                JOIN active_game ag ON cgj.game = ag.game
                JOIN game g ON ag.game = g.id
                WHERE guild =  ?""",
            [ctx.guild.id],
        ]
        if ctx.author.id != game.gm:
            sql[0] += " AND c.author = ?"
            sql[1].append(str(ctx.author.id))

        cursor = await db.execute(sql[0], sql[1])
        for row in await cursor.fetchall():
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
            db = await aiosqlite.connect("data/Assets.db")
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
                (char_id, game.id),
            )
            await cursor.close()
            await db.commit()
            await ctx.respond(content=f"{options[0].value} added to {game.name}!")
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
        id = char.id

        char = await get_form(ctx, to_dict(char), display_only=False)

        char: list[Field] = [field for key in list(char.keys()) for field in char[key]]

        sql = "UPDATE char SET "
        for field in char:
            sql += field.label.lower() + " = ?,\n"
        sql = sql[: len(sql) - 2]
        sql += "\nWHERE id = ?"

        try:
            db = await aiosqlite.connect("data/Assets.db")
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
