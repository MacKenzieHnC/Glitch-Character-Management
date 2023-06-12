import asyncio

import discord
from discord.ext import pages


async def get_form_input(ctx, options: dict[str : dict[str:any]]):
    def get_page(key):
        page = discord.Embed(title=page_name)
        for key in options[page_name]:
            page.add_field(name=key, value=options[page_name][key], inline=False)
        return page

    page_list: list[discord.Embed] = []
    for page_name in options.keys():
        page_list.append(get_page(page_name))

    class EditButton(discord.ui.View):
        @discord.ui.button(label="EDIT", style=discord.ButtonStyle.primary)
        async def button_callback(self, button, interaction):
            key = list(options.keys())[paginator.current_page]

            class EditModal(discord.ui.Modal):
                def __init__(self, *args, **kwargs) -> None:
                    super().__init__(*args, **kwargs)
                    for field in options[key]:
                        self.add_item(discord.ui.InputText(label=field))

                async def callback(self, interaction: discord.Interaction):
                    current_page = paginator.current_page
                    fields = list(options[key].keys())
                    for i in range(len(fields)):
                        options[key][fields[i]] = self.children[i].value
                        page_list[current_page].fields[i].value = self.children[i].value
                    await interaction.response.edit_message(content="Success")
                    await paginator.goto_page(current_page)

            modal = EditModal(title=list(options.keys())[paginator.current_page])
            await interaction.response.send_modal(modal)

    paginator = pages.Paginator(pages=page_list, custom_view=EditButton())
    await paginator.respond(ctx.interaction, ephemeral=False)
