import aiosqlite
from discord import SlashCommandGroup
import discord
from discord.ext import commands
from discord.ext.commands import Context
from cogs.char import Stat

from cogs.char import get_single_character
from utils.utils import db_call, error


class SpendCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    spend_commands = SlashCommandGroup("spend", "Spend cost to do magic")

    for stat in Stat:

        @spend_commands.command(
            name=stat.stat.lower(),
            description=f"""Spend {stat.cost.lower()} to do magic""",
        )
        @discord.option("amount", description="Amount to spend", required=True)
        async def spend(self, ctx, amount: int, stat=stat):
            char = await get_single_character(
                ctx,
                choose_msg=f"What character will be spending {stat.stat}?",
            )

            @db_call
            async def update(ctx):
                return [
                    {
                        "sql": f"""UPDATE char\nSET """
                        + ("xp = xp + 1,\n" if amount >= 5 else "")
                        + f"""{stat.cost.lower()} = {stat.cost.lower()} + MAX({amount} - {stat.stat.lower()}, 0)\nWHERE id = {char['id']}""",
                        "params": [],
                    },
                    {
                        "sql": f"SELECT {stat.stat.lower()}, {stat.cost.lower()} FROM char WHERE id = {char['id']}",
                        "params": [],
                    },
                ]

            stat_value, final_cost_value = (await update(ctx))[0]
            suffer = max(0, amount - stat_value)

            msg = (
                f"{char['Name']} spent {amount} {stat.stat}"
                + (f", suffering {suffer} {stat.cost}" if suffer > 0 else "")
                + (",\nand gained 1 xp" if amount >= 5 else "")
                + "!"
                + (f"\n{stat.cost} is now {final_cost_value}")
            )

            await ctx.respond(msg)


def setup(bot):
    bot.add_cog(SpendCog(bot))
