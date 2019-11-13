import discord
import asyncio
import mysql.connector
from discord.ext import commands
from cogs.mysqlinfo import mysqlconfig
from cogs.utility import rcrp_utility

class RoleSyncCog(commands.Cog, name="Fun Commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.loop.create_task(SyncMemberRoles(self))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        discordguild = self.bot.get_guild(rcrp_utility.getrcrpguild())
        sql = mysql.connector.connect(** mysqlconfig)
        cursor = sql.cursor()
        cursor.execute("SELECT discordrole FROM discordroles WHERE discorduser = %s", (member.id, ))

        roles = []
        for roleid in cursor:
            role = int(roleid[0])
            if role == rcrp_utility.getrcrpguild(): ##check to see if the role is @everyone, skip it if so
                continue
            roles.append(discordguild.get_role(int(roleid[0])))
        await member.add_roles(*roles)

        cursor.close()
        sql.close()

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if not rcrp_utility.isverified(after) or before.roles == after.roles:
            return

        sql = mysql.connector.connect(** mysqlconfig)
        cursor = sql.cursor()

        #check for removed roles and delete them
        for role in before.roles:
            if role.id not in after.roles:
                cursor.execute("DELETE FROM discordroles WHERE discorduser = %s AND discordrole = %s", (before.id, role.id))
        cursor.close()

        #check for added roles and insert them
        cursor = sql.cursor()
        for role in after.roles:
            if role.id not in before.roles:
                if role.id == rcrp_utility.getrcrpguild(): #check to see if role is @everyone, skip it if so
                    continue;
                cursor.execute("INSERT INTO discordroles (discorduser, discordrole) VALUES (%s, %s)", (before.id, role.id))
                sql.commit()

        cursor.close()
        sql.close()

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        sql = mysql.connector.connect(** mysqlconfig)
        cursor = sql.cursor()
        cursor.execute("DELETE FROM discordroles WHERE discorduser = %s", (user.id, ))
        cursor.execute("UPDATE masters SET discordid = 0 WHERE discordid = %s", (user.id, ))
        cursor.close()
        sql.close()

async def SyncMemberRoles(self):
    while 1:
        discordguild = self.bot.get_guild(rcrp_utility.getrcrpguild())
        sql = mysql.connector.connect(** mysqlconfig)
        for member in self.bot.get_all_members():
            if not rcrp_utility.isverified(member):
                continue

            cursor = sql.cursor(dictionary = True)
            cursor.execute("SELECT id, Helper, Tester, AdminLevel, Premium FROM masters WHERE discordid = %s", (member.id, ))
            data = cursor.fetchone()
            cursor.close()

            if data is None:
                continue

            if rcrp_utility.ismanagement(member):
                continue

            banned = False
            if rcrp_utility.isbanned(data['id']):
                banned = True

            #remove roles a member shouldn't have
            removeroles = []
            if rcrp_utility.helperrole() in [role.id for role in member.roles] and data['Helper'] == 0: #member isn't a helper but has the role
                removeroles.append(discordguild.get_role(rcrp_utility.helperrole()))
            if rcrp_utility.testerrole() in [role.id for role in member.roles] and data['Tester'] == 0: #member isn't a tester but has the role
                removeroles.append(discordguild.get_role(rcrp_utility.testerrole()))
            if rcrp_utility.adminrole() in [role.id for role in member.roles] and data['AdminLevel'] == 0: #member isn't an admin but has the role
                removeroles.append(discordguild.get_role(rcrp_utility.adminrole()))
            if rcrp_utility.premiumrole() in [role.id for role in member.roles] and data['Premium'] == 0: #member isn't an admin but has the role
                removeroles.append(discordguild.get_role(rcrp_utility.premiumrole()))
            if rcrp_utility.bannedrole() in [role.id for role in member.roles] and banned is False: #member isn't banned but has the role
                removeroles.append(discordguild.get_role(rcrp_utility.bannedrole()))
            if removeroles:
                await member.remove_roles(*removeroles)

            #add roles a member should have
            addroles = []
            if rcrp_utility.helperrole() not in [role.id for role in member.roles] and data['Helper'] == 1: #member is a helper but doesn't have the role
                addroles.append(discordguild.get_role(rcrp_utility.helperrole()))
            if rcrp_utility.testerrole() not in [role.id for role in member.roles] and data['Tester'] == 1: #member is a tester but doesn't have the role
                addroles.append(discordguild.get_role(rcrp_utility.testerrole()))
            if rcrp_utility.adminrole() not in [role.id for role in member.roles] and data['AdminLevel'] != 0: #member is an admin but doesn't have the role
                addroles.append(discordguild.get_role(rcrp_utility.adminrole()))
            if rcrp_utility.premiumrole() not in [role.id for role in member.roles] and data['Premium'] != 0: #member is an admin but doesn't have the role
                addroles.append(discordguild.get_role(rcrp_utility.premiumrole()))
            if rcrp_utility.bannedrole() not in [role.id for role in member.roles] and banned is True: #member isn't banned but has the role
                addroles.append(discordguild.get_role(rcrp_utility.bannedrole()))
            if addroles:
                await member.add_roles(*addroles)
        sql.close()
        await asyncio.sleep(60) #check every minute

def setup(bot):
    bot.add_cog(RoleSyncCog(bot))