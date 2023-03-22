import disnake
from disnake.ext import commands

class PingCog(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot

    @commands.slash_command(description="Ping me to check if I'm alive.")
    async def ping(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.send_message("Hello! I'm alive!")