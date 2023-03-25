import os
import disnake
from disnake.ext import commands
from dotenv import load_dotenv

from depraved_bot.config import load_config
from depraved_bot.check_roles import check_roles

from depraved_bot.cogs import ping, role_checker

command_sync_flags = commands.CommandSyncFlags.default()
command_sync_flags.sync_commands_debug = True

intents = disnake.Intents.default()

bot = commands.InteractionBot(
    command_sync_flags=command_sync_flags,
    intents=intents,
)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}! (ID: {bot.user.id})\n-------")

if __name__ == "__main__":
    load_dotenv()
    env = os.getenv("ENVIRONMENT", "dev")

    if env in ["dev", "development"]:
        bot_token = os.getenv("DISCORD_TOKEN_DEV")
        required_kinks, optional_kinks = load_config(os.getenv("CONFIG_PATH_DEV"))
    elif env in ["prod", "production"]:
        bot_token = os.getenv("DISCORD_TOKEN_PROD")
        required_kinks, optional_kinks = load_config(os.getenv("CONFIG_PATH_PROD"))
    else:
        print("invalid ENVIRONMENT, exiting.")

    bot.add_cog(ping.PingCog(bot))
    bot.add_cog(role_checker.RoleCheckerCog(bot, required_kinks, optional_kinks))

    bot.run(bot_token)