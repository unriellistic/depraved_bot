import disnake
from disnake.ext import commands

from sqlalchemy import Engine, Table, select
from sqlalchemy.dialects.postgresql import insert

class CacheRolesCog(commands.Cog):
    def __init__(self, bot: commands.InteractionBot, engine: Engine, members_table: Table):
        self.bot = bot
        self.engine = engine
        self.members_table = members_table

    @commands.Cog.listener()
    async def on_member_update(self, before: disnake.Member, after: disnake.Member) -> None:
        # called whenever a member's data is updated. We only care about when the roles are changed
        if before.roles != after.roles:
            member_id = after.id
            new_roles = [role.id for role in after.roles]

            stmt = insert(self.members_table).values(id=member_id, roles=new_roles).on_conflict_do_update(
                index_elements=["id"],
                set_={"roles": new_roles}
            )

            with self.engine.connect() as conn:
                conn.execute(stmt)

    @commands.Cog.listener()
    async def on_member_join(self, member: disnake.Member) -> None:
        stmt = select(self.members_table).where(self.members_table.c.id==member.id).limit(1)
        with self.engine.connect() as conn:
            old_member = conn.execute(stmt).first()

        if old_member:
            for role_id in old_member.roles[1:]:
                await member.add_roles(member.guild.get_role(role_id))
