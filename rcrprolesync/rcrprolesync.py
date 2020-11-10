import discord
import asyncio
import aiomysql
from redbot.core import commands
from .config import mysqlconfig

#rcrp guild ID
rcrpguildid = 93142223473905664

#various role IDs for syncing
adminrole = 293441894585729024
bannedrole = 592730783924486168
helperrole = 293441873945821184
managementrole = 310927289317588992
ownerrole = 293303836125298690
premiumrole = 534479263966167069
testerrole = 293441807055060993
verifiedrole = 293441047244308481

def member_is_verified(member: discord.Member):
    return (verifiedrole in [role.id for role in member.roles])

def member_is_management(member: discord.Member):
    role_ids = [role.id for role in member.roles]
    if managementrole in role_ids or ownerrole in role_ids:
        return True
    else:
        return False

class RCRPRoleSync(commands.Cog, name = "RCRP Role Sync"):
    def __init__(self, bot: discord.Client):
        self.bot: discord.Client = bot
        self.sync_task = self.bot.loop.create_task(self.sync_member_roles())

    async def verified_filter(self, member: discord.Member):
        return member_is_verified(member) == True

    async def account_is_banned(self, accountid):
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor()
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
            sql = await aiomysql.connect(**mysqlconfig)
            cursor = await sql.cursor()

            await cursor.execute("SELECT discordrole FROM discordroles WHERE discorduser = %s", (member.id, ))
            results = await cursor.fetchall()
            await cursor.close()
            sql.close()

            roles = list(results)
            roles.remove(rcrpguildid)
            for role in results:
                role = rcrpguild.get_role(role)
                roles.append(role)
            await member.add_roles(*roles)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if member_is_verified(after) == False or before.roles == after.roles or after.guild.id != rcrpguildid:
            return

        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor()

        #delete previous roles
        await cursor.execute("DELETE FROM discordroles WHERE discorduser = %s", (before.id, ))

        #insert roles
        role_ids = [role.id for role in after.roles]
        role_ids.remove(rcrpguildid)
        for role in role_ids:
            await cursor.execute("INSERT INTO discordroles (discorduser, discordrole) VALUES (%s, %s)", (before.id, role.id, ))

        await cursor.close()
        sql.close()

    async def assign_roles(self, field: str, rcrpguild: discord.Guild, role: discord.Role):
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor(aiomysql.DictCursor)

        await cursor.execute("SELECT discordid FROM masters WHERE %s != 0 AND discordid != 0", (field, ))
        results = await cursor.fetchall()
        await cursor.close()
        sql.close()

        rcrp_ids = list(results)
        discord_ids = [member.id for member in role.members]

        #assign roles to those who should have it
        for member_id in rcrp_ids:
            if member_id not in discord_ids:
                member = await rcrpguild.get_member(member_id)
                if member is not None and member_is_management(member) == False:
                    await member.add_roles(role)

        #remove roles from those who shouldn't have it
        for member_id in discord_ids:
            if member_id not in rcrp_ids:
                member = await rcrpguild.get_member(member_id)
                if member is not None and member_is_management(member) == False:
                    await member.remove_roles(role)
    
    async def sync_member_roles(self):
        while 1:
            rcrpguild = await self.bot.fetch_guild(rcrpguildid)
            try:
                admin = rcrpguild.get_role(adminrole)
                tester = rcrpguild.get_role(testerrole)
                helper = rcrpguild.get_role(helperrole)
                premium = rcrpguild.get_role(premiumrole)
                await self.assign_roles('AdminLevel', rcrpguild, admin)
                await self.assign_roles('Tester', rcrpguild, tester)
                await self.assign_roles('Helper', rcrpguild, helper)
                await self.assign_roles('Premium', rcrpguild, premium)
            except Exception as e:
                channel = rcrpguild.get_channel(775767985586962462)
                await channel.send(f'An exception occurred in role sync. Exception: {e}')
            await asyncio.sleep(60) #check every minute
    
    def __unload(self):
        self.sync_task.cancel()
