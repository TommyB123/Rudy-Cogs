import discord
import mysql.connector
from discord.ext import commands
from cogs.utility import *
from cogs.mysqlinfo import mysqlconfig

class VerificationCog(commands.Cog, name="RCRP Verification"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden = True)
    @commands.dm_only()
    async def verify(self, ctx, masteraccount:str = None):
        if masteraccount is None:
            await ctx.send("Usage: !verify [Master account name]")
            return

        if rcrp_utility.IsDiscordIDLinked(ctx.author.id):
            await ctx.send("This Discord account is already linked to an RCRP account.")
            return

        if rcrp_utility.isValidMasterAccountName(masteraccount) == False:
            await ctx.send("Invalid account name.")
            return

        if rcrp_utility.IsAcceptedMasterAccount(masteraccount) == False:
            await ctx.send("You cannot verify your Master Account if you have not been accepted into the server.\nIf you're looking for help with the registration process, visit our forums at https://forum.redcountyrp.com")
            return

        code = rcrp_utility.random_with_N_digits(10)
        sql = mysql.connector.connect(** mysqlconfig)
        cursor = sql.cursor()
        cursor.execute("UPDATE masters SET discordcode = %s, pendingdiscordid = %s WHERE Username = %s AND discordid = 0", (str(code), ctx.author.id, masteraccount))
        cursor.close()
        sql.close()

        await ctx.send(f"Your verification code has been set! Log in on our website and look for 'Discord Verification Code' at your dashboard page. ({dashboardurl})\nOnce you have found your verification code, send '!validate [code]' to confirm your account.")

    @commands.command(hidden = True)
    @commands.dm_only()
    async def validate(self, ctx, code:int = -1):
        if code == -1:
            await ctx.send("Usage: !validate [code]")

        sql = mysql.connector.connect(** mysqlconfig)
        cursor = sql.cursor()
        cursor.execute("SELECT COUNT(*), id, Helper, Tester, AdminLevel AS results FROM masters WHERE discordcode = %s AND pendingdiscordid = %s", (code, ctx.author.id))
        data = cursor.fetchone()
        cursor.close()

        if data[0] == 0: #account doesn't match
            await ct.send("Invalid verification code.")
            return

        discordguild = self.bot.get_guild(rcrpguild)
        discordmember = discordguild.get_member(ctx.author.id)
        discordroles = []
        discordroles.append(discordguild.get_role(verifiedrole))
        if data[2] == 1: #guy is helper
            discordroles.append(discordguild.get_role(helperrole))
        if data[3] == 1: #guy is tester
            discordroles.append(discordguild.get_role(testerrole))
        if data[4] != 0: #guy is admin
            discordroles.append(discordguild.get_role(adminrole))
        if data[4] == 4: #guy is management
            discordroles.append(discordguild.get_role(managementrole))
        await discordmember.add_roles(*discordroles)

        cursor = sql.cursor()
        cursor.execute("UPDATE masters SET discordid = %s, discordcode = 0, pendingdiscordid = 0 WHERE id = %s", (ctx.author.id, data[1]))
        cursor.close()
        sql.close()

        await ctx.send("Your account is now verified!")

def setup(bot):
    bot.add_cog(VerificationCog(bot))