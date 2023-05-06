import discord
import aiomysql
from aiomysql import Cursor
from discord.ext import tasks
from redbot.core import commands
from redbot.core.bot import Red

# rcrp guild ID
rcrpguildid = 93142223473905664

# various role IDs for syncing
adminrole = 293441894585729024
bannedrole = 592730783924486168
helperrole = 293441873945821184
managementrole = 310927289317588992
ownerrole = 293303836125298690
premiumrole = 534479263966167069
testerrole = 293441807055060993
verifiedrole = 293441047244308481
fcrole = 393186381306003466
farole = 813872907612586004


def member_is_verified(member: discord.Member):
    return (verifiedrole in [role.id for role in member.roles])


def member_is_management(member: discord.Member):
    role_ids = [role.id for role in member.roles]
    if managementrole in role_ids or ownerrole in role_ids:
        return True
    else:
        return False


class RCRPRoleSync(commands.Cog, name="RCRP Role Sync"):
    def __init__(self, bot: Red):
        self.bot = bot
        self.sync_member_roles.start()

    def cog_unload(self):
        self.sync_member_roles.cancel()

    async def log(self, message: str):
        rcrpguild = self.bot.get_guild(rcrpguildid)
        logchannel = rcrpguild.get_channel(775767985586962462)
        await logchannel.send(message)

    async def verified_filter(self, member: discord.Member):
        return member_is_verified(member) is True

    async def account_is_banned(self, accountid):
        mysqlconfig = await self.bot.get_shared_api_tokens('mysql')
        sql = await aiomysql.connect(**mysqlconfig)
        cursor: Cursor = await sql.cursor()
        await cursor.execute("SELECT NULL FROM bans WHERE MasterAccount = %s", (accountid, ))
        data = await cursor.fetchone()
        await cursor.close()
        sql.close()

        if data is None:
            return False
        else:
            return True

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.guild.id == rcrpguildid:
            rcrpguild: discord.Guild = self.bot.get_guild(rcrpguildid)
            mysqlconfig = await self.bot.get_shared_api_tokens('mysql')
            sql = await aiomysql.connect(**mysqlconfig)
            cursor: Cursor = await sql.cursor()

            count = await cursor.execute("SELECT discordrole FROM discordroles WHERE discorduser = %s", (member.id, ))
            if count != 0:
                results = await cursor.fetchall()

                roles = []
                for roleid in results:
                    role = rcrpguild.get_role(roleid[0])
                    if role is None or roleid[0] == rcrpguildid:
                        continue
                    else:
                        roles.append(role)

                await member.add_roles(*roles)
            await cursor.close()
            sql.close()

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if member_is_verified(after) is False or before.roles == after.roles or after.guild.id != rcrpguildid:
            return

        mysqlconfig = await self.bot.get_shared_api_tokens('mysql')
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor()

        # delete previous roles
        await cursor.execute("DELETE FROM discordroles WHERE discorduser = %s", (before.id, ))

        # insert roles
        role_ids = [role.id for role in after.roles]
        if rcrpguildid in role_ids:
            role_ids.remove(rcrpguildid)
        for role in role_ids:
            await cursor.execute("INSERT INTO discordroles (discorduser, discordrole) VALUES (%s, %s)", (before.id, role, ))

        await cursor.close()
        sql.close()

    async def assign_roles(self, field: str, role_id: int):
        mysqlconfig = await self.bot.get_shared_api_tokens('mysql')
        sql = await aiomysql.connect(**mysqlconfig)
        cursor: Cursor = await sql.cursor()

        if role_id == bannedrole:
            await cursor.execute('SELECT masters.discordid FROM bans JOIN masters ON bans.MasterAccount = masters.id WHERE discordid != 0')
        else:
            await cursor.execute(f"SELECT discordid FROM masters WHERE {field} != 0 AND discordid != 0")

        results = await cursor.fetchall()
        await cursor.close()
        sql.close()

        rcrp_ids = []
        for member_id in results:
            rcrp_ids.append(member_id[0])

        rcrpguild = self.bot.get_guild(rcrpguildid)
        role = rcrpguild.get_role(role_id)
        discord_ids = [member.id for member in role.members]

        # remove roles from those who shouldn't have it
        for member_id in discord_ids:
            if member_id not in rcrp_ids:
                member = rcrpguild.get_member(member_id)
                if member is not None and member_is_management(member) is False:
                    await member.remove_roles(role)

        # assign roles to those who should have it
        for member_id in rcrp_ids:
            if member_id not in discord_ids:
                member = rcrpguild.get_member(member_id)
                if member is not None and member_is_management(member) is False:
                    await member.add_roles(role)

    @tasks.loop(seconds=60.0)
    async def sync_member_roles(self):
        await self.assign_roles('AdminLevel', adminrole)
        await self.assign_roles('Tester', testerrole)
        await self.assign_roles('Helper', helperrole)
        await self.assign_roles('Premium', premiumrole)
        await self.assign_roles('FC', fcrole)
        await self.assign_roles('HoF', farole)
        await self.assign_roles('Banned', bannedrole)
        await self.assign_roles('id', verifiedrole)  # checking for id because every account has an ID and we want to check every verified account here

    @sync_member_roles.before_loop
    async def before_sync_member_roles(self):
        await self.bot.wait_until_ready()
