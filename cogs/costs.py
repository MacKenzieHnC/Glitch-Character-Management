import aiosqlite
from discord import SlashCommandGroup
import discord
from discord.ext import commands
from discord.ext.commands import Context
from cogs.char import Stat

from cogs.char import get_single_character
from utils.utils import error


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
        async def spend(self, ctx: Context, amount: int, stat=stat):
            char = await get_single_character(
                ctx,
                choose_msg=f"What character will be spending {stat.stat}?",
            )

            msg = f"""{char['Name']} spent {amount} {stat.stat}"""
            xp_msg = ""
            sql = f"""UPDATE char\nSET """
            if amount >= 5:
                xp_msg += ", and gained 1xp"
                sql += "xp = xp + 1,\n"
            sql += f"""{stat.cost.lower()} = {stat.cost.lower()} + MAX({amount} - {stat.stat.lower()}, 0)\nWHERE id = {char['id']}"""

            try:
                cursor = None
                db = await aiosqlite.connect("data/Assets.db")
                cursor = await db.execute(
                    sql,
                )
                await db.commit()
                cursor = await cursor.execute(
                    f"SELECT {stat.stat.lower()}, {stat.cost.lower()} FROM char WHERE id = {char['id']}"
                )

                stat_value, cost_value = await cursor.fetchone()
                suffer = max(0, amount - stat_value)
                if suffer > 0:
                    msg += f", suffering {suffer} {stat.cost}"
                msg += xp_msg + "!"
                msg += f"\n{stat.cost} is now {cost_value}"
                await ctx.respond(msg)
                await cursor.close()
            except Exception as e:
                await error(ctx, e)
            finally:
                await db.close()
