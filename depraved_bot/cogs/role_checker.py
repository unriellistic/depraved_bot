from typing import Union

import disnake
from disnake.ext import commands

from depraved_bot.structures.kinks import RequiredKink, OptionalKink
from depraved_bot.views import RoleCheckerView
from depraved_bot.utils import check_roles

class RoleCheckerCog(commands.Cog):
    def __init__(self, bot: commands.InteractionBot, required_kinks: list[RequiredKink], optional_kinks: list[OptionalKink]):
        self.bot = bot
        self.required_kinks = required_kinks
        self.optional_kinks = optional_kinks

    @commands.slash_command(description="Set up the kink role buttons in this channel.")
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
        #view = RoleCheckerView(self.required_kinks, self.optional_kinks)
        #await inter.channel.send("Please click this button when you're done selecting all your kink roles.", view=view)

        await inter.channel.send("Please click this button when you're done selecting all your kink roles.", components=[
            disnake.ui.Button(label="I've selected all my kinks", style=disnake.ButtonStyle.primary, custom_id="check_roles")
        ])

        # confirmation of completion
        await inter.edit_original_response("Message sent.")

    

    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        # if check_roles button was clicked, check roles
        # check which roles are missing
        missing_required, missing_optional = check_roles(inter.author, self.required_kinks, self.optional_kinks)
        
        # if all roles are present
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

        # if the button for a required kink was clicked, add the role
        for kink in self.required_kinks:
            if kink.name == inter.component.custom_id:
                role_to_add = disnake.utils.get(inter.guild.roles, name=kink.name)
                await inter.author.add_roles(role_to_add)

                await inter.send(f"Assigned role {kink.name} to you.", ephemeral=True)
                break

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: disnake.RawReactionActionEvent):
        rxn_name = payload.emoji.name
        msg_id = payload.message_id
        ch_id = payload.channel_id
        user_id = payload.user_id
        guild_id = payload.guild_id

        channel = self.bot.get_channel(ch_id)
        msg = await channel.fetch_message(msg_id)
        guild = self.bot.get_guild(guild_id)
        member = guild.get_member(user_id)

        # if the reaction was added by this bot
        if user_id == self.bot.user.id:
            return
        
        # if the message is not from this bot
        if msg.author.id != self.bot.user.id:
            return
        
        # message has no embeds (not the right message)
        if not msg.embeds:
            return
        
        kink_name = msg.embeds[0].title
        kink_to_add = next((x for x in self.optional_kinks if x.name == kink_name), None)

        # kink name isn't in the list for some reason (reaction done on wrong embed)
        if not kink_to_add:
            return

        green_role = guild.get_role(kink_to_add.green)
        yellow_role = guild.get_role(kink_to_add.yellow)
        red_role = guild.get_role(kink_to_add.red)

        # actually add the role now, based on the emoji
        if rxn_name == "🟩":
            await member.add_roles(green_role)
            await member.remove_roles(yellow_role, red_role)
        elif rxn_name == "🟨":
            await member.add_roles(yellow_role)
            await member.remove_roles(green_role, red_role)
        elif rxn_name == "🟥":
            await member.add_roles(red_role)
            await member.remove_roles(green_role, yellow_role)

            
        # remove other reactions on the message (this will also trigger reaction remove event and remove associated roles)
        for existing_reaction in msg.reactions:
            # don't remove the reaction they just added
            if existing_reaction.emoji != payload.emoji.name:
                await msg.remove_reaction(existing_reaction, member)
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: disnake.RawReactionActionEvent):
        rxn_name = payload.emoji.name
        msg_id = payload.message_id
        ch_id = payload.channel_id
        user_id = payload.user_id
        guild_id = payload.guild_id

        channel = self.bot.get_channel(ch_id)
        msg = await channel.fetch_message(msg_id)
        guild = self.bot.get_guild(guild_id)
        member = guild.get_member(user_id)

        # if the message is not from this bot
        if msg.author.id != self.bot.user.id:
            return
        
        # message has no embeds (not the right message)
        if not msg.embeds:
            return
        
        kink_name = msg.embeds[0].title
        kink_to_add = next((x for x in self.optional_kinks if x.name == kink_name), None)

        # kink name isn't in the list for some reason (reaction done on wrong embed)
        if not kink_to_add:
            return

        # figure out which role to remove, based on the emoji
        if rxn_name == "🟩":
            role = kink_to_add.green
        elif rxn_name == "🟨":
            role = kink_to_add.yellow
        elif rxn_name == "🟥":
            role = kink_to_add.red

        await member.remove_roles(member.guild.get_role(role))