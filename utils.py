import discord
from discord.ui import View, Select
import asyncio


async def select_menu(ctx, options: dict):
    response = []
    select = Select(
        min_values=1,
        max_values=1,
        placeholder="Choose your color here",
        options=[discord.SelectOption(label=key) for key in options.keys()],
    )

    async def select_callback(
        interaction,
    ):
        response.append(options[select.values[0]])
        await interaction.response.edit_message(
            content=f"{select.values[0]} selected!", view=None
        )

    select.callback = select_callback

    view = View(timeout=None)
    view.add_item(select)

    await ctx.respond(view=view)

    while len(response) == 0:
        await asyncio.sleep(1)

    return response[0]
