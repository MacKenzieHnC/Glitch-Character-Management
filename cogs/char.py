import aiosqlite
from discord import SlashCommandGroup
from discord.ext import commands
from cogs.form import Field, get_form_input
from cogs.game import GameCog, get_guild_games

from utils import (
    error_text,
    get_selector_input,
    validate_int,
    validate_str,
)


class Character:
    def __init__(
        # discord access
        self,
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

        options = {
            "Name": [Field("Name", "", validate_str), Field("XP", 0, validate_int)],
            "Stats": [
                Field(key, 0, validate_int)
                for key in ["Eide", "Lore", "Flore", "Wyrd", "Ability"]
            ],
            "Costs": [
                Field(key, 0, validate_int)
                for key in ["Stillness", "Immersion", "Fugue", "Burn", "Wear"]
            ],
        }

        options: dict[list[Field]] = await get_form_input(ctx, options)

        options = [field for key in list(options.keys()) for field in options[key]]

        sql = "INSERT INTO char (guild,\n\tauthor"
        for field in options:
            sql += ",\n\t" + field.label.lower()
        sql += ")\nVALUES(?, ?"
        for field in options:
            sql += ", ?"
        sql += ")"

        try:
            db = await aiosqlite.connect("data/Assets.db")
            cursor = await db.execute(
                sql,
                (
                    str(ctx.guild.id),
                    str(ctx.author),
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
