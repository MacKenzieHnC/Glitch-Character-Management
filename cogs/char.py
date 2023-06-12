import aiosqlite
from discord import SlashCommandGroup
import discord
from discord.ext import commands
from cogs.form import get_form_input
from cogs.game import Game, get_guild_games

from utils import error_text, get_selector_input, get_text_input


class Character:
    def __init__(
        # discord access
        self,
        label,
        author,
        # # stats
        # xp,
        # eide,
        # flore,
        # lore,
        # wyrd,
        # ability,
        # # cost pools
        # stillness,
        # immersion,
        # fugue,
        # burn,
        # wear
        # # flavor
        # name,
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
        self.label = label
        self.author = author
        # self.xp = xp
        # self.eide = eide
        # self.flore = flore
        # self.lore = lore
        # self.wyrd = wyrd
        # self.ability = ability
        # self.stillness = stillness
        # self.immersion = immersion
        # self.fugue = fugue
        # self.burn = burn
        # self.wear = wear
        # self.name = name
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
        game = await get_selector_input(
            ctx,
            "What game will this character belong to?",
            await get_guild_games(ctx),
        )

        options = {
            "Name": {"Name": "", "Label": ""},
            "Stats": {"Eide": 0, "Lore": 0, "Flore": 0, "Wyrd": 0, "Ability": 0},
            "Costs": {"Stillness": 0, "Immersion": 0, "Fugue": 0, "Burn": 0, "Wear": 0},
        }

        await get_form_input(ctx, options)

        # try:
        #     db = await aiosqlite.connect("data/Assets.db")
        #     cursor = await db.execute(
        #         f"""INSERT INTO char (guild, author, label)
        #             VALUES("{ctx.guild.id}", "{ctx.author}", "{name}")"""
        #     )
        #     await db.commit()
        #     await ctx.respond("Made it!")
        # except Exception as e:
        #     await ctx.respond(error_text(e))
        # finally:
        #     await cursor.close()
        #     await db.close()
