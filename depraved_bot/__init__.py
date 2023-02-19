import disnake
from disnake.ext import commands

from depraved_bot.config import *

command_sync_flags = commands.CommandSyncFlags.default()
command_sync_flags.sync_commands_debug = True

intents = disnake.Intents.default()

bot = commands.Bot(
    command_sync_flags=command_sync_flags,
    intents=intents,
)

@bot.slash_command(description="Ping me to check if I'm alive.")
async def ping(interaction):
    await interaction.response.send_message("Hello! I'm alive!")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}! (ID: {bot.user.id})\n-------")

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN_ALPHA) # change to DISCORD_TOKEN for production