import discord
import asyncio
import aiomysql
from discord.ext import commands
from cogs.mysqlinfo import mysqlconfig
from cogs.utility import *

class RoleSyncCog(commands.Cog, name="Fun Commands"):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(SyncMemberRoles(self))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        discordguild = self.bot.get_guild(rcrpguild)
        sql = await aiomysql.connect(** mysqlconfig)
        cursor = await sql.cursor()
        await cursor.execute("SELECT discordrole FROM discordroles WHERE discorduser = %s", (member.id, ))

        roles = []
        results = await cursor.fetchall()
        await cursor.close()
        sql.close()
        for role in results:
            if role[0] == rcrpguild: #check to see if the role is @everyone, skip it if so
                continue
            roles.append(discordguild.get_role(role[0]))
        await member.add_roles(*roles)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if not rcrp_utility.isverified(after) or before.roles == after.roles:
            return

        sql = await aiomysql.connect(** mysqlconfig)
        cursor = await sql.cursor()

        #check for removed roles and delete them
        for role in before.roles:
            if role.id not in after.roles:
                await cursor.execute("DELETE FROM discordroles WHERE discorduser = %s AND discordrole = %s", (before.id, role.id))
        await cursor.close()

        #check for added roles and insert them
        cursor = await sql.cursor()
        for role in after.roles:
            if role.id not in before.roles:
                if role.id == rcrpguild: #check to see if role is @everyone, skip it if so
                    continue;
                await cursor.execute("INSERT INTO discordroles (discorduser, discordrole) VALUES (%s, %s)", (before.id, role.id))
                await sql.commit()

        await cursor.close()
        sql.close()

async def SyncMemberRoles(self):
    while 1:
        discordguild = self.bot.get_guild(rcrpguild)
        sql = await aiomysql.connect(** mysqlconfig)
        for member in self.bot.get_all_members():
            if rcrp_utility.ismanagement(member) == True:
                continue

            cursor = await sql.cursor(aiomysql.DictCursor)
            await cursor.execute("SELECT id, Helper, Tester, AdminLevel, Premium FROM masters WHERE discordid = %s", (member.id, ))
            data = await cursor.fetchone()
            await cursor.close()

            if data is None:
                continue

            banned = await rcrp_utility.isbanned(data['id'])

            #remove roles a member shouldn't have
            removeroles = []
            if helperrole in [role.id for role in member.roles] and data['Helper'] == 0: #member isn't a helper but has the role
                removeroles.append(discordguild.get_role(helperrole))
            if testerrole in [role.id for role in member.roles] and data['Tester'] == 0: #member isn't a tester but has the role
                removeroles.append(discordguild.get_role(testerrole))
            if adminrole in [role.id for role in member.roles] and data['AdminLevel'] == 0: #member isn't an admin but has the role
                removeroles.append(discordguild.get_role(adminrole))
            if premiumrole in [role.id for role in member.roles] and data['Premium'] == 0: #member isn't an admin but has the role
                removeroles.append(discordguild.get_role(premiumrole))
            if bannedrole in [role.id for role in member.roles] and banned is False: #member isn't banned but has the role
                removeroles.append(discordguild.get_role(bannedrole))
            if removeroles:
                await member.remove_roles(*removeroles)

            #add roles a member should have
            addroles = []
            if helperrole not in [role.id for role in member.roles] and data['Helper'] == 1: #member is a helper but doesn't have the role
                addroles.append(discordguild.get_role(helperrole))
            if testerrole not in [role.id for role in member.roles] and data['Tester'] == 1: #member is a tester but doesn't have the role
                addroles.append(discordguild.get_role(testerrole))
            if adminrole not in [role.id for role in member.roles] and data['AdminLevel'] != 0: #member is an admin but doesn't have the role
                addroles.append(discordguild.get_role(adminrole))
            if premiumrole not in [role.id for role in member.roles] and data['Premium'] != 0: #member is an admin but doesn't have the role
                addroles.append(discordguild.get_role(premiumrole))
            if bannedrole not in [role.id for role in member.roles] and banned is True: #member isn't banned but has the role
                addroles.append(discordguild.get_role(bannedrole))
            if verifiedrole not in [role.id for role in member.roles]:
                addroles.append(discordguild.get_role(verifiedrole))
            if addroles:
                await member.add_roles(*addroles)
        sql.close()
        await asyncio.sleep(60) #check every minute

def setup(bot):
    bot.add_cog(RoleSyncCog(bot))