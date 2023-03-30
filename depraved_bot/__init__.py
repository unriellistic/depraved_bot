import os

import disnake
from disnake.ext import commands
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Table, Column, BigInteger, String

from depraved_bot.config import load_config_from_sql

from depraved_bot.cogs import PingCog, RoleCheckerCog

# bot initialization
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
    # get bot token and database from .env file
    load_dotenv()
    env = os.getenv("ENVIRONMENT", "dev")

    if env in ["dev", "development"]:
        bot_token = os.getenv("DISCORD_TOKEN_DEV")
        database_addr = os.getenv("DATABASE_DEV")
    elif env in ["prod", "production"]:
        bot_token = os.getenv("DISCORD_TOKEN_PROD")
        database_addr = os.getenv("DATABASE_PROD")
    else:
        print("invalid ENVIRONMENT, exiting.")

    # initialize database
    engine = create_engine(database_addr)
    metadata_obj = MetaData()

    # initialize data tables and get existing data
    table_required = Table(
        "required_kinks",
        metadata_obj,
        Column("name", String, primary_key=True),
        Column("id", BigInteger),
        autoload_with=engine,
    )
    table_optional = Table(
        "optional_kinks",
        metadata_obj,
        Column("name", String, primary_key=True),
        Column("green", BigInteger),
        Column("yellow", BigInteger),
        Column("red", BigInteger),
        autoload_with=engine,
    )

    # process the raw table data
    required_kinks, optional_kinks = load_config_from_sql(engine, table_required, table_optional)

    # add bot commands
    bot.add_cog(PingCog(bot))
    bot.add_cog(RoleCheckerCog(bot, required_kinks, optional_kinks))

    bot.run(bot_token)