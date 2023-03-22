import disnake
from disnake.ext import commands

from depraved_bot.check_roles import check_roles
from depraved_bot.config import RequiredKink, OptionalKink

class RoleCheckerButton(disnake.ui.View):
    def __init__(self, required_kinks: list[RequiredKink], optional_kinks: list[OptionalKink]):
        super().__init__(timeout=None)
        self.required_kinks = required_kinks
        self.optional_kinks = optional_kinks

    @disnake.ui.button(label="I've selected all my kinks")
    async def check_roles(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        missing_required, missing_optional = check_roles(inter.author, self.required_kinks, self.optional_kinks)
        
        if not missing_required and not missing_optional:
            # remove role
            await inter.response.send_message("Welcome to the server!", ephemeral = True)
        else:
            await inter.response.send_message("You're missing one or more roles.", ephemeral = True)

class RoleCheckerCog(commands.Cog):
    def __init__(self, bot: commands.InteractionBot, required_kinks: list[RequiredKink], optional_kinks: list[OptionalKink]):
        self.bot = bot
        self.required_kinks = required_kinks
        self.optional_kinks = optional_kinks

    @commands.slash_command(description="Set up the role checking button in this channel.")
    async def setup_button(self, inter: disnake.ApplicationCommandInteraction):
        view = RoleCheckerButton(self.required_kinks, self.optional_kinks)
        await inter.channel.send("Please click this button when you're done selecting all your kink roles.", view=view)
        await inter.response.send_message("Message sent.", ephemeral=True)