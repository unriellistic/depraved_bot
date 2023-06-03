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
        
        # remove other reactions on the message (this will also trigger reaction remove event and remove associated roles)
        for existing_reaction in msg.reactions:
            # don't remove the reaction they just added
            if existing_reaction.emoji == payload.emoji.name:
                continue
            rxn_users = await existing_reaction.users().flatten()
            if user_id in (user.id for user in rxn_users):
                await msg.remove_reaction(existing_reaction, member)
                
        green_role = guild.get_role(kink_to_add.green)
        yellow_role = guild.get_role(kink_to_add.yellow)
        red_role = guild.get_role(kink_to_add.red)

        # actually add the role now, based on the emoji
        if rxn_name == "🟩":
            await member.add_roles(green_role)
        elif rxn_name == "🟨":
            await member.add_roles(yellow_role)
        elif rxn_name == "🟥":
            await member.add_roles(red_role)        

    # @commands.Cog.listener()
    # async def on_reaction_add(self, reaction: disnake.Reaction, member: disnake.Member):
    #     # if the reaction was added by this bot
    #     if member.id == self.bot.user.id:
    #         return

    #     # if the message is not from this bot
    #     if reaction.message.author.id != self.bot.user.id:
    #         return
        
    #     # message has no embeds (not the right message)
    #     if not reaction.message.embeds:
    #         return
        
    #     kink_name = reaction.message.embeds[0].title
    #     kink_to_add = next((x for x in self.optional_kinks if x.name == kink_name), None)

    #     # kink name isn't in the list for some reason (reaction done on wrong embed)
    #     if not kink_to_add:
    #         return
        
    #     # remove other reactions on the message (this will also trigger reaction remove event and remove associated roles)
    #     for existing_reaction in reaction.message.reactions:
    #         # don't remove the reaction they just added
    #         if existing_reaction == reaction:
    #             continue
    #         rxn_users = await existing_reaction.users().flatten()
    #         if member.id in (user.id for user in rxn_users):
    #             await reaction.message.remove_reaction(existing_reaction, member)


    #     green_role = member.guild.get_role(kink_to_add.green)
    #     yellow_role = member.guild.get_role(kink_to_add.yellow)
    #     red_role = member.guild.get_role(kink_to_add.red)

    #     # actually add the role now, based on the emoji
    #     if reaction.emoji == "🟩":
    #         await member.add_roles(green_role)
    #     elif reaction.emoji == "🟨":
    #         await member.add_roles(yellow_role)
    #     elif reaction.emoji == "🟥":
    #         await member.add_roles(red_role)

    # @commands.Cog.listener()
    # async def on_reaction_remove(self, reaction: disnake.Reaction, member: disnake.Member):
    #     # if the message is not from this bot
    #     if reaction.message.author.id != self.bot.user.id:
    #         return
        
    #     # message has no embeds (not the right message)
    #     if not reaction.message.embeds:
    #         return
        
    #     kink_name = reaction.message.embeds[0].title
    #     kink_to_add = next((x for x in self.optional_kinks if x.name == kink_name), None)

    #     # kink name isn't in the list for some reason (likely reaction done on wrong embed)
    #     if not kink_to_add:
    #         return
        
    #     # figure out which role to remove, based on the emoji
    #     if reaction.emoji == "🟩":
    #         role = kink_to_add.green
    #     elif reaction.emoji == "🟨":
    #         role = kink_to_add.yellow
    #     elif reaction.emoji == "🟥":
    #         role = kink_to_add.red

    #     await member.remove_roles(member.guild.get_role(role))
    
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