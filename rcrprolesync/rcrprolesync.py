import discord
import asyncio
import aiomysql
from redbot.core import commands
from .config import mysqlconfig
from .utility import member_is_verified, member_is_management, rcrpguildid, helperrole, testerrole, adminrole, premiumrole, bannedrole, verifiedrole

class RCRPRoleSync(commands.Cog, name="Role sync"):
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.bot.loop.create_task(self.sync_member_roles())

    async def verified_filter(self, member):
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
            rcrpguild = self.bot.get_guild(rcrpguildid)
            sql = await aiomysql.connect(**mysqlconfig)
            cursor = await sql.cursor()
            await cursor.execute("SELECT discordrole FROM discordroles WHERE discorduser = %s", (member.id, ))

            roles = []
            results = await cursor.fetchall()
            await cursor.close()
            sql.close()
            for role in results:
                if role[0] == rcrpguildid: #check to see if the role is @everyone, skip it if so
                    continue
                roles.append(rcrpguild.get_role(role[0]))
            await member.add_roles(*roles)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if not member_is_verified(after) or before.roles == after.roles or after.guild.id != rcrpguildid:
            return

        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor()

        #check for removed roles and delete them
        for role in before.roles:
            if role.id not in after.roles:
                await cursor.execute("DELETE FROM discordroles WHERE discorduser = %s AND discordrole = %s", (before.id, role.id))

        #check for added roles and insert them
        cursor = await sql.cursor()
        for role in after.roles:
            if role.id not in before.roles:
                if role.id == rcrpguildid: #check to see if role is @everyone, skip it if so
                    continue
                await cursor.execute("INSERT INTO discordroles (discorduser, discordrole) VALUES (%s, %s)", (before.id, role.id))

        await cursor.close()
        sql.close()
    
    async def sync_member_roles(self):
        while 1:
            rcrpguild = await self.bot.fetch_guild(rcrpguildid)
            sql = await aiomysql.connect(**mysqlconfig)
            cursor = await sql.cursor(aiomysql.DictCursor)
            async for member in rcrpguild.fetch_members(limit = None).filter(self.verified_filter):
                if member_is_management(member) == True or member_is_verified(member) == False:
                    continue

                await cursor.execute("SELECT id, Helper, Tester, AdminLevel, Premium FROM masters WHERE discordid = %s", (member.id, ))
                data = await cursor.fetchone()

                if data is None:
                    continue

                banned = await self.account_is_banned(data['id'])

                #remove roles a member shouldn't have
                removeroles = []
                if helperrole in [role.id for role in member.roles] and data['Helper'] == 0: #member isn't a helper but has the role
                    removeroles.append(rcrpguild.get_role(helperrole))
                if testerrole in [role.id for role in member.roles] and data['Tester'] == 0: #member isn't a tester but has the role
                    removeroles.append(rcrpguild.get_role(testerrole))
                if adminrole in [role.id for role in member.roles] and data['AdminLevel'] == 0: #member isn't an admin but has the role
                    removeroles.append(rcrpguild.get_role(adminrole))
                if premiumrole in [role.id for role in member.roles] and data['Premium'] == 0: #member isn't an admin but has the role
                    removeroles.append(rcrpguild.get_role(premiumrole))
                if bannedrole in [role.id for role in member.roles] and banned is False: #member isn't banned but has the role
                    removeroles.append(rcrpguild.get_role(bannedrole))
                if removeroles:
                    await member.remove_roles(*removeroles)

                #add roles a member should have
                addroles = []
                if helperrole not in [role.id for role in member.roles] and data['Helper'] == 1: #member is a helper but doesn't have the role
                    addroles.append(rcrpguild.get_role(helperrole))
                if testerrole not in [role.id for role in member.roles] and data['Tester'] == 1: #member is a tester but doesn't have the role
                    addroles.append(rcrpguild.get_role(testerrole))
                if adminrole not in [role.id for role in member.roles] and data['AdminLevel'] != 0: #member is an admin but doesn't have the role
                    addroles.append(rcrpguild.get_role(adminrole))
                if premiumrole not in [role.id for role in member.roles] and data['Premium'] != 0: #member is an admin but doesn't have the role
                    addroles.append(rcrpguild.get_role(premiumrole))
                if bannedrole not in [role.id for role in member.roles] and banned is True: #member isn't banned but has the role
                    addroles.append(rcrpguild.get_role(bannedrole))
                if verifiedrole not in [role.id for role in member.roles]:
                    addroles.append(rcrpguild.get_role(verifiedrole))
                if addroles:
                    await member.add_roles(*addroles)

            await cursor.close()
            sql.close()
            await asyncio.sleep(60) #check every minute
