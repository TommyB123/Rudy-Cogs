import discord
import aiomysql
from discord.ext import commands
from cogs.utility import *
from cogs.mysqlinfo import mysqlconfig

class VerificationCog(commands.Cog, name="RCRP Verification"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.dm_only()
    async def verify(self, ctx, masteraccount:str = None):
        if masteraccount is None:
            await ctx.send("Usage: !verify [Master account name]")
            return

        linked = await rcrp_utility.IsDiscordIDLinked(ctx.author.id)
        if linked == True:
            await ctx.send("This Discord account is already linked to an RCRP account.")
            return

        validname = await rcrp_utility.isValidMasterAccountName(masteraccount)
        if validname == False:
            await ctx.send("Invalid account name.")
            return

        acceptedma = await rcrp_utility.IsAcceptedMasterAccount(masteraccount)
        if acceptedma == False:
            await ctx.send("You cannot verify your Master Account if you have not been accepted into the server.\nIf you're looking for help with the registration process, visit our forums at https://forum.redcountyrp.com")
            return

        code = rcrp_utility.random_with_N_digits(10)
        sql = await aiomysql.connect(** mysqlconfig)
        cursor = await sql.cursor()
        await cursor.execute("UPDATE masters SET discordcode = %s, pendingdiscordid = %s WHERE Username = %s AND discordid = 0", (str(code), ctx.author.id, masteraccount))
        await cursor.close()
        sql.close()

        await ctx.send(f"Your verification code has been set! Log in on our website and look for 'Discord Verification Code' at your dashboard page. ({dashboardurl})\nOnce you have found your verification code, send '!validate [code]' to confirm your account.")

    @commands.command()
    @commands.dm_only()
    async def validate(self, ctx, code:int = None):
        if code == None:
            await ctx.send("Usage: !validate [code]")

        sql = await aiomysql.connect(** mysqlconfig)
        cursor = await sql.cursor(aiomysql.DictCursor)
        await cursor.execute("SELECT COUNT(*) AS matches, id, Helper, Tester, AdminLevel FROM masters WHERE discordcode = %s AND pendingdiscordid = %s", (code, ctx.author.id))
        data = await cursor.fetchone()
        await cursor.close()

        if data['matches'] == 0: #account doesn't match
            await ct.send("Invalid verification code.")
            return

        discordguild = self.bot.get_guild(rcrpguild)
        discordmember = discordguild.get_member(ctx.author.id)
        discordroles = []
        discordroles.append(discordguild.get_role(verifiedrole))
        if data['Helper'] == 1: #guy is helper
            discordroles.append(discordguild.get_role(helperrole))
        if data['Tester'] == 1: #guy is tester
            discordroles.append(discordguild.get_role(testerrole))
        if data['AdminLevel'] != 0: #guy is admin
            discordroles.append(discordguild.get_role(adminrole))
        if data['AdminLevel'] == 4: #guy is management
            discordroles.append(discordguild.get_role(managementrole))
        await discordmember.add_roles(*discordroles)

        cursor = await sql.cursor()
        await cursor.execute("UPDATE masters SET discordid = %s, discordcode = 0, pendingdiscordid = 0 WHERE id = %s", (ctx.author.id, data['id']))
        await cursor.close()
        sql.close()

        await ctx.send("Your account is now verified!")

    @commands.command()
    @commands.guild_only()
    @commands.check(rcrp_utility.is_management)
    async def manualverify(self, ctx, member: discord.Member = None, masteraccount: str = " "):
        if not member:
            await ctx.send("Invalid user.")
            return

        if rcrp_utility.isverified(member) == True:
            await ctx.send(f"{member.mention} is already verified.")
            return

        if rcrp_utility.isValidMasterAccountName(masteraccount) == False:
            await ctx.send("Invalid MA name")
            return

        if rcrp_utility.isMasterAccountVerified(masteraccount) == True:
            await ctx.send("MA is already verified")
            return

        sql = await aiomysql.connect(** mysqlconfig)
        cursor = await sql.cursor()
        await cursor.execute("UPDATE masters SET discordid = %s, discordcode = 0 WHERE Username = %s", (member.id, masteraccount))
        await cursor.close()
        sql.close()

        await member.add_roles(ctx.guild.get_role(verifiedrole))
        await ctx.send(f"{member.mention} has been manually verified as {masteraccount}")

    @commands.command()
    @commands.guild_only()
    @commands.check(rcrp_utility.is_management)
    async def unverify(self, ctx, member: discord.Member = None):
        if not member:
            await ctx.send("Invalid user.")
            return

        if not rcrp_utility.isverified(member):
            await ctx.send("This user is not verified")
            return

        sql = await aiomysql.connect(** mysqlconfig)
        cursor = await sql.cursor()
        await cursor.execute("DELETE FROM discordroles WHERE discorduser = %s", (member.id, ))
        await cursor.execute("UPDATE masters SET discordid = 0 WHERE discordid = %s", (member.id, ))
        await cursor.close()
        sql.close()

        roles = []
        for role in member.roles:
            if role.id == rcrpguild: #check to see if the role is @everyone, skip it if so
                continue
            roles.append(role)

        await ctx.send(f"{member.mention} has been unverified.")
        await member.remove_roles(*roles)

    @commands.command()
    @commands.guild_only()
    @commands.check(rcrp_utility.is_management)
    async def softunverify(self, ctx, discordid:int = None):
        if discordid == None:
            await ctx.send('Usage: !softunverify [discord ID]')
            return

        sql = await aiomysql.connect(** mysqlconfig)
        cursor = await sql.cursor()
        await cursor.execute("UPDATE masters SET discordid = 0 WHERE discordid = %s", (discordid))

        if cursor.rowcount != 0:
            await ctx.send(f"Discord ID {discordid} has been unlinked from its MA.")
        else:
            await ctx.send(f"There are no accounts linked to Discord ID {discordid}")

        await cursor.close()
        sql.close()


def setup(bot):
    bot.add_cog(VerificationCog(bot))