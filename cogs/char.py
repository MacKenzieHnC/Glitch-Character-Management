import aiosqlite
from discord import SlashCommandGroup
import discord
from discord.ext import commands
from cogs.form import Field, get_form
from cogs.game import GameCog, get_guild_games, getActiveGame
from enum import Enum

from utils import (
    error_text,
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


def init_spend(bot):
    def addCommand(t: Stat):
        @bot.slash_command(
            name=t.stat.lower(),
            description=f"""Spend {t.cost.lower()} to do magic""",
        )
        @discord.option("amount", description="Amount to spend", required=True)
        async def _spend(ctx, amount: int):
            try:
                char = await get_single_character(
                    ctx,
                    zero_msg="You have no characters in this game yet!",
                    choose_msg=f"What character will be spending {t.stat}?",
                )
            except Exception as e:
                await ctx.respond(error_text(e))

            msg = f"""{char.name} spent {amount} {t.cost}"""
            sql = f"""UPDATE char\nSET """
            if amount >= 5:
                msg += " and gained 1xp!"
                sql += "xp = xp + 1,\n"
            sql += f"""{t.cost.lower()} = {t.cost.lower()} + MAX({amount} - {t.stat.lower()}, 0)\nWHERE id = {char.id}"""

            try:
                cursor = None
                db = await aiosqlite.connect("data/Assets.db")
                cursor = await db.execute(
                    sql,
                )
                await db.commit()
                await ctx.respond(msg)
                await cursor.close()
            except Exception as e:
                await ctx.respond(error_text(e))
            finally:
                await db.close()

    for t in Stat:
        addCommand(t)


def char_from_row(row: aiosqlite.Row):
    return Character(*row[:14])


async def get_characters(ctx):
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
        await ctx.respond(error_text(e))
    finally:
        await db.close()

    return chars


async def get_single_character(ctx, zero_msg: str, choose_msg: str):
    chars = await get_characters(ctx)
    if len(chars) == 0:
        raise Exception(zero_msg)
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
    async def addChar(self, ctx):
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
            await ctx.respond(error_text(e))
        finally:
            await db.close()
