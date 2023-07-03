import discord
from discord.ext import pages
from discord.ext.commands import Context

from utils import await_variable, error


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
