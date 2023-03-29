import disnake
from disnake.ext import commands

from depraved_bot.utils.check_roles import check_roles
from depraved_bot.config import RequiredKink, OptionalKink

class RoleCheckerButton(disnake.ui.View):
    def __init__(self, required_kinks: list[RequiredKink], optional_kinks: list[OptionalKink]):
        super().__init__(timeout=None)
        self.required_kinks = required_kinks
        self.optional_kinks = optional_kinks

    @disnake.ui.button(label="I've selected all my kinks", style=disnake.ButtonStyle.primary)
    async def check_roles(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        missing_required, missing_optional = check_roles(inter.author, self.required_kinks, self.optional_kinks)
        
        if not missing_required and not missing_optional:
            role_to_remove = disnake.utils.get(inter.guild.roles, name="Kink List Incomplete")
            await inter.author.remove_roles(role_to_remove)
            await inter.response.send_message("Welcome to the server!", ephemeral = True)
        else:
            response = ""
            if missing_required: 
                response += f"You're missing the following required roles: {', '.join(kink.name for kink in missing_required)}\n"
            if missing_optional:
                response += f"You're missing the following optional roles: {', '.join(kink.name for kink in missing_optional)}"
            await inter.response.send_message(response, ephemeral = True)

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