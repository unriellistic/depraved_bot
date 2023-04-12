import disnake
from disnake.ext import commands

from depraved_bot.structures.kinks import RequiredKink, OptionalKink
from depraved_bot.views import RoleCheckerView

class RoleCheckerCog(commands.Cog):
    def __init__(self, bot: commands.InteractionBot, required_kinks: list[RequiredKink], optional_kinks: list[OptionalKink]):
        self.bot = bot
        self.required_kinks = required_kinks
        self.optional_kinks = optional_kinks

    @commands.slash_command(description="Set up the role checking button in this channel.")
    async def setup_button(self, inter: disnake.ApplicationCommandInteraction):
        required_embed = disnake.Embed(
            title="Required Kinks", 
            description="These kinks are primary to the fantasy of the server. You must agree to engage in CNC (consensual noncon) play involving these kinks to gain access to the server.",
        )
        required_components = [disnake.ui.Button(label=kink.name, custom_id=kink.name) for kink in self.required_kinks]
        await inter.channel.send(embed=required_embed, components=required_components)

        # role checker, to be clicked when user has selected all roles
        view = RoleCheckerView(self.required_kinks, self.optional_kinks)
        await inter.channel.send("Please click this button when you're done selecting all your kink roles.", view=view)

        await inter.response.send_message("Message sent.", ephemeral=True)