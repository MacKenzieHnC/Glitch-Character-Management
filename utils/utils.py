import aiosqlite
from discord.ext.commands import Context


async def error(ctx: Context, e: str):
    await ctx.respond(f"`Error: {e}`", ephemeral=True)


def validate_str(value: str):
    return len(value) > 0


def validate_int(value: str):
    try:
        value = int(value)
        return True
    except ValueError:
        return False


async def get_db_connection():
    db = await aiosqlite.connect("data/Assets.db")
    db.row_factory = aiosqlite.Row
    return db
