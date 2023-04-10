import disnake

from depraved_bot.structures.kinks import RequiredKink, OptionalKink
from depraved_bot.utils import check_roles

class RoleCheckerView(disnake.ui.View):
    def __init__(self, required_kinks: list[RequiredKink], optional_kinks: list[OptionalKink]):
        super().__init__(timeout=None)
        self.required_kinks = required_kinks
        self.optional_kinks = optional_kinks

    @disnake.ui.button(label="I've selected all my kinks", style=disnake.ButtonStyle.primary)
    async def check_roles(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
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
