import disnake
from disnake.ext import commands

from sqlalchemy import Engine, Table
from sqlalchemy.dialects.postgresql import insert

class CacheRolesCog(commands.Cog):
    def __init__(self, bot: commands.InteractionBot, engine: Engine, members_table: Table):
        self.bot = bot
        self.engine = engine
        self.members_table = members_table

    @commands.Cog.listener()
    async def on_member_update(self, before: disnake.Member, after: disnake.Member):
        # called whenever a member's data is updated. We only care about when the roles are changed
        if before.roles != after.roles:
            member_id = after.id
            new_roles = [role.id for role in after.roles]

            stmt = insert(self.members_table).values(id=member_id, roles=new_roles).on_conflict_do_update(
                index_elements=["id"],
                set_={"roles": new_roles}
            )

            with self.engine.connect() as conn:
                await conn.execute(stmt)

    