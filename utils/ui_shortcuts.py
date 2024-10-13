import discord
import asyncio

import discord.ext.pages as pages
from discord.ext.commands import Context
from discord import Interaction

from utils.utils import error


DEFAULT_TIMEOUT = 1800


async def get_text_input(ctx: Context, title: str, labels: str | list[str]):
    response: list[str] = []

    class TextModal(discord.ui.Modal):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            if isinstance(labels, str):
                self.add_item(discord.ui.InputText(label=labels))
            else:
                for label in labels:
                    self.add_item(discord.ui.InputText(label=label))

        async def callback(self, interaction: Interaction):
            if interaction.user.id == ctx.author.id:
                for child in self.children:
                    response.append(child.value)
                await interaction.response.edit_message(
                    content="Great!", delete_after=0
                )

    modal = TextModal(title=title)
    await ctx.send_modal(modal)
    try:
        await await_variable(ctx, response)
        return response[0]
    except Exception as e:
        await modal.on_timeout()
        await ctx.respond(f"`Error: Timeout`", ephemeral=True)
        raise Exception("Timeout")


async def get_user_selector_input(ctx: Context, message: str):
    response = []

    class UserSelector(discord.ui.View):
        @discord.ui.select(select_type=discord.ComponentType.user_select)
        async def select_callback(
            self, select: discord.ui.Select, interaction: Interaction
        ):
            if interaction.user.id == ctx.author.id:
                response.append(select.values[0].id)
                select.disabled = True
                await interaction.response.edit_message(
                    content=f"{select.values[0].name} selected!",
                    view=None,
                    delete_after=0,
                )

    selector = UserSelector()
    await ctx.respond(message, view=selector, ephemeral=True)

    try:
        await await_variable(ctx, response)
        return response[0]
    except Exception as e:
        await selector.on_timeout()
        raise Exception("Timeout")


async def get_selector_input(ctx: Context, message: str, options):
    response = []

    class SelectorView(discord.ui.View):
        @discord.ui.select(  # the decorator that lets you specify the properties of the select menu
            placeholder="Choose option",  # the placeholder text that will be displayed if nothing is selected
            min_values=1,  # the minimum number of values that must be selected by the users
            max_values=1,  # the maximum number of values that can be selected by the users
            options=[
                discord.SelectOption(
                    label=str(i) + ": " + options[i]["Name"], value=str(i)
                )
                for i in range(len(options))
            ],
        )
        async def select_callback(
            self, select, interaction: Interaction
        ):  # the function called when the user is done selecting options
            if interaction.user.id == ctx.author.id:
                response.append(options[int(select.values[0])])
                select.disabled = True
                await interaction.response.edit_message(
                    content=f"{options[int(select.values[0])]['Name']} selected!",
                    view=None,
                    delete_after=0,
                )

        async def on_timeout(self):
            self.disable_all_items()
            await self.message.edit(content=(f"`Error: Timeout`"), view=self)

    selector = SelectorView()
    await ctx.respond(message, view=selector, ephemeral=True)

    try:
        await await_variable(ctx, response)
        return response[0]
    except Exception as e:
        await selector.on_timeout()
        raise Exception("Timeout")


async def confirmation_button(ctx: Context, message, confirm_method, cancel_method):
    class ButtonView(discord.ui.View):
        @discord.ui.button(label="CANCEL", style=discord.ButtonStyle.red, row=2)
        async def submit_button_callback(self, button, interaction: Interaction):
            if interaction.user.id == ctx.author.id:
                await cancel_method()
                await interaction.response.edit_message(
                    content=f"Success!",
                    view=None,
                    delete_after=0,
                )

        @discord.ui.button(label="OKAY", style=discord.ButtonStyle.green, row=2)
        async def submit_button_callback(self, button, interaction: Interaction):
            if interaction.user.id == ctx.author.id:
                await confirm_method()
                await interaction.response.edit_message(
                    content=f"Success!",
                    view=None,
                    delete_after=0,
                )

    await ctx.respond(message, view=ButtonView(), ephemeral=True)


async def await_variable(ctx: Context, response: list, timeout=DEFAULT_TIMEOUT):
    while len(response) == 0 and timeout > 0:
        await asyncio.sleep(1)
        timeout -= 1
    if timeout == 0:
        raise Exception("Timeout!")


class Field:
    def __init__(self, label: str, value: any, validate):
        self.label = label
        self.value = value
        self.validate = validate

    def is_valid(self):
        return self.validate(self.value)


async def get_form(ctx: Context, options: dict[list[Field]], display_only=False):
    response = []
    # Initialize pages
    page_list: list[discord.Embed] = []
    for page_name in options.keys():
        page = discord.Embed(title=page_name)
        for field in options[page_name]:
            page.add_field(name=field.label, value=field.value, inline=False)
        page_list.append(page)

    # The View containing the edit button
    class ButtonView(discord.ui.View):
        @discord.ui.button(label="EDIT", style=discord.ButtonStyle.primary, row=2)
        async def edit_button_callback(self, button, interaction: discord.Interaction):
            if interaction.user.id == ctx.author.id:
                fields = options[list(options.keys())[paginator.current_page]]

                class EditModal(discord.ui.Modal):
                    def __init__(self, *args, **kwargs) -> None:
                        super().__init__(*args, **kwargs)
                        for field in fields:
                            self.add_item(
                                discord.ui.InputText(
                                    label=field.label, value=str(field.value)
                                )
                            )

                    async def callback(self, interaction: discord.Interaction):
                        current_page = paginator.current_page
                        for i in range(len(fields)):
                            fields[i].value = self.children[i].value
                            if fields[i].is_valid():
                                page_list[current_page].fields[i].value = str(
                                    self.children[i].value
                                )
                            else:
                                page_list[current_page].fields[i].value = (
                                    str(self.children[i].value)
                                    + " "
                                    + f"`Error: invalid`"
                                )
                        await interaction.response.edit_message(content="Success")
                        await paginator.goto_page(current_page)

                modal = EditModal(title=list(options.keys())[paginator.current_page])
                await interaction.response.send_modal(modal)

        @discord.ui.button(label="SUBMIT", style=discord.ButtonStyle.green, row=2)
        async def submit_button_callback(
            self, button, interaction: discord.Interaction
        ):
            if interaction.user.id == ctx.author.id:
                valid = True
                for key in list(options.keys()):
                    for field in options[key]:
                        if not field.is_valid():
                            valid = False
                            break

                if valid:
                    response.append(options)
                    await interaction.response.edit_message(
                        content="Changes submitted!",
                        view=None,
                        embed=None,
                        delete_after=1,
                    )
                else:
                    await interaction.response.edit_message(
                        content=(f"`Error: Content contains invalid responses!`")
                    )

    buttons = None if display_only else ButtonView()
    paginator = pages.Paginator(pages=page_list, custom_view=buttons)
    await paginator.respond(ctx.interaction, ephemeral=True)
    if buttons:
        try:
            await await_variable(ctx, response)
            return response[0]
        except Exception as e:
            paginator.custom_view = None
            await paginator.goto_page(paginator.current_page)
            await error(ctx, e)
            raise Exception("Timeout")
