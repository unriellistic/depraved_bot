from typing import Union

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
        # show "bot is thinking..." so the interaction doesn't show as failed
        await inter.response.defer(ephemeral=True)

        # embed (the blockquote thing)
        required_embed = disnake.Embed(
            title="Required Kinks", 
            description="These kinks are primary to the fantasy of the server. You must agree to engage in CNC (consensual non-consent) play involving these kinks to gain access to the server.",
        )
        required_components = [disnake.ui.Button(label=kink.name, custom_id=kink.name) for kink in self.required_kinks]
        await inter.channel.send(embed=required_embed, components=required_components)

        for kink in self.optional_kinks:
            embed = disnake.Embed(
                title=kink.name,
                description=kink.description,
            )
            msg = await inter.channel.send(embed=embed)
            await msg.add_reaction("🟩")
            await msg.add_reaction("🟨")
            await msg.add_reaction("🟥")
        
        # role checker, to be clicked when user has selected all roles
        view = RoleCheckerView(self.required_kinks, self.optional_kinks)
        await inter.channel.send("Please click this button when you're done selecting all your kink roles.", view=view)

        # confirmation of completion
        await inter.edit_original_response("Message sent.")

    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        # if the button for a required kink was clicked, add the role
        for kink in self.required_kinks:
            if kink.name == inter.component.custom_id:
                role_to_add = disnake.utils.get(inter.guild.roles, name=kink.name)
                await inter.author.add_roles(role_to_add)