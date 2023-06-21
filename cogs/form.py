import asyncio

import discord
from discord.ext import pages

from utils import error_text


class Field:
    def __init__(self, label: str, value: any, validate):
        self.label = label
        self.value = value
        self.validate = validate

    def is_valid(self):
        return self.validate(self.value)


async def get_form(ctx, options: dict[list[Field]], display_only=False):
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
        async def edit_button_callback(self, button, interaction):
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
                                    + error_text("invalid")
                                )
                        await interaction.response.edit_message(content="Success")
                        await paginator.goto_page(current_page)

                modal = EditModal(title=list(options.keys())[paginator.current_page])
                await interaction.response.send_modal(modal)

        @discord.ui.button(label="SUBMIT", style=discord.ButtonStyle.green, row=2)
        async def submit_button_callback(self, button, interaction):
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
                        content=error_text("Content contains invalid responses!")
                    )

    paginator = pages.Paginator(
        pages=page_list, custom_view=None if display_only else ButtonView()
    )
    await paginator.respond(ctx.interaction, ephemeral=False)
    while len(response) == 0:
        await asyncio.sleep(1)
    return response[0]
