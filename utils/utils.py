import aiosqlite
from discord.ext.commands import Context
from aiosqlite import Row


async def error(ctx: Context, e: str):
    await ctx.respond(f"`Error: {e}`")


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


def db_call(func):
    async def wrapper(ctx):
        rows: list[Row] = []
        try:
            cursor = None
            db = await get_db_connection()
            db.row_factory = Row
            calls = await func(ctx)
            for call in calls:
                cursor = await db.execute(
                    call["sql"],
                    call["params"],
                )
            await db.commit()
            for row in await cursor.fetchall():
                rows.append(row)
            return rows
        except Exception as e:
            await error(ctx, e)
            raise Exception(e)
        finally:
            if cursor:
                await cursor.close()
            await db.close()

    return wrapper
