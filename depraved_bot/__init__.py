import os
import disnake
from disnake.ext import commands
from dotenv import load_dotenv

from depraved_bot.check_roles import check_roles

command_sync_flags = commands.CommandSyncFlags.default()
command_sync_flags.sync_commands_debug = True

intents = disnake.Intents.default()

bot = commands.InteractionBot(
    command_sync_flags=command_sync_flags,
    intents=intents,
)

@bot.slash_command(description="Ping me to check if I'm alive.")
async def ping(inter: disnake.ApplicationCommandInteraction):
    await inter.response.send_message("Hello! I'm alive!")


class RoleCheckButton(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label="I've selected all my kinks")
    async def check_roles(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        missing_required, missing_optional = check_roles(inter.author)
        
        if not missing_required and not missing_optional:
            # remove role
            await inter.response.send_message("Welcome to the server!", ephemeral = True)
        else:
            await inter.response.send_message("You're missing one or more roles.", ephemeral = True)

@bot.slash_command(description="Set up the role checking button in this channel.")
async def setup_button(inter: disnake.ApplicationCommandInteraction):
    view = RoleCheckButton()
    await inter.channel.send("Please click this button when you're done selecting all your kink roles.", view=view)
    await inter.response.send_message("Message sent.")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}! (ID: {bot.user.id})\n-------")

if __name__ == "__main__":
    load_dotenv()
    env = os.getenv("ENVIRONMENT", "dev")
    if env in ["dev", "development"]:
        bot.run(os.getenv("DISCORD_TOKEN_DEV"))
    elif env in ["prod", "production"]:
        bot.run(os.getenv("DISCORD_TOKEN_PROD"))
    else:
        print("invalid ENVIRONMENT, exiting.")