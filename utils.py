import discord
from discord.ui import View, Select
import asyncio


def error_text(e):
    return f"```ansi\n\u001b[1;40m\u001b[1;31mError: {e}\n```"


async def get_text_input(ctx, title: str, label: str):
    response = []

    class TextModal(discord.ui.Modal):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.add_item(discord.ui.InputText(label=label))

        async def callback(self, interaction: discord.Interaction):
            response.append(self.children[0].value)
            await interaction.response.send_message(
                f'Great! So the game will be called "{response[0]}"'
            )

    modal = TextModal(title=title)
    await ctx.response.send_modal(modal)
    while len(response) == 0:
        await asyncio.sleep(1)
    return response[0]


async def get_user_selector_input(ctx, message: str):
    response = []

    class UserSelector(discord.ui.View):
        @discord.ui.select(select_type=discord.ComponentType.user_select)
        async def select_callback(self, select, interaction):
            response.append(select.values[0])
            await interaction.response.edit_message(
                content=f"{select.values[0]} selected!",
                view=None,
            )

    await ctx.respond(
        message,
        view=UserSelector(),
    )
    while len(response) == 0:
        await asyncio.sleep(1)
    return response[0]


async def get_selector_input(ctx, message: str, options):
    response = []

    class SelectorView(discord.ui.View):
        @discord.ui.select(  # the decorator that lets you specify the properties of the select menu
            placeholder="Choose option",  # the placeholder text that will be displayed if nothing is selected
            min_values=1,  # the minimum number of values that must be selected by the users
            max_values=1,  # the maximum number of values that can be selected by the users
            options=[
                discord.SelectOption(
                    label=str(i) + ": " + options[i].name, value=str(i)
                )
                for i in range(len(options))
            ],
        )
        async def select_callback(
            self, select, interaction
        ):  # the function called when the user is done selecting options
            response.append(options[int(select.values[0])])

    await ctx.respond(message, view=SelectorView())
    while len(response) == 0:
        await asyncio.sleep(1)
    return response[0]
